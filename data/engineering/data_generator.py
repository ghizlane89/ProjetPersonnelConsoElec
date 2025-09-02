#!/usr/bin/env python3
"""
Module de génération des données manquantes
Partie du bloc 1 - Data Engineering
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any
import random

class DataGenerator:
    """
    Générateur de données manquantes pour le bloc 1
    """
    
    def __init__(self):
        self.household_file = "data/raw/household.csv"
        self.backup_file = "data/raw/household_backup_before_generation.csv"
    
    def analyze_historical_patterns(self) -> Dict[str, Any]:
        """
        Analyse les patterns historiques pour générer des données réalistes
        """
        try:
            df = pd.read_csv(self.household_file, sep='\t')
            
            # Nettoyer les noms de colonnes (supprimer les espaces)
            df.columns = df.columns.str.strip()
            
            # Convertir en datetime
            df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H:%M:%S')
            
            # Patterns par heure de la journée
            hourly_patterns = df.groupby(df['datetime'].dt.hour).agg({
                'Global_active_power': ['mean', 'std'],
                'Global_reactive_power': ['mean', 'std'],
                'Voltage': ['mean', 'std'],
                'Global_intensity': ['mean', 'std'],
                'Sub_metering_1': ['mean', 'std'],
                'Sub_metering_2': ['mean', 'std'],
                'Sub_metering_3': ['mean', 'std']
            }).round(3)
            
            # Patterns par jour de la semaine
            weekly_patterns = df.groupby(df['datetime'].dt.dayofweek).agg({
                'Global_active_power': ['mean', 'std']
            }).round(3)
            
            return {
                "hourly": hourly_patterns.to_dict(),
                "weekly": weekly_patterns.to_dict(),
                "global_stats": {
                    "power_mean": df['Global_active_power'].mean(),
                    "power_std": df['Global_active_power'].std(),
                    "voltage_mean": df['Voltage'].mean(),
                    "voltage_std": df['Voltage'].std()
                }
            }
            
        except Exception as e:
            print(f"Erreur lors de l'analyse des patterns : {e}")
            return None
    
    def generate_realistic_values(self, timestamp: datetime, patterns: Dict[str, Any]) -> Dict[str, float]:
        """
        Génère des valeurs réalistes basées sur les patterns
        """
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Valeurs de base
        try:
            base_power = patterns["hourly"]["Global_active_power"]["mean"].get(hour, patterns["global_stats"]["power_mean"])
        except:
            base_power = patterns["global_stats"]["power_mean"]
        
        base_voltage = patterns["global_stats"]["voltage_mean"]
        
        # Ajouter du bruit réaliste
        noise_factor = random.uniform(-0.2, 0.2)
        seasonal_factor = 1.0 + 0.1 * np.sin(2 * np.pi * hour / 24)  # Variation saisonnière
        
        # Générer les valeurs
        power = max(0.1, base_power * (1 + noise_factor) * seasonal_factor)
        voltage = base_voltage + random.uniform(-2, 2)
        intensity = power * 4.2 + random.uniform(-0.5, 0.5)  # Relation approximative
        
        # Sub-meterings (basés sur les patterns)
        sub1 = random.uniform(0, 100) if random.random() > 0.7 else 0
        sub2 = random.uniform(0, 100) if random.random() > 0.5 else 0
        sub3 = random.uniform(0, 300) if random.random() > 0.3 else 0
        
        return {
            'Global_active_power': round(power, 3),
            'Global_reactive_power': round(power * 0.1 + random.uniform(-0.05, 0.05), 3),
            'Voltage': round(voltage, 3),
            'Global_intensity': round(intensity, 3),
            'Sub_metering_1': round(sub1, 3),
            'Sub_metering_2': round(sub2, 3),
            'Sub_metering_3': round(sub3, 3)
        }
    
    def generate_missing_data(self, gap_start: datetime, gap_end: datetime, progress_callback=None) -> Dict[str, Any]:
        """
        Génère les données manquantes pour la période spécifiée
        """
        try:
            # Sauvegarder le fichier original
            if os.path.exists(self.household_file):
                backup_df = pd.read_csv(self.household_file, sep='\t')
                backup_df.to_csv(self.backup_file, sep='\t', index=False)
                print(f"💾 Sauvegarde créée : {self.backup_file}")
            
            # Analyser les patterns
            patterns = self.analyze_historical_patterns()
            if not patterns:
                return {"success": False, "error": "Impossible d'analyser les patterns historiques"}
            
            # Générer les nouvelles données
            new_data = []
            current = gap_start
            total_minutes = int((gap_end - gap_start).total_seconds() / 60)
            processed_minutes = 0
            
            while current < gap_end:
                # Générer les valeurs pour cette minute
                values = self.generate_realistic_values(current, patterns)
                
                new_data.append({
                    'Date': current.strftime('%d/%m/%Y'),
                    'Time': current.strftime('%H:%M:%S'),
                    **values
                })
                
                # Mettre à jour la progression
                processed_minutes += 1
                if progress_callback and processed_minutes % 100 == 0:
                    progress = processed_minutes / total_minutes
                    progress_callback(progress)
                
                current += timedelta(minutes=1)
            
            # Créer le DataFrame des nouvelles données
            new_df = pd.DataFrame(new_data)
            
            # Lire le fichier existant
            existing_df = pd.read_csv(self.household_file, sep='\t')
            
            # Concaténer les données
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Sauvegarder le fichier mis à jour
            combined_df.to_csv(self.household_file, sep='\t', index=False)
            
            return {
                "success": True,
                "records_generated": len(new_data),
                "total_records": len(combined_df),
                "period": f"{gap_start} → {gap_end}",
                "backup_file": self.backup_file
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la génération : {str(e)}"}
    
    def validate_generated_data(self) -> bool:
        """
        Valide les données générées
        """
        try:
            df = pd.read_csv(self.household_file, sep='\t')
            
            # Nettoyer les noms de colonnes
            df.columns = df.columns.str.strip()
            
            # Vérifications de base
            checks = [
                len(df) > 0,
                'Date' in df.columns,
                'Time' in df.columns,
                'Global_active_power' in df.columns,
                df['Global_active_power'].min() >= 0,
                df['Voltage'].min() > 200,
                df['Voltage'].max() <= 250
            ]
            
            # Debug des vérifications
            for i, check in enumerate(checks):
                if not check:
                    print(f"❌ Vérification {i} échouée")
                    if i == 4:  # Global_active_power
                        print(f"   Min puissance: {df['Global_active_power'].min()}")
                    elif i == 5:  # Voltage min
                        print(f"   Min tension: {df['Voltage'].min()}")
                    elif i == 6:  # Voltage max
                        print(f"   Max tension: {df['Voltage'].max()}")
            
            return all(checks)
            
        except Exception as e:
            print(f"Erreur de validation : {e}")
            return False
