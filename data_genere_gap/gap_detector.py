#!/usr/bin/env python3
"""
🔍 GAP DETECTOR - Détection des données manquantes
=================================================

Détecte les gaps entre la dernière donnée en base et aujourd'hui.
Calcule les périodes manquantes pour génération automatique.

Auteur : Energy Agent Project
"""

import duckdb
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

class GapDetector:
    """Détecteur de gaps dans les données énergétiques"""
    
    def __init__(self, db_path: str = "data_genere/processed/energy_fictional_2h.duckdb"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def detect_gap(self) -> Dict:
        """
        Détecte les gaps dans les données
        
        Returns:
            Dict avec informations sur le gap détecté
        """
        try:
            # Connexion à la base
            conn = duckdb.connect(self.db_path)
            
            # Récupérer la dernière timestamp
            result = conn.execute("""
                SELECT MAX(timestamp) as last_timestamp 
                FROM energy_data
            """).fetchone()
            
            if not result or not result[0]:
                conn.close()
                return {
                    'gap_detected': True,
                    'error': 'Aucune donnée trouvée dans la base',
                    'last_timestamp': None,
                    'current_time': datetime.now(),
                    'gap_hours': 0,
                    'gap_records': 0
                }
            
            last_timestamp = result[0]
            if isinstance(last_timestamp, str):
                last_timestamp = datetime.fromisoformat(last_timestamp)
            
            conn.close()
            
            # Calculer le gap
            current_time = datetime.now()
            
            # Dernière période attendue (hier 22:00)
            yesterday = current_time.date() - timedelta(days=1)
            expected_last = datetime.combine(yesterday, datetime.min.time().replace(hour=22))
            
            # Vérifier s'il y a un gap
            gap_detected = last_timestamp < expected_last
            
            if gap_detected:
                # Calculer la première période manquante (2h après la dernière)
                next_expected = last_timestamp + timedelta(hours=2)
                
                # Calculer le nombre d'heures manquantes
                gap_hours = int((expected_last - last_timestamp).total_seconds() / 3600)
                
                # Calculer le nombre d'enregistrements manquants (toutes les 2h)
                gap_records = gap_hours // 2
                
                return {
                    'gap_detected': True,
                    'last_timestamp': last_timestamp,
                    'expected_last': expected_last,
                    'next_expected': next_expected,
                    'current_time': current_time,
                    'gap_hours': gap_hours,
                    'gap_records': gap_records,
                    'gap_start': next_expected,
                    'gap_end': expected_last,
                    'human_readable': {
                        'last_data': last_timestamp.strftime('%d/%m/%Y %H:%M'),
                        'missing_until': expected_last.strftime('%d/%m/%Y %H:%M'),
                        'gap_days': gap_hours // 24,
                        'gap_remaining_hours': gap_hours % 24
                    }
                }
            else:
                return {
                    'gap_detected': False,
                    'last_timestamp': last_timestamp,
                    'current_time': current_time,
                    'message': 'Données à jour'
                }
                
        except Exception as e:
            self.logger.error(f"Erreur détection gap: {e}")
            return {
                'gap_detected': True,
                'error': str(e),
                'last_timestamp': None,
                'current_time': datetime.now()
            }
    
    def get_missing_timestamps(self) -> list:
        """
        Retourne la liste des timestamps manquants
        
        Returns:
            Liste des datetime manquants (toutes les 2h)
        """
        gap_info = self.detect_gap()
        
        if not gap_info['gap_detected'] or 'gap_start' not in gap_info:
            return []
        
        missing_timestamps = []
        current = gap_info['gap_start']
        end = gap_info['gap_end']
        
        while current <= end:
            missing_timestamps.append(current)
            current += timedelta(hours=2)
        
        return missing_timestamps
    
    def get_gap_summary(self) -> str:
        """
        Retourne un résumé textuel du gap
        
        Returns:
            Texte descriptif du gap détecté
        """
        gap_info = self.detect_gap()
        
        if 'error' in gap_info:
            return f"❌ Erreur : {gap_info['error']}"
        
        if not gap_info['gap_detected']:
            return "✅ Données à jour"
        
        human = gap_info.get('human_readable', {})
        last_data = human.get('last_data', 'Inconnue')
        missing_until = human.get('missing_until', 'Inconnue')
        gap_days = human.get('gap_days', 0)
        gap_hours = human.get('gap_remaining_hours', 0)
        records = gap_info.get('gap_records', 0)
        
        if gap_days > 0:
            if gap_hours > 0:
                duration = f"{gap_days} jour(s) et {gap_hours}h"
            else:
                duration = f"{gap_days} jour(s)"
        else:
            duration = f"{gap_hours}h"
        
        return f"⚠️ Données manquantes du {last_data} au {missing_until} ({duration}, {records} enregistrements)"

def main():
    """Test du détecteur de gaps"""
    print("🔍 Test du détecteur de gaps")
    print("=" * 50)
    
    detector = GapDetector()
    
    # Test de détection
    gap_info = detector.detect_gap()
    print("Informations du gap :")
    for key, value in gap_info.items():
        print(f"  {key}: {value}")
    
    print("\nRésumé :")
    print(detector.get_gap_summary())
    
    # Test des timestamps manquants
    missing = detector.get_missing_timestamps()
    print(f"\nNombre de timestamps manquants : {len(missing)}")
    
    if missing:
        print("Premiers timestamps manquants :")
        for i, ts in enumerate(missing[:5]):
            print(f"  {i+1}. {ts.strftime('%d/%m/%Y %H:%M')}")
        
        if len(missing) > 5:
            print(f"  ... et {len(missing) - 5} autres")

if __name__ == "__main__":
    main()








