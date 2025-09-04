#!/usr/bin/env python3
"""
💾 GAP UPDATER - Mise à jour DuckDB avec données générées
=======================================================

Met à jour la base DuckDB avec les nouvelles données générées.
Inclut backup automatique et validation des données.

Auteur : Energy Agent Project
"""

import duckdb
import pandas as pd
import shutil
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List
import sys
import os

# Ajouter le chemin pour importer le processeur
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GapUpdater:
    """Mise à jour de la base DuckDB avec les données générées"""
    
    def __init__(self, db_path: str = "data_genere/processed/energy_fictional_2h.duckdb"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Chemin de backup
        self.backup_dir = Path("data_genere/backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> str:
        """
        Crée une sauvegarde de la base avant mise à jour
        
        Returns:
            Chemin du fichier de backup
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"energy_fictional_2h_backup_{timestamp}.duckdb"
            backup_path = self.backup_dir / backup_filename
            
            # Copier la base
            shutil.copy2(self.db_path, backup_path)
            
            self.logger.info(f"Backup créé: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Erreur création backup: {e}")
            raise
    
    def process_generated_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Traite les données générées pour les préparer à l'insertion
        (Utilise la même logique que data_processor_fictional.py)
        
        Args:
            df: DataFrame brut généré
            
        Returns:
            DataFrame traité prêt pour insertion
        """
        if df.empty:
            return df
        
        # Copie pour éviter les modifications
        df_processed = df.copy()
        
        # Créer la colonne timestamp
        df_processed['timestamp'] = pd.to_datetime(
            df_processed['Date'] + ' ' + df_processed['Time'], 
            format='%d/%m/%Y %H:%M:%S'
        )
        
        # Calculs énergétiques (énergie = puissance × 2h)
        df_processed['energy_total_kwh'] = df_processed['Global_active_power'] * 2
        
        # Renommer les sous-compteurs
        df_processed['sub_metering_1_kwh'] = df_processed['Sub_metering_1']
        df_processed['sub_metering_2_kwh'] = df_processed['Sub_metering_2'] 
        df_processed['sub_metering_3_kwh'] = df_processed['Sub_metering_3']
        
        # Renommer les colonnes principales
        df_processed['global_active_power_kw'] = df_processed['Global_active_power']
        df_processed['global_reactive_power_kw'] = df_processed['Global_reactive_power']
        df_processed['voltage_v'] = df_processed['Voltage']
        df_processed['global_intensity_a'] = df_processed['Global_intensity']
        
        # Ajouter les colonnes supplémentaires
        df_processed['power_peak_kw'] = df_processed['global_active_power_kw']
        df_processed['power_min_kw'] = df_processed['global_active_power_kw']
        df_processed['measurement_count'] = 1
        
        # Sélectionner les colonnes finales (même ordre que la table existante)
        final_columns = [
            'Global_active_power', 'Global_reactive_power', 'Voltage', 'Global_intensity',
            'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3', 'timestamp',
            'energy_total_kwh', 'sub_metering_1_kwh', 'sub_metering_2_kwh', 'sub_metering_3_kwh',
            'global_active_power_kw', 'global_reactive_power_kw', 'voltage_v', 'global_intensity_a',
            'power_peak_kw', 'power_min_kw', 'measurement_count'
        ]
        
        return df_processed[final_columns]
    
    def insert_data(self, df_processed: pd.DataFrame) -> Dict:
        """
        Insère les données traitées dans DuckDB
        
        Args:
            df_processed: DataFrame traité
            
        Returns:
            Dict avec résultats de l'insertion
        """
        if df_processed.empty:
            return {'success': False, 'message': 'Aucune donnée à insérer'}
        
        try:
            # Connexion à la base
            conn = duckdb.connect(self.db_path)
            
            # Vérifier le nombre d'enregistrements avant
            count_before = conn.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
            
            # Insérer les nouvelles données
            conn.register('new_data', df_processed)
            
            insert_query = """
                INSERT INTO energy_data 
                SELECT * FROM new_data
                ORDER BY timestamp
            """
            
            conn.execute(insert_query)
            
            # Vérifier le nombre d'enregistrements après
            count_after = conn.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
            
            # Vérifier la nouvelle période
            period_result = conn.execute("""
                SELECT 
                    MIN(timestamp) as start_date,
                    MAX(timestamp) as end_date
                FROM energy_data
            """).fetchone()
            
            conn.close()
            
            inserted_count = count_after - count_before
            
            return {
                'success': True,
                'inserted_count': inserted_count,
                'total_count': count_after,
                'period_start': period_result[0],
                'period_end': period_result[1],
                'message': f'{inserted_count} enregistrements ajoutés avec succès'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur insertion données: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur lors de l\'insertion: {e}'
            }
    
    def update_database(self, df_generated: pd.DataFrame, create_backup: bool = True) -> Dict:
        """
        Met à jour la base de données complète
        
        Args:
            df_generated: DataFrame généré brut
            create_backup: Créer un backup avant mise à jour
            
        Returns:
            Dict avec le résultat complet de l'opération
        """
        try:
            start_time = datetime.now()
            
            # Backup si demandé
            backup_path = None
            if create_backup:
                backup_path = self.create_backup()
            
            # Traitement des données
            df_processed = self.process_generated_data(df_generated)
            
            if df_processed.empty:
                return {
                    'success': False,
                    'message': 'Aucune donnée à traiter',
                    'backup_path': backup_path
                }
            
            # Insertion
            insert_result = self.insert_data(df_processed)
            
            # Temps d'exécution
            duration = (datetime.now() - start_time).total_seconds()
            
            # Résultat complet
            result = {
                'success': insert_result['success'],
                'backup_path': backup_path,
                'duration': duration,
                'timestamp': datetime.now(),
                **insert_result
            }
            
            if result['success']:
                self.logger.info(f"Mise à jour réussie: {insert_result['inserted_count']} enregistrements en {duration:.2f}s")
            else:
                self.logger.error(f"Échec mise à jour: {insert_result.get('message', 'Erreur inconnue')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour base: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur critique: {e}',
                'backup_path': backup_path if 'backup_path' in locals() else None
            }
    
    def validate_database(self) -> Dict:
        """
        Valide l'intégrité de la base après mise à jour
        
        Returns:
            Dict avec le résultat de la validation
        """
        try:
            conn = duckdb.connect(self.db_path)
            
            # Vérifications de base
            total_count = conn.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
            
            # Vérifier la continuité temporelle
            continuity_check = conn.execute("""
                WITH time_diffs AS (
                    SELECT 
                        timestamp,
                        LAG(timestamp) OVER (ORDER BY timestamp) as prev_timestamp,
                        EXTRACT(EPOCH FROM timestamp - LAG(timestamp) OVER (ORDER BY timestamp))/3600 as hours_diff
                    FROM energy_data
                    ORDER BY timestamp
                )
                SELECT COUNT(*) as gaps
                FROM time_diffs 
                WHERE hours_diff > 2.1  -- Tolérance de 6 minutes
            """).fetchone()[0]
            
            # Période couverte
            period = conn.execute("""
                SELECT 
                    MIN(timestamp) as start_date,
                    MAX(timestamp) as end_date,
                    COUNT(DISTINCT DATE(timestamp)) as unique_days
                FROM energy_data
            """).fetchone()
            
            conn.close()
            
            return {
                'valid': True,
                'total_records': total_count,
                'temporal_gaps': continuity_check,
                'period_start': period[0],
                'period_end': period[1],
                'unique_days': period[2],
                'message': f'Base validée: {total_count} enregistrements, {continuity_check} gaps temporels'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur validation: {e}")
            return {
                'valid': False,
                'error': str(e),
                'message': f'Erreur validation: {e}'
            }

def main():
    """Test du updater"""
    print("💾 Test du updater")
    print("=" * 50)
    
    # Test avec données factices
    test_data = pd.DataFrame({
        'Date': ['01/09/2025', '01/09/2025'],
        'Time': ['00:00:00', '02:00:00'],
        'Global_active_power': [0.5, 0.6],
        'Global_reactive_power': [0.1, 0.12],
        'Voltage': [230, 231],
        'Global_intensity': [2.5, 3.0],
        'Sub_metering_1': [0.1, 0.12],
        'Sub_metering_2': [0.08, 0.10],
        'Sub_metering_3': [0.05, 0.06]
    })
    
    updater = GapUpdater()
    
    print("Test traitement données...")
    processed = updater.process_generated_data(test_data)
    print(f"Données traitées : {len(processed)} enregistrements")
    print("\nAperçu colonnes :")
    print(list(processed.columns))
    
    print("\nValidation base actuelle...")
    validation = updater.validate_database()
    print(f"Validation : {validation['message']}")

if __name__ == "__main__":
    main()








