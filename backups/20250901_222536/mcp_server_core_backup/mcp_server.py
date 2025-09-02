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
    """Serveur MCP principal pour exécution des plans"""
    
    def __init__(self):
        """Initialisation du serveur MCP"""
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des composants
        self.db_manager = get_database_manager()
        self.energy_tools = get_energy_tools()
        self.dashboard_tools = get_dashboard_tools()
        
        # Mapping des outils
        self.tools_mapping = {
            "aggregate": self._execute_aggregate,
            "forecast": self._execute_forecast,
            "peak": self._execute_peak,
            "cost": self._execute_cost,
            "anomaly": self._execute_anomaly,
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
            if not self._validate_plan(plan_json):
                return {"status": "error", "message": "Plan invalide"}
            
            # Exécution des étapes
            results = []
            execution_order = self._get_execution_order(plan_json["steps"])
            
            for step_id in execution_order:
                step = self._find_step(plan_json["steps"], step_id)
                if step:
                    result = self._execute_step(step, results)
                    results.append({
                        "step_id": step_id,
                        "tool_name": step["tool_name"],
                        "result": result
                    })
            
            execution_time = time.time() - start_time
            
            # Sérialisation JSON propre
            response = {
                "status": "success",
                "execution_time": execution_time,
                "results": self._serialize_results(results),
                "summary": self._generate_summary(results)
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur d'exécution du plan: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_plan(self, plan_json: Dict[str, Any]) -> bool:
        """Valider la structure du plan"""
        try:
            required_keys = ["metadata", "steps", "summary"]
            for key in required_keys:
                if key not in plan_json:
                    return False
            
            if not plan_json["steps"]:
                return False
            
            return True
        except Exception:
            return False
    
    def _get_execution_order(self, steps: List[Dict[str, Any]]) -> List[int]:
        """Déterminer l'ordre d'exécution des étapes"""
        # Tri topologique simple
        execution_order = []
        completed = set()
        
        while len(execution_order) < len(steps):
            for step in steps:
                if step["step_id"] in completed:
                    continue
                
                # Vérifier les dépendances
                depends_on = step.get("depends_on", [])
                if all(dep in completed for dep in depends_on):
                    execution_order.append(step["step_id"])
                    completed.add(step["step_id"])
            
            # Éviter les boucles infinies
            if len(execution_order) == len(completed):
                break
        
        return execution_order
    
    def _find_step(self, steps: List[Dict[str, Any]], step_id: int) -> Optional[Dict[str, Any]]:
        """Trouver une étape par son ID"""
        for step in steps:
            if step["step_id"] == step_id:
                return step
        return None
    
    def _execute_step(self, step: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter une étape individuelle"""
        try:
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
            from .energy_business_logic import energy_business_logic
            
            # Validation et correction métier
            corrected_parameters = energy_business_logic.validate_and_correct_parameters(
                parameters, 
                question_context=parameters.get("question_context", "")
            )
            
            # Exécution avec paramètres corrigés
            period = corrected_parameters.get("period", "7d")
            aggregation = corrected_parameters.get("aggregation", "sum")
            filters = corrected_parameters.get("filters", None)
            
            result = self.energy_tools.query_energy_data(period, aggregation, filters)
            
            # Post-traitement métier si nécessaire
            result = energy_business_logic.apply_post_processing(result, corrected_parameters)
            
            return {
                "tool": "aggregate",
                "parameters": corrected_parameters,
                "original_parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _execute_forecast(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de prévision"""
        try:
            horizon = parameters.get("horizon", "7d")
            model = parameters.get("model", "simple")
            
            result = self.energy_tools.generate_forecast(horizon, model)
            
            return {
                "tool": "forecast",
                "parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _execute_peak(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de détection de pics"""
        try:
            threshold = parameters.get("threshold", 2.0)
            period = parameters.get("period", "7d")
            
            # Utiliser l'outil d'anomalies avec méthode threshold
            result = self.energy_tools.detect_anomalies(threshold, "threshold")
            
            return {
                "tool": "peak",
                "parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _execute_cost(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de calcul de coûts"""
        try:
            tariff = parameters.get("tariff", 0.20)
            period = parameters.get("period", "30d")
            
            result = self.energy_tools.estimate_costs(tariff, period)
            
            return {
                "tool": "cost",
                "parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _execute_anomaly(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de détection d'anomalies"""
        try:
            threshold = parameters.get("threshold", 2.0)
            method = parameters.get("method", "zscore")
            
            result = self.energy_tools.detect_anomalies(threshold, method)
            
            return {
                "tool": "anomaly",
                "parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _execute_plot(self, parameters: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exécuter l'outil de visualisation"""
        try:
            chart_type = parameters.get("chart_type", "line")
            
            # Mapping des types de graphiques
            plot_mapping = {
                "consumption_overview": self.dashboard_tools.create_consumption_overview,
                "cost_analysis": self.dashboard_tools.create_cost_analysis,
                "anomaly_dashboard": self.dashboard_tools.create_anomaly_dashboard,
                "forecast_dashboard": self.dashboard_tools.create_forecast_dashboard,
                "time_analysis": self.dashboard_tools.create_time_analysis_chart,
                "sub_metering": self.dashboard_tools.create_sub_metering_chart
            }
            
            if chart_type in plot_mapping:
                # Paramètres spécifiques au type de graphique
                if chart_type == "consumption_overview":
                    period = parameters.get("period", "7d")
                    result = plot_mapping[chart_type](period)
                elif chart_type == "cost_analysis":
                    tariff = parameters.get("tariff", 0.20)
                    period = parameters.get("period", "30d")
                    result = plot_mapping[chart_type](tariff, period)
                elif chart_type == "anomaly_dashboard":
                    threshold = parameters.get("threshold", 2.0)
                    result = plot_mapping[chart_type](threshold)
                elif chart_type == "forecast_dashboard":
                    horizon = parameters.get("horizon", "7d")
                    result = plot_mapping[chart_type](horizon)
                elif chart_type == "time_analysis":
                    analysis_type = parameters.get("analysis_type", "hourly")
                    result = plot_mapping[chart_type](analysis_type)
                elif chart_type == "sub_metering":
                    result = plot_mapping[chart_type]()
                else:
                    result = plot_mapping[chart_type]()
            else:
                return {"status": "error", "message": f"Type de graphique non supporté: {chart_type}"}
            
            return {
                "tool": "plot",
                "parameters": parameters,
                "result": {"chart_json": result}
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _serialize_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sérialiser les résultats pour JSON"""
        import json
        from datetime import datetime
        
        def json_serializer(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif hasattr(obj, 'item'):
                return obj.item()
            elif hasattr(obj, '__dict__'):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        serialized_results = []
        for result in results:
            try:
                # Conversion profonde des timestamps
                serialized_result = self._deep_serialize(result)
                serialized_results.append(serialized_result)
            except Exception as e:
                # En cas d'erreur, remplacer par un message d'erreur
                serialized_results.append({
                    "step_id": result.get("step_id"),
                    "tool_name": result.get("tool_name"),
                    "result": {"status": "error", "message": f"Erreur de sérialisation: {str(e)}"}
                })
        
        return serialized_results
    
    def _deep_serialize(self, obj):
        """Sérialisation profonde des objets"""
        if isinstance(obj, dict):
            return {k: self._deep_serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_serialize(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # Timestamp pandas
            return obj.isoformat()
        elif hasattr(obj, 'item'):  # Numpy scalar
            return obj.item()
        elif hasattr(obj, '__dict__'):  # Objet complexe
            return str(obj)
        else:
            return obj
        
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            # Vérifier si les résultats contiennent des erreurs
            successful_steps = []
            failed_steps = []
            
            for r in results:
                result = r.get("result", {})
                # Un résultat est considéré comme réussi s'il n'a pas de statut "error"
                if result.get("status") == "error" or "error" in result:
                    failed_steps.append(r)
                else:
                    successful_steps.append(r)
            
            summary = {
                "total_steps": len(results),
                "successful_steps": len(successful_steps),
                "failed_steps": len(failed_steps),
                "success_rate": len(successful_steps) / len(results) if results else 0,
                "tools_used": list(set(r["tool_name"] for r in results))
            }
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_server_info(self) -> Dict[str, Any]:
        """Obtenir les informations du serveur"""
        try:
            db_info = self.db_manager.get_table_info()
            
            return {
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
