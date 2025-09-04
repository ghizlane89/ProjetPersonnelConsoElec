#!/usr/bin/env python3
"""
Module d'exécution du pipeline bloc 1
Partie du bloc 1 - Data Engineering
"""

import subprocess
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class PipelineRunner:
    """
    Exécuteur du pipeline bloc 1
    """
    
    def __init__(self):
        # Chemin absolu vers le script depuis le répertoire racine
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        self.pipeline_script = os.path.join(root_dir, "data_processor.py")
        self.duckdb_file = os.path.join(root_dir, "data/processed/energy_2h_aggregated.duckdb")
        self.backup_duckdb = os.path.join(root_dir, "data/processed/energy_2h_aggregated_backup.duckdb")
    
    def backup_existing_duckdb(self) -> bool:
        """
        Sauvegarde le fichier DuckDB existant
        """
        try:
            if os.path.exists(self.duckdb_file):
                import shutil
                shutil.copy2(self.duckdb_file, self.backup_duckdb)
                print(f"💾 Sauvegarde DuckDB créée : {self.backup_duckdb}")
                return True
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde DuckDB : {e}")
            return False
    
    def run_pipeline(self, progress_callback=None) -> Dict[str, Any]:
        """
        Exécute le pipeline bloc 1
        """
        try:
            print("⚙️ Démarrage du pipeline bloc 1...")
            
            # Sauvegarder le DuckDB existant
            if not self.backup_existing_duckdb():
                return {"success": False, "error": "Impossible de sauvegarder le DuckDB existant"}
            
            # Vérifier que le script existe
            if not os.path.exists(self.pipeline_script):
                return {"success": False, "error": f"Script {self.pipeline_script} non trouvé"}
            
            # Exécuter le pipeline
            start_time = datetime.now()
            
            # Gestion sécurisée du callback de progression
            if progress_callback is not None:
                try:
                    progress_callback(0.1)  # Démarrage
                except Exception as e:
                    print(f"⚠️ Erreur callback progression: {e}")
            
            result = subprocess.run(
                [sys.executable, self.pipeline_script],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(self.pipeline_script)  # Exécuter depuis le répertoire du script
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Gestion sécurisée du callback de progression
            if progress_callback is not None:
                try:
                    progress_callback(1.0)  # Terminé
                except Exception as e:
                    print(f"⚠️ Erreur callback progression: {e}")
            
            # Vérifier le succès
            if result.returncode == 0:
                print(f"✅ Pipeline exécuté avec succès en {duration:.1f} secondes")
                
                # Vérifier que le fichier DuckDB a été créé/mis à jour
                if os.path.exists(self.duckdb_file):
                    file_size = os.path.getsize(self.duckdb_file)
                    return {
                        "success": True,
                        "duration": duration,
                        "output": result.stdout,
                        "duckdb_size": file_size,
                        "timestamp": datetime.now()
                    }
                else:
                    return {
                        "success": False,
                        "error": "Pipeline exécuté mais fichier DuckDB non créé",
                        "output": result.stdout,
                        "error_output": result.stderr
                    }
            else:
                return {
                    "success": False,
                    "error": f"Erreur lors de l'exécution du pipeline (code {result.returncode})",
                    "output": result.stdout,
                    "error_output": result.stderr
                }
                
        except Exception as e:
            return {"success": False, "error": f"Exception lors de l'exécution : {str(e)}"}
    
    def validate_pipeline_output(self) -> Dict[str, Any]:
        """
        Valide la sortie du pipeline
        """
        try:
            if not os.path.exists(self.duckdb_file):
                return {"valid": False, "error": "Fichier DuckDB non trouvé"}
            
            # Vérifier la taille du fichier
            file_size = os.path.getsize(self.duckdb_file)
            if file_size == 0:
                return {"valid": False, "error": "Fichier DuckDB vide"}
            
            # Vérifier le contenu avec DuckDB
            import duckdb
            
            conn = duckdb.connect(self.duckdb_file)
            
            # Vérifier que la table existe
            tables = conn.execute("SHOW TABLES").fetchall()
            if not tables:
                return {"valid": False, "error": "Aucune table trouvée dans le DuckDB"}
            
            # Vérifier les données
            row_count = conn.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
            if row_count == 0:
                return {"valid": False, "error": "Table energy_data vide"}
            
            # Vérifier la plage de dates
            date_range = conn.execute("""
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM energy_data
            """).fetchone()
            
            conn.close()
            
            return {
                "valid": True,
                "file_size": file_size,
                "row_count": row_count,
                "date_range": date_range,
                "tables": [table[0] for table in tables]
            }
            
        except Exception as e:
            return {"valid": False, "error": f"Erreur lors de la validation : {str(e)}"}
    
    def rollback_if_needed(self) -> bool:
        """
        Restaure la sauvegarde si nécessaire
        """
        try:
            if os.path.exists(self.backup_duckdb):
                import shutil
                shutil.copy2(self.backup_duckdb, self.duckdb_file)
                print(f"🔄 Restauration effectuée depuis : {self.backup_duckdb}")
                return True
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la restauration : {e}")
            return False
