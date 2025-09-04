#!/usr/bin/env python3
"""
🎛️ GAP MANAGER - Gestionnaire principal des gaps
===============================================

Interface principale pour la gestion des gaps de données.
Orchestre la détection, génération et mise à jour.

Auteur : Energy Agent Project
"""

from .gap_detector import GapDetector
from .gap_generator import GapGenerator
from .gap_updater import GapUpdater
from datetime import datetime
import logging
from typing import Dict, Callable, Optional

class GapManager:
    """Gestionnaire principal des gaps de données"""
    
    def __init__(self, db_path: str = "data_genere/processed/energy_fictional_2h.duckdb"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Composants
        self.detector = GapDetector(db_path)
        self.generator = GapGenerator(db_path)
        self.updater = GapUpdater(db_path)
    
    def check_and_fill_gaps(self, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Vérifie et comble automatiquement les gaps détectés
        
        Args:
            progress_callback: Fonction de callback pour le progrès (progress, message)
            
        Returns:
            Dict avec le résultat complet de l'opération
        """
        try:
            start_time = datetime.now()
            
            # Étape 1: Détection
            if progress_callback:
                progress_callback(0.1, "🔍 Détection des gaps...")
            
            gap_info = self.detector.detect_gap()
            
            if 'error' in gap_info:
                return {
                    'success': False,
                    'error': gap_info['error'],
                    'message': f"Erreur détection: {gap_info['error']}"
                }
            
            if not gap_info['gap_detected']:
                return {
                    'success': True,
                    'gap_detected': False,
                    'message': '✅ Aucun gap détecté, données à jour'
                }
            
            # Étape 2: Préparation génération
            if progress_callback:
                progress_callback(0.2, "📋 Préparation de la génération...")
            
            missing_timestamps = self.detector.get_missing_timestamps()
            
            if not missing_timestamps:
                return {
                    'success': True,
                    'gap_detected': False,
                    'message': '✅ Aucune donnée à générer'
                }
            
            records_to_generate = len(missing_timestamps)
            
            # Étape 3: Génération
            if progress_callback:
                progress_callback(0.3, f"🔧 Génération de {records_to_generate} enregistrements...")
            
            generated_df = self.generator.generate_gap_data(missing_timestamps)
            
            if generated_df.empty:
                return {
                    'success': False,
                    'message': '❌ Échec génération des données'
                }
            
            # Étape 4: Backup
            if progress_callback:
                progress_callback(0.7, "💾 Création du backup...")
            
            backup_path = self.updater.create_backup()
            
            # Étape 5: Mise à jour
            if progress_callback:
                progress_callback(0.8, "📥 Mise à jour de la base de données...")
            
            update_result = self.updater.update_database(
                generated_df, 
                create_backup=False  # Déjà fait
            )
            update_result['backup_path'] = backup_path
            
            # Étape 6: Validation
            if progress_callback:
                progress_callback(0.9, "✅ Validation...")
            
            if update_result['success']:
                validation = self.updater.validate_database()
                update_result['validation'] = validation
            
            # Finalisation
            if progress_callback:
                progress_callback(1.0, "🎉 Terminé!")
            
            # Temps total
            duration = (datetime.now() - start_time).total_seconds()
            
            # Résultat final
            result = {
                'success': update_result['success'],
                'gap_detected': True,
                'records_generated': records_to_generate,
                'duration': duration,
                'gap_info': gap_info,
                'backup_path': backup_path,
                **update_result
            }
            
            if result['success']:
                human = gap_info.get('human_readable', {})
                result['message'] = f"✅ {records_to_generate} enregistrements générés du {human.get('last_data', '')} au {human.get('missing_until', '')} en {duration:.1f}s"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur gap manager: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'❌ Erreur critique: {e}'
            }
    
    def get_gap_status(self) -> Dict:
        """
        Retourne le statut actuel des gaps
        
        Returns:
            Dict avec informations sur l'état des gaps
        """
        try:
            gap_info = self.detector.detect_gap()
            summary = self.detector.get_gap_summary()
            
            return {
                'gap_detected': gap_info.get('gap_detected', False),
                'summary': summary,
                'gap_info': gap_info
            }
            
        except Exception as e:
            return {
                'gap_detected': True,
                'summary': f"❌ Erreur: {e}",
                'error': str(e)
            }

def main():
    """Test du gestionnaire principal"""
    print("🎛️ Test du gestionnaire de gaps")
    print("=" * 50)
    
    manager = GapManager()
    
    # Test statut
    print("Statut actuel des gaps:")
    status = manager.get_gap_status()
    print(f"  {status['summary']}")
    
    # Test génération (simulation)
    print("\nSimulation génération...")
    
    def progress_callback(progress, message):
        print(f"  [{progress*100:3.0f}%] {message}")
    
    result = manager.check_and_fill_gaps(progress_callback)
    
    print(f"\nRésultat: {result['message']}")
    if result['success'] and result.get('gap_detected'):
        print(f"  Durée: {result['duration']:.1f}s")
        print(f"  Backup: {result.get('backup_path', 'N/A')}")

if __name__ == "__main__":
    main()








