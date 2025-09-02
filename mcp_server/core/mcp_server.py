#!/usr/bin/env python3
"""
🚀 SERVEUR MCP PRINCIPAL - BLOC 3
================================

Serveur MCP principal pour exécution des plans JSON.
Orchestration des outils et gestion des réponses.

Critères d'acceptation :
- Endpoints sécurisés
- Validation des arguments
- Retour JSON propre
- Performance < 5 secondes
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
import logging

from .database_manager import get_database_manager
from .energy_mcp_tools import get_energy_tools
from .dashboard_tools import get_dashboard_tools


class MCPServer:
    """Serveur MCP pour l'exécution des plans"""
    
    def __init__(self):
        """Initialise le serveur MCP"""
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des composants
        self.db_manager = get_database_manager()
        self.energy_tools = get_energy_tools()
        self.dashboard_tools = get_dashboard_tools()
        
        # Mapping des outils - PRIORITÉ 1: Garder seulement les outils non dupliqués
        self.tools_mapping = {
            "cost": self._execute_cost,
            "plot": self._execute_plot
        }
        
        print("✅ Serveur MCP initialisé")
    
    def execute_plan(self, plan_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécuter un plan JSON généré par le BLOC 2
        Args:
            plan_json: Plan JSON avec étapes et paramètres
        Returns:
            Résultats d'exécution
        """
        try:
            start_time = time.time()
            
            # Validation du plan
            if not isinstance(plan_json, dict) or "steps" not in plan_json:
                return {
                    "status": "error",
                    "message": "Plan JSON invalide - 'steps' manquant",
                    "execution_time": 0
                }
            
            steps = plan_json["steps"]
            if not isinstance(steps, list) or len(steps) == 0:
                return {
                    "status": "error", 
                    "message": "Plan JSON invalide - 'steps' doit être une liste non vide",
                    "execution_time": 0
                }
            
            # Exécution séquentielle des étapes
            results = []
            previous_results = []
            
            for step in steps:
                step_result = self._execute_step(step, previous_results)
                results.append(step_result)
                previous_results.append(step_result)
                
                # Arrêt en cas d'erreur critique
                if step_result.get("status") == "error":
                    break
            
            # Calcul du temps d'exécution
            execution_time = time.time() - start_time
            
            # Résultat final
            final_result = {
                "status": "success" if all(r.get("status") != "error" for r in results) else "partial",
                "steps_executed": len(results),
                "results": results,
                "execution_time": execution_time
            }
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Erreur d'exécution du plan: {e}")
            return {
                "status": "error",
                "message": str(e),
                "execution_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def _execute_step(self, step: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter une étape individuelle"""
        try:
            # Validation de l'étape
            if "tool_name" not in step:
                return {"status": "error", "message": "tool_name manquant"}
            
            tool_name = step["tool_name"]
            parameters = step.get("parameters", {})
            
            if tool_name not in self.tools_mapping:
                return {"status": "error", "message": f"Outil non supporté: {tool_name}"}
            
            # Exécution de l'outil
            result = self.tools_mapping[tool_name](parameters, previous_results)
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur d'exécution de l'étape {step['step_id']}: {e}")
            return {"status": "error", "message": str(e)}
    
    # OUTILS MCP PRINCIPAUX
    def _execute_aggregate(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil d'agrégation avec validation métier"""
        try:
            # Import de la logique métier
            from orchestration.energy_business_logic import energy_business_logic
            
            # Validation et correction métier
            corrected_params = energy_business_logic.validate_and_correct_parameters(parameters)
            
            # Exécution via les outils spécialisés
            result = self.energy_tools.query_energy_data(
                period=corrected_params.get("period", "7d"),
                aggregation=corrected_params.get("aggregation", "sum"),
                equipment=corrected_params.get("equipment"),
                start_date=corrected_params.get("start_date"),
                end_date=corrected_params.get("end_date")
            )
            
            # Post-traitement métier
            processed_result = energy_business_logic.apply_post_processing(result, corrected_params)
            
            return {
                "status": "success",
                "result": processed_result,
                "corrections_applied": corrected_params.get("corrections", [])
            }
            
        except Exception as e:
            self.logger.error(f"Erreur aggregate: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_forecast(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de prévision"""
        try:
            period = parameters.get("period", "7d")
            model_type = parameters.get("model_type", "linear")
            
            result = self.energy_tools.forecast_consumption(period, model_type)
            
            return {
                "status": "success",
                "result": result,
                "parameters_used": parameters
            }
            
        except Exception as e:
            self.logger.error(f"Erreur forecast: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_peak(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil d'analyse des pics"""
        try:
            period = parameters.get("period", "7d")
            threshold = parameters.get("threshold", 2.0)
            
            result = self.energy_tools.detect_peaks(period, threshold)
            
            return {
                "status": "success",
                "result": result,
                "parameters_used": parameters
            }
            
        except Exception as e:
            self.logger.error(f"Erreur peak: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_cost(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de calcul de coûts"""
        try:
            tariff = parameters.get("tariff", 0.20)
            period = parameters.get("period", "30d")
            
            result = self.energy_tools.estimate_costs(tariff, period)
            
            return {
                "status": "success",
                "result": result,
                "parameters_used": parameters
            }
            
        except Exception as e:
            self.logger.error(f"Erreur cost: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_anomaly(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de détection d'anomalies"""
        try:
            method = parameters.get("method", "statistical")
            sensitivity = parameters.get("sensitivity", 2.0)
            
            result = self.energy_tools.detect_anomalies(method, sensitivity)
            
            return {
                "status": "success",
                "result": result,
                "parameters_used": parameters
            }
            
        except Exception as e:
            self.logger.error(f"Erreur anomaly: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_plot(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de visualisation"""
        try:
            chart_type = parameters.get("chart_type", "line")
            period = parameters.get("period", "7d")
            
            # Utiliser les données des résultats précédents si disponibles
            data_source = None
            if previous_results:
                for prev_result in reversed(previous_results):
                    if prev_result.get("status") == "success" and "result" in prev_result:
                        data_source = prev_result["result"]
                        break
            
            if chart_type == "consumption_monthly":
                result = self.dashboard_tools.create_monthly_consumption_chart(period)
            elif chart_type == "equipment_breakdown":
                result = self.dashboard_tools.create_equipment_breakdown_chart()
            elif chart_type == "cost_analysis":
                tariff = parameters.get("tariff", 0.20)
                result = self.dashboard_tools.create_cost_analysis(tariff, period)
            else:
                # Graphique générique
                result = self.dashboard_tools.create_generic_chart(
                    chart_type, period, data_source
                )
            
            return {
                "status": "success",
                "result": result,
                "chart_type": chart_type,
                "parameters_used": parameters
            }
            
        except Exception as e:
            self.logger.error(f"Erreur plot: {e}")
            return {"status": "error", "message": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Vérification de l'état du serveur"""
        try:
            # Test de connexion à la base de données
            db_info = self.db_manager.get_connection_info()
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "server_status": "running",
                "database_info": db_info,
                "available_tools": list(self.tools_mapping.keys()),
                "version": "1.0.0"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Instance globale
_mcp_server: Optional[MCPServer] = None

def get_mcp_server() -> MCPServer:
    """Retourne l'instance globale du serveur MCP"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server