#!/usr/bin/env python3
"""
🔧 GAP GENERATOR - Génération de données manquantes
=================================================

Génère les données énergétiques manquantes en continuité avec les données existantes.
Utilise le même algorithme que le générateur principal avec adaptation pour la continuité.

Auteur : Energy Agent Project
"""

import numpy as np
import pandas as pd
import duckdb
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import sys
import os

# Ajouter le chemin pour importer le générateur principal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GapGenerator:
    """Générateur de données pour combler les gaps"""
    
    def __init__(self, db_path: str = "../data_genere/processed/energy_fictional_2h.duckdb"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Paramètres identiques au générateur principal
        self.TARGET_DAILY_KWH = 12.0
        self.VOLTAGE_NOMINAL = 231.0
        self.VOLTAGE_MIN = 225.0
        self.VOLTAGE_MAX = 240.0
        self.PF_MIN = 0.94
        self.PF_MAX = 0.99
        
        # Facteur de multiplication pour atteindre la cible
        self.POWER_MULTIPLIER = 1.25
        
        # Coefficients saisonniers (identiques au générateur principal)
        self.SEASONAL_COEFFS = {
            1: 1.30,   # Janvier - pic hivernal
            2: 1.25,   # Février
            3: 1.15,   # Mars
            4: 1.05,   # Avril
            5: 0.95,   # Mai
            6: 0.90,   # Juin
            7: 0.85,   # Juillet
            8: 0.80,   # Août - minimum estival
            9: 0.85,   # Septembre
            10: 0.95,  # Octobre
            11: 1.10,  # Novembre
            12: 1.25   # Décembre
        }
    
    def get_last_values(self) -> Dict:
        """
        Récupère les dernières valeurs pour assurer la continuité
        
        Returns:
            Dict avec les dernières valeurs connues
        """
        try:
            conn = duckdb.connect(self.db_path)
            
            result = conn.execute("""
                SELECT 
                    timestamp,
                    energy_total_kwh,
                    global_active_power_kw,
                    voltage_v,
                    global_intensity_a,
                    sub_metering_1_kwh,
                    sub_metering_2_kwh,
                    sub_metering_3_kwh
                FROM energy_data 
                ORDER BY timestamp DESC 
                LIMIT 10
            """).fetchall()
            
            conn.close()
            
            if not result:
                return {}
            
            # Dernières valeurs pour continuité
            last = result[0]
            
            # Moyennes des 10 dernières valeurs pour stabilité
            recent_values = np.array([[row[i] for row in result] for i in range(1, len(last))])
            recent_means = np.mean(recent_values, axis=1)
            
            return {
                'last_timestamp': last[0],
                'last_power': last[2],  # global_active_power_kw
                'last_voltage': last[3],  # voltage_v
                'last_intensity': last[4],  # global_intensity_a
                'mean_sub1': recent_means[4],  # sub_metering_1_kwh moyenne
                'mean_sub2': recent_means[5],  # sub_metering_2_kwh moyenne
                'mean_sub3': recent_means[6],  # sub_metering_3_kwh moyenne
                'mean_power': recent_means[1],  # global_active_power_kw moyenne
                'mean_voltage': recent_means[2],  # voltage_v moyenne
            }
            
        except Exception as e:
            self.logger.error(f"Erreur récupération dernières valeurs: {e}")
            return {}
    
    def generate_gap_data(self, timestamps: List[datetime]) -> pd.DataFrame:
        """
        Génère les données pour les timestamps manquants
        
        Args:
            timestamps: Liste des timestamps à générer
            
        Returns:
            DataFrame avec les données générées
        """
        if not timestamps:
            return pd.DataFrame()
        
        # Récupérer les dernières valeurs pour continuité
        last_values = self.get_last_values()
        
        data = []
        
        for timestamp in timestamps:
            row = self._generate_single_record(timestamp, last_values)
            data.append(row)
        
        # Créer le DataFrame
        df = pd.DataFrame(data, columns=[
            'Date', 'Time', 'Global_active_power', 'Global_reactive_power',
            'Voltage', 'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3'
        ])
        
        return df
    
    def _generate_single_record(self, timestamp: datetime, last_values: Dict) -> List:
        """
        Génère un enregistrement unique
        
        Args:
            timestamp: Timestamp à générer
            last_values: Dernières valeurs pour continuité
            
        Returns:
            Liste des valeurs pour cet enregistrement
        """
        # Facteurs temporels (identiques au générateur principal)
        seasonal_factor = self.SEASONAL_COEFFS.get(timestamp.month, 1.0)
        
        # Profil journalier
        hour = timestamp.hour
        if 6 <= hour <= 8 or 18 <= hour <= 22:  # Pics matin/soir
            daily_factor = 1.4
        elif 12 <= hour <= 14:  # Pic midi
            daily_factor = 1.2
        elif 0 <= hour <= 6:  # Nuit
            daily_factor = 0.6
        else:  # Journée normale
            daily_factor = 1.0
        
        # Weekend
        if timestamp.weekday() >= 5:  # Samedi/Dimanche
            weekend_factor = 1.1
        else:
            weekend_factor = 1.0
        
        # Puissance de base avec continuité
        if last_values and 'mean_power' in last_values:
            base_power = last_values['mean_power'] * 0.8 + np.random.normal(0.5, 0.1) * 0.2
        else:
            base_power = np.random.normal(0.5, 0.1)
        
        # Application des facteurs
        target_power = (base_power * seasonal_factor * daily_factor * weekend_factor * self.POWER_MULTIPLIER)
        
        # Contraintes physiques
        target_power = max(0.05, min(target_power, 5.8))  # Entre 50W et 5.8kW
        
        # Tension avec continuité
        if last_values and 'mean_voltage' in last_values:
            voltage = last_values['mean_voltage'] + np.random.normal(0, 1.0)
        else:
            voltage = np.random.uniform(self.VOLTAGE_MIN, self.VOLTAGE_MAX)
        voltage = np.clip(voltage, self.VOLTAGE_MIN, self.VOLTAGE_MAX)
        
        # Facteur de puissance
        power_factor = np.random.uniform(self.PF_MIN, self.PF_MAX)
        
        # Puissance réactive
        reactive_power = target_power * np.tan(np.arccos(power_factor))
        
        # Intensité
        apparent_power = np.sqrt(target_power**2 + reactive_power**2)
        intensity = (apparent_power * 1000) / voltage
        intensity = min(intensity, 29.0)  # Limite contractuelle
        
        # Sous-compteurs avec continuité
        if last_values:
            sub1_base = last_values.get('mean_sub1', 0.2) * 2  # Cuisine
            sub2_base = last_values.get('mean_sub2', 0.15) * 2  # Buanderie  
            sub3_base = last_values.get('mean_sub3', 0.1) * 2   # ECS
        else:
            sub1_base = 0.2  # Cuisine
            sub2_base = 0.15  # Buanderie
            sub3_base = 0.1   # ECS
        
        # Variation des sous-compteurs
        energy_window = target_power * 2  # kWh sur 2h
        
        sub1_energy = max(0, np.random.normal(sub1_base, sub1_base * 0.3))
        sub2_energy = max(0, np.random.normal(sub2_base, sub2_base * 0.3))
        sub3_energy = max(0, np.random.normal(sub3_base, sub3_base * 0.3))
        
        # Assurer que les sous-compteurs ne dépassent pas le total
        total_sub = sub1_energy + sub2_energy + sub3_energy
        if total_sub > energy_window * 0.9:  # Laisser 10% pour "autres"
            factor = (energy_window * 0.9) / total_sub
            sub1_energy *= factor
            sub2_energy *= factor
            sub3_energy *= factor
        
        # Format de sortie (identique au générateur principal)
        return [
            timestamp.strftime('%d/%m/%Y'),  # Date
            timestamp.strftime('%H:%M:%S'),  # Time
            target_power,                    # Global_active_power (kW)
            reactive_power,                  # Global_reactive_power (kVAR)
            voltage,                         # Voltage (V)
            intensity,                       # Global_intensity (A)
            sub1_energy,                     # Sub_metering_1 (kWh)
            sub2_energy,                     # Sub_metering_2 (kWh)
            sub3_energy                      # Sub_metering_3 (kWh)
        ]

def main():
    """Test du générateur de gaps"""
    print("🔧 Test du générateur de gaps")
    print("=" * 50)
    
    # Test avec quelques timestamps
    test_timestamps = [
        datetime(2025, 9, 1, 0, 0),
        datetime(2025, 9, 1, 2, 0),
        datetime(2025, 9, 1, 4, 0),
    ]
    
    generator = GapGenerator()
    
    print("Génération de données test...")
    df = generator.generate_gap_data(test_timestamps)
    
    print(f"Données générées : {len(df)} enregistrements")
    print("\nAperçu :")
    print(df.head())
    
    # Test des dernières valeurs
    print("\nDernières valeurs en base :")
    last_values = generator.get_last_values()
    for key, value in last_values.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()








