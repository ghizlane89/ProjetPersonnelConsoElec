#!/usr/bin/env python3
"""
Module de vérification des données
Partie du bloc 1 - Data Engineering
"""

import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, Any, Optional

class DataChecker:
    """
    Vérificateur de données pour le bloc 1
    """
    
    def __init__(self):
        self.household_file = "data/raw/household.csv"
        self.duckdb_file = "data/processed/energy_2h_aggregated.duckdb"
    
    def check_data_gap(self) -> Dict[str, Any]:
        """
        Vérifie s'il y a un gap dans les données
        """
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(self.household_file):
                return {
                    "has_gap": True,
                    "gap_start": datetime.now(),
                    "gap_end": datetime.now(),
                    "days_missing": 0,
                    "error": "Fichier household.csv non trouvé"
                }
            
            # Lire la dernière ligne du fichier
            df = pd.read_csv(self.household_file, sep='\t')
            
            if len(df) == 0:
                return {
                    "has_gap": True,
                    "gap_start": datetime.now(),
                    "gap_end": datetime.now(),
                    "days_missing": 0,
                    "error": "Fichier household.csv vide"
                }
            
            # Obtenir la dernière date
            last_date_str = df['Date'].iloc[-1]
            last_time_str = df['Time'].iloc[-1]
            
            # Convertir en datetime
            last_datetime = datetime.strptime(
                f"{last_date_str} {last_time_str}", 
                "%d/%m/%Y %H:%M:%S"
            )
            
            # Date actuelle
            current_datetime = datetime.now()
            
            # Calculer le gap avec tolérance de 5 minutes
            tolerance = timedelta(minutes=5)
            gap_duration = current_datetime - last_datetime
            
            if gap_duration > tolerance:
                gap_start = last_datetime + timedelta(minutes=1)
                # gap_end = date actuelle MOINS 1 minute pour éviter les données futures
                gap_end = current_datetime - timedelta(minutes=1)
                days_missing = (gap_end - gap_start).days
                
                return {
                    "has_gap": True,
                    "gap_start": gap_start,
                    "gap_end": gap_end,
                    "days_missing": days_missing,
                    "last_data_date": last_datetime,
                    "current_date": current_datetime,
                    "gap_duration_minutes": gap_duration.total_seconds() / 60,
                    "error": None
                }
            else:
                return {
                    "has_gap": False,
                    "gap_start": None,
                    "gap_end": None,
                    "days_missing": 0,
                    "last_data_date": last_datetime,
                    "current_date": current_datetime,
                    "error": None
                }
                
        except Exception as e:
            return {
                "has_gap": True,
                "gap_start": datetime.now(),
                "gap_end": datetime.now(),
                "days_missing": 0,
                "error": f"Erreur lors de la vérification : {str(e)}"
            }
    
    def get_data_status(self) -> Dict[str, Any]:
        """
        Obtient le statut complet des données
        """
        gap_info = self.check_data_gap()
        
        return {
            "has_gap": gap_info["has_gap"],
            "gap_info": gap_info,
            "household_file_exists": os.path.exists(self.household_file),
            "duckdb_file_exists": os.path.exists(self.duckdb_file),
            "timestamp": datetime.now()
        }
    
    def is_update_needed(self) -> bool:
        """
        Détermine si une mise à jour est nécessaire
        """
        gap_info = self.check_data_gap()
        return gap_info["has_gap"] and gap_info["error"] is None
