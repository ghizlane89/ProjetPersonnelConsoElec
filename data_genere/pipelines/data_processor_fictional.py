#!/usr/bin/env python3
"""
Processeur de données énergétiques FICTIF - Optimisé pour données 2h
================================================================

Version optimisée pour le dataset fictif déjà agrégé en tranches de 2h.
Corrige les problèmes d'incompatibilité avec le processeur original.

PROBLÈMES CORRIGÉS :
- ❌ Agrégation inutile (données déjà 2h)
- ❌ Formule d'énergie minute par minute sur données 2h
- ❌ Sub_meters mal interprétés (Wh/minute vs kWh/2h)

SOLUTIONS :
- ✅ Traitement direct sans agrégation
- ✅ Formule d'énergie : Global_active_power × 2
- ✅ Sub_meters en kWh/2h (pas de conversion)
"""

import polars as pl
import pandas as pd
import duckdb
import time
import os
from datetime import datetime
from pathlib import Path


class FictionalEnergyDataProcessor:
    """Processeur optimisé pour données fictives déjà agrégées en 2h"""
    
    def __init__(self, raw_file: str = "data_genere/raw/household_fictional_2h.csv", 
                 output_file: str = "data_genere/processed/energy_fictional_2h.duckdb"):
        """
        Initialise le processeur fictif
        
        Args:
            raw_file: Chemin vers le fichier CSV fictif (déjà 2h)
            output_file: Chemin vers le fichier DuckDB de sortie
        """
        self.raw_file = raw_file
        self.output_file = output_file
        
        # Créer le répertoire de sortie si nécessaire
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 Processeur FICTIF initialisé:")
        print(f"   📁 Données fictives: {raw_file}")
        print(f"   📁 Sortie: {output_file}")
        print(f"   ⚡ Optimisé pour données déjà agrégées en 2h")
        print()
    
    def load_raw_data(self) -> pl.DataFrame:
        """Charge les données fictives depuis le fichier CSV"""
        print("📂 Chargement des données fictives...")
        
        start_time = time.time()
        
        try:
            # Vérifier l'existence du fichier
            if not os.path.exists(self.raw_file):
                raise FileNotFoundError(f"Fichier introuvable: {self.raw_file}")
            
            # Charger avec Polars
            df_raw = pl.read_csv(
                self.raw_file,
                separator="\t",
                try_parse_dates=False
            )
            
            load_time = time.time() - start_time
            print(f"✅ Données fictives chargées en {load_time:.2f}s")
            print(f"📊 Taille: {df_raw.shape[0]:,} lignes x {df_raw.shape[1]} colonnes")
            print()
            
            return df_raw
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            raise
    
    def clean_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Nettoyage simplifié pour données fictives déjà propres"""
        print("🧹 Nettoyage des données fictives...")
        
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
            
            # 2. Validation des contraintes physiques (données fictives déjà validées)
            print("   ✅ Validation des contraintes physiques...")
            df_validated = df_with_timestamp.filter(
                # Puissance active : 0-10 kW (contraintes réalistes)
                (pl.col("Global_active_power") >= 0) & (pl.col("Global_active_power") <= 10) &
                # Tension : 200-250V (contraintes physiques)
                (pl.col("Voltage") >= 200) & (pl.col("Voltage") <= 250) &
                # Intensité : 0-50A (contraintes physiques)
                (pl.col("Global_intensity") >= 0) & (pl.col("Global_intensity") <= 50) &
                # Cohérence physique : P <= U*I
                (pl.col("Global_active_power") <= pl.col("Voltage") * pl.col("Global_intensity") / 1000) &
                # Sub-meters positifs
                (pl.col("Sub_metering_1") >= 0) & (pl.col("Sub_metering_2") >= 0) & (pl.col("Sub_metering_3") >= 0)
            )
            
            # 3. Suppression des valeurs manquantes
            print("   🧽 Suppression des valeurs manquantes...")
            df_clean = df_validated.drop_nulls()
            
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
    
    def process_data_2h(self, df: pl.DataFrame) -> pl.DataFrame:
        """Traitement direct des données déjà agrégées en 2h (PAS d'agrégation)"""
        print("⏰ Traitement direct des données 2h (sans agrégation)...")
        
        start_time = time.time()
        
        try:
            # CORRECTION MAJEURE : Pas d'agrégation, traitement direct
            print("   ✅ Données déjà agrégées en 2h - pas d'agrégation nécessaire")
            
            # Calcul direct de l'énergie totale (CORRECTION DE LA FORMULE)
            df_processed = df.with_columns([
                # FORMULE CORRIGÉE pour données 2h :
                # Énergie totale = Puissance active × 2h (pas de formule minute par minute)
                (pl.col("Global_active_power") * 2).alias("energy_total_kwh"),
                
                # Sub-meters déjà en kWh/2h (pas de conversion)
                pl.col("Sub_metering_1").alias("sub_metering_1_kwh"),
                pl.col("Sub_metering_2").alias("sub_metering_2_kwh"),
                pl.col("Sub_metering_3").alias("sub_metering_3_kwh"),
                
                # Puissances (déjà en kW)
                pl.col("Global_active_power").alias("global_active_power_kw"),
                pl.col("Global_reactive_power").alias("global_reactive_power_kw"),
                
                # Grandeurs instantanées
                pl.col("Voltage").alias("voltage_v"),
                pl.col("Global_intensity").alias("global_intensity_a"),
                
                # Statistiques (même valeur car 1 mesure par tranche 2h)
                pl.col("Global_active_power").alias("power_peak_kw"),
                pl.col("Global_active_power").alias("power_min_kw"),
                pl.lit(1).alias("measurement_count")  # Toujours 1 pour données 2h
            ])
            
            # Tri par timestamp
            df_processed = df_processed.sort("timestamp")
            
            process_time = time.time() - start_time
            print(f"✅ Traitement direct terminé en {process_time:.2f}s")
            print(f"📊 Données traitées: {df_processed.shape[0]:,} lignes")
            print(f"📊 Période: {df_processed['timestamp'].min()} à {df_processed['timestamp'].max()}")
            print()
            
            return df_processed
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
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
        """Sauvegarde les données dans DuckDB"""
        print("💾 Sauvegarde dans DuckDB...")
        
        start_time = time.time()
        
        try:
            # Connexion DuckDB
            conn = duckdb.connect(self.output_file)
            
            # Sauvegarde des données
            conn.execute("DROP TABLE IF EXISTS energy_data")
            conn.execute("""
                CREATE TABLE energy_data AS 
                SELECT * FROM df
            """)
            
            # Vérification
            count = conn.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
            conn.close()
            
            save_time = time.time() - start_time
            print(f"✅ Sauvegarde terminée en {save_time:.2f}s")
            print(f"📊 Données sauvegardées: {count:,} lignes")
            print(f"📁 Fichier: {self.output_file}")
            print()
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            raise
    
    def run_pipeline(self) -> None:
        """Exécute le pipeline complet de traitement fictif"""
        print("🚀 DÉMARRAGE DU PIPELINE FICTIF")
        print("=" * 50)
        
        try:
            # 1. Chargement
            df_raw = self.load_raw_data()
            
            # 2. Nettoyage
            df_clean = self.clean_data(df_raw)
            
            # 3. Traitement direct (pas d'agrégation)
            df_processed = self.process_data_2h(df_clean)
            
            # 4. Conversion
            df_pandas = self.convert_to_pandas(df_processed)
            
            # 5. Sauvegarde
            self.save_to_duckdb(df_pandas)
            
            print("🎉 PIPELINE FICTIF TERMINÉ AVEC SUCCÈS")
            print("=" * 50)
            print(f"⏱️ Temps total: {time.time() - time.time():.2f}s")
            print(f"📊 Données finales: {len(df_pandas):,} lignes")
            print(f"📁 Fichier de sortie: {self.output_file}")
            print()
            print("✅ Traitement fictif terminé avec succès !")
            
        except Exception as e:
            print(f"❌ Erreur dans le pipeline fictif: {e}")
            raise


if __name__ == "__main__":
    # Exécution du pipeline fictif
    processor = FictionalEnergyDataProcessor()
    processor.run_pipeline()
