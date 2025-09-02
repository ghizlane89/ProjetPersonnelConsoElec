"""
Orchestrateur LangGraph - Orchestration Layer (Bloc 4)
=====================================================

Orchestrateur principal qui coordonne les Blocs 2 (LLM) et 3 (MCP).
Gère l'exécution complète du workflow : plan → validation → exécution → formatage.
"""

import logging
import time
import sys
import os
from typing import Dict, List, Any, Optional

# Ajouter les chemins pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .plan_validator import PlanValidator
from .error_handler import ErrorHandler
from .result_formatter import ResultFormatter
from .config.orchestration_config import OrchestrationConfig
from .energy_business_logic import energy_business_logic

# Imports des Blocs 2 et 3
try:
    from llm_planner.core.gemini_client import GeminiClient
    from mcp_server.core.mcp_server import MCPServer
except ImportError as e:
    logging.error(f"Erreur d'import des blocs: {e}")
    raise

class LangGraphOrchestrator:
    """Orchestrateur principal LangGraph"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = OrchestrationConfig()
        
        # Initialiser les composants
        self.plan_validator = PlanValidator()
        self.error_handler = ErrorHandler()
        self.result_formatter = ResultFormatter()
        self.business_logic = energy_business_logic
        
        # Initialiser les blocs
        self.llm_client = None
        self.mcp_server = None
        
        self._initialize_blocks()
    
    def _initialize_blocks(self):
        """Initialise les Blocs 2 et 3"""
        try:
            # Bloc 2 - LLM Planner
            self.llm_client = GeminiClient()
            self.logger.info("✅ Bloc 2 (LLM) initialisé")
            
            # Bloc 3 - MCP Server
            self.mcp_server = MCPServer()
            self.logger.info("✅ Bloc 3 (MCP) initialisé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur d'initialisation des blocs: {e}")
            raise
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Traite une question utilisateur complète
        
        Args:
            question: Question utilisateur en français
            
        Returns:
            Réponse formatée avec métadonnées
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🎯 Traitement de la question: {question}")
            
            # ÉTAPE 1: Génération du plan (Bloc 2)
            plan = self._generate_plan(question)
            if not plan:
                return self._create_error_response(question, "Échec de génération du plan")
            
            # ÉTAPE 2: Validation et correction du plan
            corrected_plan = self._validate_and_correct_plan(plan, question)
            
            # Vérifier si le plan a une erreur de validation
            if corrected_plan.get('error'):
                return self._create_error_response(question, corrected_plan['error_message'])
            
            # ÉTAPE 3: Exécution du plan (Bloc 3)
            execution_results = self._execute_plan(corrected_plan)
            
            # ÉTAPE 4: Formatage de la réponse
            final_response = self._format_response(question, corrected_plan, execution_results)
            
            # Calculer le temps total
            total_time = time.time() - start_time
            final_response['total_execution_time'] = total_time
            
            self.logger.info(f"✅ Question traitée en {total_time:.2f}s")
            return final_response
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du traitement: {e}")
            return self._create_error_response(question, str(e))
    
    def _generate_plan(self, question: str) -> Optional[Dict[str, Any]]:
        """Génère un plan avec le Bloc 2 (LLM)"""
        try:
            # Utiliser le retry handler pour la génération de plan
            result = self.error_handler.execute_with_retry(
                self.llm_client.generate_plan,
                question,
                max_retries=2
            )
            
            if result['status'] == 'success':
                return result['result']
            else:
                self.logger.error(f"Échec de génération de plan: {result['error']}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de plan: {e}")
            return None
    
    def _validate_and_correct_plan(self, plan: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Valide et corrige le plan généré"""
        try:
            # Valider la structure du plan
            if not self.plan_validator.validate_plan_structure(plan):
                self.logger.error("Structure de plan invalide")
                return plan
            
            # Valider les dépendances
            if not self.error_handler.validate_dependencies(plan.get('steps', [])):
                self.logger.error("Dépendances invalides dans le plan")
                return plan
            
            # Corriger le plan
            corrected_plan = self.plan_validator.validate_and_correct_plan(plan, question)
            
            self.logger.info(f"Plan corrigé avec {len(corrected_plan.get('corrections', []))} corrections")
            return corrected_plan
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation du plan: {e}")
            return plan
    
    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute le plan avec le Bloc 3 (MCP)"""
        try:
            steps = plan.get('steps', [])
            if not steps:
                return {'status': 'error', 'results': [], 'error': 'Aucune étape à exécuter'}
            
            # Déterminer l'ordre d'exécution
            execution_order = self.error_handler.get_execution_order(steps)
            self.logger.info(f"Ordre d'exécution: {execution_order}")
            
            # Exécuter les étapes dans l'ordre
            step_results = {}
            results = []
            
            for step_id in execution_order:
                step = next(s for s in steps if s['step_id'] == step_id)
                
                try:
                    # Exécuter l'étape avec retry
                    execution_result = self.error_handler.execute_with_retry(
                        self._execute_step,
                        step,
                        max_retries=2
                    )
                    
                    if execution_result['status'] == 'success':
                        step_results[step_id] = execution_result['result']
                        results.append({
                            'step_id': step_id,
                            'tool_name': step.get('tool_name'),
                            'result': execution_result['result']['result'],
                            'execution_time': execution_result['execution_time']
                        })
                    else:
                        # Gérer l'erreur avec fallback
                        fallback_result = self.error_handler.handle_step_error(
                            step, 
                            Exception(execution_result['error']), 
                            step_results
                        )
                        step_results[step_id] = fallback_result
                        results.append({
                            'step_id': step_id,
                            'tool_name': step.get('tool_name'),
                            'result': fallback_result,
                            'execution_time': 0,
                            'status': 'fallback'
                        })
                        
                except Exception as e:
                    self.logger.error(f"Erreur lors de l'exécution de l'étape {step_id}: {e}")
                    fallback_result = self.error_handler.handle_step_error(step, e, step_results)
                    step_results[step_id] = fallback_result
                    results.append({
                        'step_id': step_id,
                        'tool_name': step.get('tool_name'),
                        'result': fallback_result,
                        'execution_time': 0,
                        'status': 'error'
                    })
            
            return {
                'status': 'success',
                'results': results,
                'execution_time': sum(r.get('execution_time', 0) for r in results)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution du plan: {e}")
            return {
                'status': 'error',
                'results': [],
                'error': str(e)
            }
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une étape individuelle avec logique métier"""
        tool_name = step.get('tool_name')
        parameters = step.get('parameters', {})
        
        # Appliquer la logique métier pour valider et corriger les paramètres
        corrected_parameters = self.business_logic.validate_and_correct_parameters(
            parameters, 
            question_context=""  # TODO: Passer le contexte de la question
        )
        
        if tool_name == 'aggregate':
            # Utiliser directement l'outil spécialisé avec paramètres corrigés
            period = corrected_parameters.get('period', '7d')
            aggregation = corrected_parameters.get('aggregation', 'sum')
            filters = corrected_parameters.get('filters', None)
            
            result = self.mcp_server.energy_tools.query_energy_data(period, aggregation, filters)
            
            # Appliquer le post-traitement métier si nécessaire
            if corrected_parameters.get('post_processing'):
                result = self.business_logic.apply_post_processing(result, corrected_parameters)
            
            return {
                "tool": "aggregate",
                "parameters": corrected_parameters,
                "result": result
            }
        elif tool_name == 'post_process':
            return self._execute_post_processing(step, corrected_parameters)
        else:
            raise ValueError(f"Outil non supporté: {tool_name}")
    
    def _execute_post_processing(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute le post-processing"""
        operation = parameters.get('operation')
        depends_on_step = parameters.get('depends_on_step', 1)
        
        # Pour l'instant, retourner un résultat simulé
        # TODO: Implémenter le vrai post-processing
        return {
            'status': 'success',
            'operation': operation,
            'depends_on_step': depends_on_step,
            'business_processing': f"Post-processing {operation} appliqué"
        }
    
    def _format_response(self, question: str, plan: Dict[str, Any], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Formate la réponse finale"""
        try:
            return self.result_formatter.format_final_response(question, plan, execution_results)
        except Exception as e:
            self.logger.error(f"Erreur lors du formatage: {e}")
            return self._create_error_response(question, f"Erreur de formatage: {e}")
    
    def _create_error_response(self, question: str, error_message: str) -> Dict[str, Any]:
        """Crée une réponse d'erreur"""
        return {
            'question': question,
            'answer': f"Erreur lors du traitement: {error_message}",
            'status': 'error',
            'execution_time': 0,
            'corrections_applied': [],
            'total_execution_time': 0
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'orchestrateur"""
        return {
            'bloc_2_status': 'connected' if self.llm_client else 'disconnected',
            'bloc_3_status': 'connected' if self.mcp_server else 'disconnected',
            'config_loaded': True,
            'components': ['plan_validator', 'error_handler', 'result_formatter']
        }
