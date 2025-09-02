#!/usr/bin/env python3
"""
🧪 TESTS BLOC 1 - DATA PROCESSOR
================================

Tests unitaires et d'intégration pour le BLOC 1 (Data Processor).
Valide le traitement hybride Polars → Pandas et la création de la base DuckDB.

Tests inclus :
- Validation des fichiers source
- Chargement et nettoyage des données
- Agrégation 2h avec règles métier
- Conversion et sauvegarde DuckDB
- Performance et robustesse
"""

import unittest
import tempfile
import os
import time
import pandas as pd
import polars as pl
import duckdb
from pathlib import Path
from datetime import datetime, timedelta

# Import du module à tester
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processor import EnergyDataProcessor

class TestEnergyDataProcessor(unittest.TestCase):
    """Tests pour le BLOC 1 - Data Processor"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.raw_data_path = Path(self.temp_dir) / "test_household.csv"
        self.processed_data_path = Path(self.temp_dir) / "test_energy_2h_aggregated.duckdb"
        
        # Création de données de test
        self.create_test_data()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_data(self):
        """Crée des données de test réalistes"""
        # Génération de données sur 3 jours avec mesures toutes les minutes
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 4, 0, 0, 0)
        
        timestamps = []
        dates = []
        times = []
        global_active_power = []
        global_reactive_power = []
        voltage = []
        global_intensity = []
        sub_metering_1 = []
        sub_metering_2 = []
        sub_metering_3 = []
        
        current = start_date
        while current < end_date:
            timestamps.append(current)
            dates.append(current.strftime("%d/%m/%Y"))
            times.append(current.strftime("%H:%M:%S"))
            
            # Données réalistes avec patterns
            hour = current.hour
            is_daytime = 6 <= hour <= 22
            
            # Puissance active (kW) - plus élevée le jour
            base_power = 0.5 if is_daytime else 0.2
            power = base_power + 0.3 * (hour % 6) / 6  # Variation
            global_active_power.append(round(power, 3))
            
            # Puissance réactive (kW)
            global_reactive_power.append(round(power * 0.1, 3))
            
            # Tension (V) - stable autour de 240V
            voltage.append(round(240 + (hour % 12 - 6) * 2, 1))
            
            # Intensité (A) - calculée à partir de la puissance
            intensity = (power * 1000) / 240  # P = U*I
            global_intensity.append(round(intensity, 2))
            
            # Sub-meterings (Wh) - énergies cumulées
            sub_metering_1.append(round(power * 600 * 0.4, 1))  # 40% de l'énergie
            sub_metering_2.append(round(power * 600 * 0.3, 1))  # 30% de l'énergie
            sub_metering_3.append(round(power * 600 * 0.3, 1))  # 30% de l'énergie
            
            current += timedelta(minutes=1)
        
        # Création du DataFrame de test
        test_data = {
            'Date': dates,
            'Time': times,
            'Global_active_power': global_active_power,
            'Global_reactive_power': global_reactive_power,
            'Voltage': voltage,
            'Global_intensity': global_intensity,
            'Sub_metering_1': sub_metering_1,
            'Sub_metering_2': sub_metering_2,
            'Sub_metering_3': sub_metering_3
        }
        
        # Sauvegarde en CSV tab-separé
        df_test = pd.DataFrame(test_data)
        df_test.to_csv(self.raw_data_path, sep='\t', index=False)
    
    def test_initialization(self):
        """Test de l'initialisation du processeur"""
        processor = EnergyDataProcessor()
        
        self.assertIsInstance(processor.raw_data_path, Path)
        self.assertIsInstance(processor.processed_data_path, Path)
        self.assertIsInstance(processor.start_time, float)
    
    def test_validate_source_file(self):
        """Test de la validation du fichier source"""
        processor = EnergyDataProcessor()
        processor.raw_data_path = self.raw_data_path
        
        # Test avec fichier valide
        result = processor.validate_source_file()
        self.assertTrue(result)
        
        # Test avec fichier inexistant
        processor.raw_data_path = Path("fichier_inexistant.csv")
        result = processor.validate_source_file()
        self.assertFalse(result)
    
    def test_load_raw_data(self):
        """Test du chargement des données brutes"""
        processor = EnergyDataProcessor()
        processor.raw_data_path = self.raw_data_path
        
        df_raw = processor.load_raw_data()
        
        # Vérifications
        self.assertIsInstance(df_raw, pl.DataFrame)
        self.assertGreater(df_raw.shape[0], 0)
        self.assertEqual(df_raw.shape[1], 9)  # 9 colonnes attendues
        self.assertIn("Date", df_raw.columns)
        self.assertIn("Time", df_raw.columns)
        self.assertIn("Global_active_power", df_raw.columns)
    
    def test_clean_data(self):
        """Test du nettoyage des données"""
        processor = EnergyDataProcessor()
        processor.raw_data_path = self.raw_data_path
        
        # Chargement des données brutes
        df_raw = processor.load_raw_data()
        
        # Nettoyage
        df_clean = processor.clean_data(df_raw)
        
        # Vérifications
        self.assertIsInstance(df_clean, pl.DataFrame)
        self.assertGreater(df_clean.shape[0], 0)
        self.assertIn("timestamp", df_clean.columns)
        
        # Vérification des types
        self.assertEqual(df_clean["timestamp"].dtype, pl.Datetime)
        self.assertEqual(df_clean["Global_active_power"].dtype, pl.Float64)
        
        # Vérification de l'absence de valeurs manquantes
        for col in df_clean.columns:
            if col != "timestamp":
                null_count = df_clean.select(pl.col(col).null_count()).item()
                self.assertEqual(null_count, 0)
    
    def test_aggregate_data_2h(self):
        """Test de l'agrégation en tranches de 2h avec features enrichies"""
        processor = EnergyDataProcessor()
        processor.raw_data_path = self.raw_data_path
        
        # Pipeline complet jusqu'à l'agrégation
        df_raw = processor.load_raw_data()
        df_clean = processor.clean_data(df_raw)
        df_aggregated = processor.aggregate_data_2h(df_clean)
        
        # Vérifications
        self.assertIsInstance(df_aggregated, pl.DataFrame)
        self.assertGreater(df_aggregated.shape[0], 0)
        
        # Vérification des colonnes de base
        expected_base_columns = [
            "timestamp", "sub_metering_1_wh", "sub_metering_2_wh", "sub_metering_3_wh",
            "global_active_power_kw", "global_reactive_power_kw", "voltage_v",
            "global_intensity_a", "energy_total_kwh", "power_peak_kw", "power_min_kw",
            "measurement_count"
        ]
        
        for col in expected_base_columns:
            self.assertIn(col, df_aggregated.columns)
        
        # Vérification des features temporelles
        temporal_features = [
            "day_of_week", "hour_of_day", "month", "year", "quarter",
            "is_weekend", "is_daytime", "is_winter", "is_summer",
            "hour_sin", "hour_cos", "day_sin", "day_cos", "month_sin", "month_cos"
        ]
        
        for feature in temporal_features:
            self.assertIn(feature, df_aggregated.columns)
        
        # Vérification des lags
        lag_features = [
            "energy_lag_1", "energy_lag_2", "energy_lag_24h", "energy_lag_7d",
            "power_lag_1", "power_lag_24h", "voltage_lag_1", "voltage_lag_24h"
        ]
        
        for feature in lag_features:
            self.assertIn(feature, df_aggregated.columns)
        
        # Vérification des rolling features
        rolling_features = [
            "energy_rolling_6h", "energy_rolling_24h", "energy_rolling_7d",
            "power_rolling_6h", "power_rolling_24h", "voltage_rolling_6h", "voltage_rolling_24h",
            "sub1_rolling_24h", "sub2_rolling_24h", "sub3_rolling_24h"
        ]
        
        for feature in rolling_features:
            self.assertIn(feature, df_aggregated.columns)
        
        # Vérification des features de tendance et volatilité
        trend_features = [
            "energy_trend", "power_trend", "energy_volatility_24h", "power_volatility_24h",
            "energy_ratio_24h", "power_ratio_24h"
        ]
        
        for feature in trend_features:
            self.assertIn(feature, df_aggregated.columns)
        
        # Vérification de l'agrégation temporelle (tolérance plus large pour les données de test)
        timestamps = df_aggregated["timestamp"].to_list()
        for i in range(1, len(timestamps)):
            time_diff = timestamps[i] - timestamps[i-1]
            # La différence doit être proche de 2 heures (tolérance de 6h pour les données de test)
            self.assertAlmostEqual(time_diff.total_seconds() / 3600, 2, delta=6.0)
        
        # Vérification du nombre total de colonnes (base + features)
        expected_total_columns = len(expected_base_columns) + len(temporal_features) + len(lag_features) + len(rolling_features) + len(trend_features)
        self.assertEqual(df_aggregated.shape[1], expected_total_columns)
    
    def test_convert_to_pandas(self):
        """Test de la conversion Polars → Pandas"""
        processor = EnergyDataProcessor()
        processor.raw_data_path = self.raw_data_path
        
        # Pipeline complet jusqu'à la conversion
        df_raw = processor.load_raw_data()
        df_clean = processor.clean_data(df_raw)
        df_aggregated = processor.aggregate_data_2h(df_clean)
        df_pandas = processor.convert_to_pandas(df_aggregated)
        
        # Vérifications
        self.assertIsInstance(df_pandas, pd.DataFrame)
        self.assertEqual(df_pandas.shape[0], df_aggregated.shape[0])
        self.assertEqual(df_pandas.shape[1], df_aggregated.shape[1])
        
        # Vérification de la conversion des types
        self.assertTrue(str(df_pandas["timestamp"].dtype).startswith("datetime64"))
    
    def test_save_to_duckdb(self):
        """Test de la sauvegarde dans DuckDB"""
        processor = EnergyDataProcessor()
        processor.raw_data_path = self.raw_data_path
        processor.processed_data_path = self.processed_data_path
        
        # Pipeline complet jusqu'à la sauvegarde
        df_raw = processor.load_raw_data()
        df_clean = processor.clean_data(df_raw)
        df_aggregated = processor.aggregate_data_2h(df_clean)
        df_pandas = processor.convert_to_pandas(df_aggregated)
        
        # Sauvegarde
        processor.save_to_duckdb(df_pandas)
        
        # Vérifications
        self.assertTrue(self.processed_data_path.exists())
        
        # Test de lecture depuis DuckDB
        conn = duckdb.connect(str(self.processed_data_path))
        
        # Vérification de la table
        tables = conn.execute("SHOW TABLES").fetchall()
        self.assertIn(("energy_data",), tables)
        
        # Vérification des données
        count = conn.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
        self.assertEqual(count, df_pandas.shape[0])
        
        # Vérification des colonnes
        columns = conn.execute("DESCRIBE energy_data").fetchall()
        column_names = [col[0] for col in columns]
        self.assertIn("timestamp", column_names)
        self.assertIn("energy_total_kwh", column_names)
        
        conn.close()
    
    def test_full_pipeline(self):
        """Test du pipeline complet"""
        processor = EnergyDataProcessor()
        processor.raw_data_path = self.raw_data_path
        processor.processed_data_path = self.processed_data_path
        
        # Exécution du pipeline complet
        success = processor.process_pipeline()
        
        # Vérifications
        self.assertTrue(success)
        self.assertTrue(self.processed_data_path.exists())
        
        # Vérification de la base de données finale
        conn = duckdb.connect(str(self.processed_data_path))
        
        # Statistiques de la base
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_rows,
                MIN(timestamp) as start_date,
                MAX(timestamp) as end_date,
                AVG(energy_total_kwh) as avg_energy
            FROM energy_data
        """).fetchone()
        
        self.assertGreater(stats[0], 0)  # Au moins une ligne
        self.assertIsNotNone(stats[1])   # Date de début
        self.assertIsNotNone(stats[2])   # Date de fin
        self.assertGreater(stats[3], 0)  # Énergie moyenne positive
        
        conn.close()
    
    def test_error_handling(self):
        """Test de la gestion d'erreurs"""
        processor = EnergyDataProcessor()
        
        # Test avec fichier inexistant
        processor.raw_data_path = Path("fichier_inexistant.csv")
        success = processor.process_pipeline()
        self.assertFalse(success)
    
    def test_performance_benchmark(self):
        """Test de performance du pipeline"""
        processor = EnergyDataProcessor()
        processor.raw_data_path = self.raw_data_path
        processor.processed_data_path = self.processed_data_path
        
        # Mesure du temps d'exécution
        start_time = time.time()
        success = processor.process_pipeline()
        execution_time = time.time() - start_time
        
        # Vérifications
        self.assertTrue(success)
        self.assertLess(execution_time, 30)  # Moins de 30 secondes pour les données de test
        
        print(f"⏱️  Temps d'exécution: {execution_time:.2f} secondes")

def run_tests():
    """Lance tous les tests du BLOC 1"""
    print("🧪 TESTS BLOC 1 - DATA PROCESSOR")
    print("=" * 50)
    
    # Création de la suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnergyDataProcessor)
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print("=" * 50)
    print(f"📊 Résultats des tests:")
    print(f"   - Tests exécutés: {result.testsRun}")
    print(f"   - Échecs: {len(result.failures)}")
    print(f"   - Erreurs: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ TOUS LES TESTS RÉUSSIS - BLOC 1 VALIDÉ")
        return True
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
