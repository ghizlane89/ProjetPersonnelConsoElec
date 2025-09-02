#!/usr/bin/env python3
"""
Orchestrateur de mise à jour automatique des données
Partie du bloc 1 - Data Engineering
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable

from .data_checker import DataChecker
from .data_generator import DataGenerator
from .pipeline_runner import PipelineRunner

class AutoDataUpdater:
    """
    Orchestrateur principal pour la mise à jour automatique des données
    """
    
    def __init__(self):
        self.checker = DataChecker()
        self.generator = DataGenerator()
        self.pipeline = PipelineRunner()
        
    def run_complete_update(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Exécute la mise à jour complète des données
        """
        start_time = datetime.now()
        results = {
            "start_time": start_time,
            "steps": [],
            "success": False,
            "error": None
        }
        
        try:
            print("🚀 DÉMARRAGE DE LA MISE À JOUR AUTOMATIQUE")
            print("=" * 60)
            
            # Étape 1: Vérification des données
            if progress_callback:
                progress_callback(0.05, "🔍 Vérification des données...")
            
            gap_info = self.checker.check_data_gap()
            results["steps"].append({
                "step": "verification",
                "success": True,
                "gap_info": gap_info
            })
            
            print(f"📊 Gap détecté : {gap_info['has_gap']}")
            if gap_info["has_gap"]:
                print(f"   Période : {gap_info['gap_start']} → {gap_info['gap_end']}")
                print(f"   Jours manquants : {gap_info['days_missing']}")
            
            # Étape 2: Génération des données manquantes (si nécessaire)
            if gap_info["has_gap"] and gap_info["error"] is None:
                if progress_callback:
                    progress_callback(0.15, "🔄 Génération des données manquantes...")
                
                generation_result = self.generator.generate_missing_data(
                    gap_info["gap_start"],
                    gap_info["gap_end"],
                    lambda p: progress_callback(0.15 + p * 0.3, f"Génération... {p*100:.0f}%")
                )
                
                results["steps"].append({
                    "step": "generation",
                    "success": generation_result["success"],
                    "result": generation_result
                })
                
                if not generation_result["success"]:
                    raise Exception(f"Échec de la génération : {generation_result['error']}")
                
                print(f"✅ {generation_result['records_generated']} enregistrements générés")
                
                # Validation des données générées
                if not self.generator.validate_generated_data():
                    raise Exception("Validation des données générées échouée")
                
            # Étape 3: Exécution du pipeline bloc 1
            if progress_callback:
                progress_callback(0.5, "⚙️ Exécution du pipeline bloc 1...")
            
            pipeline_result = self.pipeline.run_pipeline(
                lambda p: progress_callback(0.5 + p * 0.4, f"Pipeline... {p*100:.0f}%")
            )
            
            results["steps"].append({
                "step": "pipeline",
                "success": pipeline_result["success"],
                "result": pipeline_result
            })
            
            if not pipeline_result["success"]:
                raise Exception(f"Échec du pipeline : {pipeline_result['error']}")
            
            print(f"✅ Pipeline exécuté en {pipeline_result['duration']:.1f} secondes")
            
            # Étape 4: Validation finale
            if progress_callback:
                progress_callback(0.95, "🔍 Validation finale...")
            
            validation_result = self.pipeline.validate_pipeline_output()
            results["steps"].append({
                "step": "validation",
                "success": validation_result["valid"],
                "result": validation_result
            })
            
            if not validation_result["valid"]:
                raise Exception(f"Validation échouée : {validation_result['error']}")
            
            print(f"✅ Validation réussie : {validation_result['row_count']} enregistrements")
            
            # Succès complet
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results.update({
                "success": True,
                "end_time": end_time,
                "duration": duration,
                "final_status": "SUCCESS"
            })
            
            if progress_callback:
                progress_callback(1.0, "✅ Mise à jour terminée avec succès !")
            
            print("=" * 60)
            print(f"✅ MISE À JOUR TERMINÉE EN {duration:.1f} SECONDES")
            print(f"📊 Données finales : {validation_result['row_count']} enregistrements")
            print(f"📅 Plage : {validation_result['date_range'][0]} → {validation_result['date_range'][1]}")
            
            return results
            
        except Exception as e:
            # Gestion des erreurs
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results.update({
                "success": False,
                "error": str(e),
                "end_time": end_time,
                "duration": duration,
                "final_status": "ERROR"
            })
            
            print("=" * 60)
            print(f"❌ ERREUR LORS DE LA MISE À JOUR : {e}")
            
            # Tentative de rollback
            try:
                self.pipeline.rollback_if_needed()
                print("🔄 Rollback effectué")
            except:
                print("⚠️ Échec du rollback")
            
            return results
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Obtient un résumé du statut actuel
        """
        status = self.checker.get_data_status()
        
        return {
            "needs_update": self.checker.is_update_needed(),
            "data_status": status,
            "last_check": datetime.now(),
            "system_ready": status["household_file_exists"] and status["duckdb_file_exists"]
        }
    
    def quick_check(self) -> bool:
        """
        Vérification rapide si une mise à jour est nécessaire
        """
        return self.checker.is_update_needed()




