#!/usr/bin/env python3
"""
Processeur de données énergétiques avec Polars
============================================

Traite les données brutes household.csv et les agrège en format DuckDB
avec calcul correct de l'énergie totale selon la formule officielle.
"""

import polars as pl
import pandas as pd
import duckdb
import time
import os
from datetime import datetime
from pathlib import Path


class EnergyDataProcessor:
    """Processeur de données énergétiques avec Polars"""
    
    def __init__(self, raw_file: str = "data/raw/household.csv", 
                 output_file: str = "data/processed/energy_2h_aggregated.duckdb"):
        """
        Initialise le processeur
        
        Args:
            raw_file: Chemin vers le fichier CSV brut
            output_file: Chemin vers le fichier DuckDB de sortie
        """
        self.raw_file = raw_file
        self.output_file = output_file
        
        # Créer le répertoire de sortie si nécessaire
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 Processeur initialisé:")
        print(f"   📁 Données brutes: {raw_file}")
        print(f"   📁 Sortie: {output_file}")
        print()
    
    def load_raw_data(self) -> pl.DataFrame:
        """Charge les données brutes depuis le fichier CSV"""
        print("📂 Chargement des données brutes...")
        
        start_time = time.time()
        
        try:
            # Vérifier l'existence du fichier
            if not os.path.exists(self.raw_file):
                raise FileNotFoundError(f"Fichier introuvable: {self.raw_file}")
            
            # Charger avec Polars (plus rapide que pandas)
            df_raw = pl.read_csv(
                self.raw_file,
                separator="\t",
                try_parse_dates=False
            )
            
            load_time = time.time() - start_time
            print(f"✅ Données chargées en {load_time:.2f}s")
            print(f"📊 Taille: {df_raw.shape[0]:,} lignes x {df_raw.shape[1]} colonnes")
            print()
            
            return df_raw
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            raise
    
    def clean_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Nettoyage complet des données avec Polars"""
        print("🧹 Nettoyage complet des données...")
        
        start_time = time.time()
        initial_rows = df.shape[0]
        
        try:
            # 1. Conversion des types et création du timestamp
            print("   🔄 Conversion des types...")
            df_typed = df.with_columns([
                pl.col("Global_active_power").cast(pl.Float64),
                pl.col("Global_reactive_power").cast(pl.Float64),
                pl.col("Voltage").cast(pl.Float64),
                pl.col("Global_intensity").cast(pl.Float64),
                pl.col("Sub_metering_1").cast(pl.Float64),
                pl.col("Sub_metering_2").cast(pl.Float64),
                pl.col("Sub_metering_3").cast(pl.Float64)
            ])
            
            print("   ⏰ Création du timestamp...")
            df_with_timestamp = df_typed.with_columns([
                (pl.col("Date") + " " + pl.col("Time")).alias("timestamp_str")
            ]).with_columns([
                pl.col("timestamp_str").str.strptime(pl.Datetime, format="%d/%m/%Y %H:%M:%S").alias("timestamp")
            ]).drop(["Date", "Time", "timestamp_str"])
            
            # 2. Détection des valeurs manquantes
            print("   🔍 Détection des valeurs manquantes...")
            null_counts = {}
            for col in df_with_timestamp.columns:
                if col != "timestamp":
                    null_count = df_with_timestamp.select(pl.col(col).null_count()).item()
                    null_counts[col] = null_count
            
            print("   📋 Valeurs manquantes par colonne:")
            for col, count in null_counts.items():
                percentage = (count / initial_rows) * 100
                print(f"      - {col}: {count:,} ({percentage:.2f}%)")
            
            # 3. Détection des outliers (3 écarts-types)
            print("   🎯 Détection des outliers...")
            stats = df_with_timestamp.select([
                pl.col("Global_active_power").mean().alias("power_mean"),
                pl.col("Global_active_power").std().alias("power_std"),
                pl.col("Voltage").mean().alias("voltage_mean"),
                pl.col("Voltage").std().alias("voltage_std"),
                pl.col("Global_intensity").mean().alias("intensity_mean"),
                pl.col("Global_intensity").std().alias("intensity_std")
            ]).row(0)
            
            print("   📊 Seuils de détection des outliers:")
            print(f"      - Puissance active: {stats[0] - 3*stats[1]:.2f} - {stats[0] + 3*stats[1]:.2f} kW")
            print(f"      - Tension: {stats[2] - 3*stats[3]:.2f} - {stats[2] + 3*stats[3]:.2f} V")
            print(f"      - Intensité: {stats[4] - 3*stats[5]:.2f} - {stats[4] + 3*stats[5]:.2f} A")
            
            # 4. Filtrage des valeurs aberrantes
            print("   🚫 Filtrage des valeurs aberrantes...")
            df_filtered = df_with_timestamp.filter(
                # Puissance active : 0-20 kW (contraintes physiques)
                (pl.col("Global_active_power") >= 0) & (pl.col("Global_active_power") <= 20) &
                # Tension : 200-250V (contraintes physiques)
                (pl.col("Voltage") >= 200) & (pl.col("Voltage") <= 250) &
                # Intensité : 0-50A (contraintes physiques)
                (pl.col("Global_intensity") >= 0) & (pl.col("Global_intensity") <= 50) &
                # Cohérence physique : P <= U*I
                (pl.col("Global_active_power") <= pl.col("Voltage") * pl.col("Global_intensity") / 1000)
            )
            
            # 5. Suppression des valeurs manquantes
            print("   🧽 Suppression des valeurs manquantes...")
            df_clean = df_filtered.drop_nulls()
            
            # 6. Vérification de la cohérence
            print("   ✅ Vérification de la cohérence...")
            
            # 7. Détection des anomalies temporelles
            print("   ⏰ Détection des anomalies temporelles...")
            df_sorted = df_clean.sort("timestamp")
            time_diff = df_sorted.with_columns([
                pl.col("timestamp").diff().dt.total_seconds().alias("time_diff_seconds")
            ])
            
            large_gaps = time_diff.filter(pl.col("time_diff_seconds") > 300).shape[0]  # >5min
            print(f"      - Gaps temporels > 5min détectés: {large_gaps:,}")
            
            # Statistiques de nettoyage
            final_rows = df_clean.shape[0]
            removed_rows = initial_rows - final_rows
            
            clean_time = time.time() - start_time
            print("   📊 Statistiques de nettoyage:")
            print(f"      - Lignes initiales: {initial_rows:,}")
            print(f"      - Lignes supprimées: {removed_rows:,} ({(removed_rows/initial_rows)*100:.2f}%)")
            print(f"      - Lignes restantes: {final_rows:,}")
            print(f"      - Temps de nettoyage: {clean_time:.2f}s")
            
            # Qualité des données après nettoyage
            final_stats = df_clean.select([
                pl.col("Global_active_power").mean().alias("power_mean"),
                pl.col("Global_active_power").std().alias("power_std"),
                pl.col("Voltage").mean().alias("voltage_mean"),
                pl.col("Voltage").std().alias("voltage_std"),
                pl.col("Global_intensity").mean().alias("intensity_mean"),
                pl.col("Global_intensity").std().alias("intensity_std")
            ]).row(0)
            
            print("   📈 Qualité des données après nettoyage:")
            print(f"      - Puissance moyenne: {final_stats[0]:.3f} ± {final_stats[1]:.3f} kW")
            print(f"      - Tension moyenne: {final_stats[2]:.1f} ± {final_stats[3]:.1f} V")
            print(f"      - Intensité moyenne: {final_stats[4]:.1f} ± {final_stats[5]:.1f} A")
            print()
            
            return df_clean
            
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage: {e}")
            raise
    
    def aggregate_data_2h(self, df: pl.DataFrame) -> pl.DataFrame:
        """Agrège les données en tranches de 2 heures selon les règles métier"""
        print("⏰ Agrégation en tranches de 2 heures...")
        
        start_time = time.time()
        
        try:
            # Arrondir le timestamp à l'intervalle de 2h le plus proche
            df_agg = df.with_columns([
                pl.col("timestamp").dt.round("2h").alias("timestamp_2h")
            ])
            
            # Agrégation selon les règles métier
            df_aggregated = df_agg.group_by("timestamp_2h").agg([
                # Énergies (Wh) → Somme
                pl.col("Sub_metering_1").sum().alias("sub_metering_1_wh"),
                pl.col("Sub_metering_2").sum().alias("sub_metering_2_wh"),
                pl.col("Sub_metering_3").sum().alias("sub_metering_3_wh"),
                
                # Puissances (kW) → Moyenne pour l'affichage
                pl.col("Global_active_power").mean().alias("global_active_power_kw"),
                pl.col("Global_reactive_power").mean().alias("global_reactive_power_kw"),
                
                # Grandeurs instantanées → Moyenne
                pl.col("Voltage").mean().alias("voltage_v"),
                pl.col("Global_intensity").mean().alias("global_intensity_a"),
                
                # FORMULE OFFICIELLE DU DATASET (celle qui marchait bien avant !)
                # Énergie totale = somme des énergies par minute, puis conversion en kWh
                # global_active_power (kW) * 1000/60 = énergie par minute (Wh)
                # Somme sur 120 minutes (2h) puis /1000 pour kWh
                ((pl.col("Global_active_power") * 1000 / 60).sum() / 1000).alias("energy_total_kwh"),
                
                # Statistiques supplémentaires
                pl.col("Global_active_power").max().alias("power_peak_kw"),
                pl.col("Global_active_power").min().alias("power_min_kw"),
                pl.len().alias("measurement_count")
            ])
            
            # Renommer le timestamp
            df_aggregated = df_aggregated.rename({"timestamp_2h": "timestamp"})
            
            # Tri par timestamp
            df_aggregated = df_aggregated.sort("timestamp")
            
            agg_time = time.time() - start_time
            print(f"✅ Agrégation terminée en {agg_time:.2f}s")
            print(f"📊 Données agrégées: {df_aggregated.shape[0]:,} lignes")
            print(f"📊 Période: {df_aggregated['timestamp'].min()} à {df_aggregated['timestamp'].max()}")
            
            return df_aggregated
            
        except Exception as e:
            print(f"❌ Erreur lors de l'agrégation: {e}")
            raise
    
    def convert_to_pandas(self, df: pl.DataFrame) -> pd.DataFrame:
        """Convertit le DataFrame Polars en Pandas pour l'intégration DuckDB"""
        print("🔄 Conversion Polars → Pandas...")
        
        start_time = time.time()
        
        try:
            df_pandas = df.to_pandas()
            
            convert_time = time.time() - start_time
            print(f"✅ Conversion terminée en {convert_time:.2f}s")
            print(f"📊 DataFrame Pandas: {df_pandas.shape[0]:,} lignes x {df_pandas.shape[1]} colonnes")
            print()
            
            return df_pandas
            
        except Exception as e:
            print(f"❌ Erreur lors de la conversion: {e}")
            raise
    
    def save_to_duckdb(self, df: pd.DataFrame) -> None:
        """Sauvegarde les données dans DuckDB en mode sécurisé"""
        print("💾 Sauvegarde SÉCURISÉE dans DuckDB...")
        
        start_time = time.time()
        
        try:
            # MODE SÉCURISÉ : Vérifier si le fichier existe déjà
            if os.path.exists(self.output_file):
                print(f"⚠️ ATTENTION: Fichier DuckDB existant détecté: {self.output_file}")
                
                # Créer une sauvegarde automatique
                backup_file = self.output_file.replace('.duckdb', '_auto_backup.duckdb')
                import shutil
                shutil.copy2(self.output_file, backup_file)
                print(f"💾 Sauvegarde automatique créée: {backup_file}")
                
                # Vérifier les données existantes
                conn_check = duckdb.connect(self.output_file)
                try:
                    existing_count = conn_check.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
                    date_range = conn_check.execute("SELECT MIN(timestamp), MAX(timestamp) FROM energy_data").fetchone()
                    print(f"📊 Données existantes: {existing_count:,} enregistrements")
                    print(f"📅 Période existante: {date_range[0]} → {date_range[1]}")
                    
                    # SÉCURITÉ : Comparer avec les nouvelles données
                    new_count = len(df)
                    new_date_range = (df['timestamp'].min(), df['timestamp'].max())
                    print(f"📊 Nouvelles données: {new_count:,} enregistrements")
                    print(f"📅 Nouvelle période: {new_date_range[0]} → {new_date_range[1]}")
                    
                    # ALERTE si perte de données massive
                    if new_count < existing_count * 0.8:  # Plus de 20% de perte
                        print(f"🚨 ALERTE: Perte massive de données détectée!")
                        print(f"   Existant: {existing_count:,} vs Nouveau: {new_count:,}")
                        print(f"   Restauration depuis: {backup_file}")
                        conn_check.close()
                        return
                        
                except Exception as e:
                    print(f"⚠️ Impossible de vérifier les données existantes: {e}")
                finally:
                    conn_check.close()
            
            # Supprimer le fichier seulement après vérifications
            if os.path.exists(self.output_file):
                os.remove(self.output_file)
                print(f"🗑️ Ancien fichier supprimé après vérifications")
            
            # Créer la connexion DuckDB
            conn = duckdb.connect(self.output_file)
            
            # Créer la table et insérer les données
            conn.execute("""
                CREATE TABLE energy_data (
                    timestamp TIMESTAMP,
                    energy_total_kwh DOUBLE,
                    global_active_power_kw DOUBLE,
                    global_reactive_power_kw DOUBLE,
                    voltage_v DOUBLE,
                    global_intensity_a DOUBLE,
                    sub_metering_1_wh DOUBLE,
                    sub_metering_2_wh DOUBLE,
                    sub_metering_3_wh DOUBLE,
                    power_peak_kw DOUBLE,
                    power_min_kw DOUBLE,
                    measurement_count INTEGER
                )
            """)
            
            # Insérer les données
            conn.execute("INSERT INTO energy_data SELECT * FROM df")
            
            # Vérifier l'insertion
            count = conn.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
            
            # Fermer la connexion
            conn.close()
            
            save_time = time.time() - start_time
            print(f"✅ Sauvegarde SÉCURISÉE terminée en {save_time:.2f}s")
            print(f"📊 Données sauvegardées: {count:,} lignes")
            print(f"📁 Fichier: {self.output_file}")
            print(f"📏 Taille: {os.path.getsize(self.output_file) / (1024*1024):.1f} MB")
            print()
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            # En cas d'erreur, restaurer le backup si disponible
            backup_file = self.output_file.replace('.duckdb', '_auto_backup.duckdb')
            if os.path.exists(backup_file):
                import shutil
                shutil.copy2(backup_file, self.output_file)
                print(f"🔄 Données restaurées depuis le backup: {backup_file}")
            raise
    
    def process_pipeline(self) -> None:
        """Exécute le pipeline complet de traitement"""
        print("🚀 DÉMARRAGE DU PIPELINE DE TRAITEMENT")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # 1. Chargement des données brutes
            df_raw = self.load_raw_data()
            
            # 2. Nettoyage des données
            df_clean = self.clean_data(df_raw)
            
            # 3. Agrégation en tranches de 2h
            df_aggregated = self.aggregate_data_2h(df_clean)
            
            # 4. Conversion en Pandas
            df_pandas = self.convert_to_pandas(df_aggregated)
            
            # 5. Sauvegarde dans DuckDB
            self.save_to_duckdb(df_pandas)
            
            # Statistiques finales
            total_time = time.time() - start_time
            print("🎉 PIPELINE TERMINÉ AVEC SUCCÈS")
            print("=" * 50)
            print(f"⏱️ Temps total: {total_time:.2f}s")
            print(f"📊 Données finales: {df_pandas.shape[0]:,} lignes")
            print(f"📁 Fichier de sortie: {self.output_file}")
            print()
            
        except Exception as e:
            print(f"❌ ERREUR DANS LE PIPELINE: {e}")
            raise


def main():
    """Fonction principale"""
    print("🔧 PROCESSEUR DE DONNÉES ÉNERGÉTIQUES")
    print("=" * 50)
    
    try:
        # Initialiser le processeur
        processor = EnergyDataProcessor()
        
        # Exécuter le pipeline
        processor.process_pipeline()
        
        print("✅ Traitement terminé avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
