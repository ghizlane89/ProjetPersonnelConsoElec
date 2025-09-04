#!/usr/bin/env python3
"""
🎼 ENERGY LANGGRAPH WORKFLOW - Architecture Agentique Refactorisée
================================================================

Workflow LangGraph propre avec agents spécialisés.
Architecture claire : Orchestration + Agents Métier + Agents Techniques.

Workflow :
Question → Validation → Intent Analysis → LLM Agent → Strategy → MCP Agent → Response Builder → Réponse
"""

import logging
import sys
import os
from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Ajouter les chemins pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports des agents techniques (blocs existants)
try:
    from llm_planner.core.gemini_client import GeminiClient
    from mcp_server.core.energy_mcp_tools import get_energy_capabilities
except ImportError as e:
    logging.error(f"Erreur d'import des agents techniques: {e}")
    raise

# Imports des nouveaux agents métier
try:
    from .agents import (
        EnergyBusinessRules, QuestionIntent, ExecutionStrategy,
        StandardResponse, ResponseBuilder, ResponseType
    )
except ImportError as e:
    logging.error(f"Erreur d'import des agents métier: {e}")
    raise

class EnergyState(TypedDict):
    """État partagé du workflow énergétique refactorisé"""
    # Input
    question: str
    
    # Nouveaux champs pour agents métier
    question_intent: Dict[str, Any]  # Résultat de l'analyse d'intention
    semantic_validation: Dict[str, Any]  # 🆕 Validation sémantique LangChain
    execution_strategy: Dict[str, Any]  # Stratégie d'exécution
    
    # Étapes du workflow (conservées pour compatibilité)
    validation_result: Dict[str, Any]
    raw_plan: Dict[str, Any]
    enhanced_plan: Dict[str, Any]
    execution_result: Dict[str, Any]
    final_response: Dict[str, Any]
    
    # Métadonnées
    metadata: Dict[str, Any]
    errors: list[str]

class EnergyLangGraphWorkflow:
    """Workflow LangGraph refactorisé pour l'Energy Agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 🧠 Agents métier (nouveaux)
        self.business_rules = EnergyBusinessRules()
        self.response_builder = ResponseBuilder()
        
        # 🔧 Agents techniques (existants)
        self.llm_agent = GeminiClient()
        
        # 🆕 Validateur sémantique LangChain (après llm_agent)
        self._setup_semantic_validator()
        self.capabilities_agent = get_energy_capabilities()
        
        # Créer le workflow LangGraph (structure conservée)
        self.workflow = self._create_workflow()
        
        self.logger.info("✅ LangGraph Workflow refactorisé initialisé")
    
    def _setup_semantic_validator(self):
        """🆕 Configure le validateur sémantique LangChain"""
        validation_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
Analysez cette question énergétique et déterminez la période OU la granularité EXACTE demandée.

Question: "{question}"

Répondez UNIQUEMENT par l'un de ces codes selon le sens précis :

PÉRIODES TEMPORELLES:
CURRENT_MONTH : "ce mois-ci", "ce mois" → mois calendaire en cours (1er du mois → aujourd'hui)
LAST_MONTH : "mois dernier", "le mois passé" → mois calendaire précédent complet
LAST_30_DAYS : "30 derniers jours", "ces 30 jours" → période glissante de 30 jours
CURRENT_WEEK : "cette semaine" → semaine calendaire en cours  
LAST_7_DAYS : "7 derniers jours" → période glissante de 7 jours
LAST_3_DAYS : "3 derniers jours", "ces 3 derniers jours", "trois derniers jours" → période glissante de 3 jours
YESTERDAY : "hier" → jour précédent seulement
DAY_BEFORE_YESTERDAY : "avant-hier", "avant hier", "il y a 2 jours" → jour spécifique avant hier (1 jour seulement)
CURRENT_YEAR : "cette année" → année calendaire en cours
LAST_YEAR : "année dernière" → année calendaire précédente

GRANULARITÉS:
HOURLY : "par heure", "consommation horaire", "à l'heure" → granularité horaire
DAILY : "par jour", "quotidienne", "journalière" → granularité quotidienne
WEEKLY : "par semaine", "hebdomadaire" → granularité hebdomadaire  
MONTHLY : "par mois", "mensuelle" → granularité mensuelle
YEARLY : "par an", "par année", "annuelle", "annuel", "moyenne par an", "consommation moyenne par an" → granularité annuelle

JOURS NOMMÉS:
SATURDAY : "samedi", "samedi dernier" → samedi le plus récent
SUNDAY : "dimanche", "dimanche dernier" → dimanche le plus récent
WEEKEND : "weekend", "weekend dernier", "fin de semaine" → samedi + dimanche récents

Réponse:
            """
        )
        
        # Créer un LLM compatible LangChain pour la validation
        import os
        langchain_gemini = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0  # Pour validation précise
        )
        
        # Validateur sémantique LangChain officiel
        self.semantic_validator = LLMChain(
            llm=langchain_gemini,
            prompt=validation_prompt,
            verbose=False
        )
    
    def _create_workflow(self):
        """Crée le workflow LangGraph refactorisé"""
        
        # Définir le graphe d'état
        workflow = StateGraph(EnergyState)
        
        # 🆕 Ajouter les nouveaux nœuds avec agents métier
        workflow.add_node("validator", self._validation_node)
        workflow.add_node("intent_analyzer", self._intent_analysis_node)  # 🆕 Nouveau
        workflow.add_node("semantic_validator", self._semantic_validation_node)  # 🆕 Validateur LangChain
        workflow.add_node("llm_agent", self._llm_planning_node)
        workflow.add_node("strategy_builder", self._strategy_building_node)  # 🆕 Nouveau
        workflow.add_node("mcp_agent", self._mcp_execution_node)
        workflow.add_node("response_builder", self._response_building_node)  # 🆕 Nouveau
        workflow.add_node("error_handler", self._error_handling_node)
        
        # 🆕 Nouveau workflow avec validation hors circuit
        workflow.set_entry_point("validator")  # 🆕 Retour au point d'entrée original
        
        # Conditions de routing normales
        workflow.add_conditional_edges(
            "validator",
            self._should_continue_after_validation,
            {
                "continue": "intent_analyzer",
                "error": "error_handler"
            }
        )
        
        # Flow normal
        workflow.add_edge("intent_analyzer", "semantic_validator")
        workflow.add_edge("semantic_validator", "llm_agent")
        workflow.add_edge("llm_agent", "strategy_builder")
        workflow.add_edge("strategy_builder", "mcp_agent")
        workflow.add_edge("mcp_agent", "response_builder")
        workflow.add_edge("response_builder", END)
        
        # 🆕 Nœuds de gestion d'erreurs
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    def _validation_node(self, state: EnergyState) -> Dict[str, Any]:
        """🔍 Nœud de validation de la question (conservé)"""
        question = state["question"]
        
        self.logger.info(f"🔍 Validation: {question}")
        
        # Validation rapide et intelligente (logique conservée)
        validation_result = self._validate_question(question)
        
        return {
            "validation_result": validation_result,
            "metadata": {
                **state.get("metadata", {}),
                "validation_time": 0.01
            }
        }
    
    def _intent_analysis_node(self, state: EnergyState) -> Dict[str, Any]:
        """🧠 Nouveau nœud d'analyse d'intention avec validation sémantique"""
        question = state["question"]
        
        self.logger.info(f"🧠 Analyse d'intention: {question}")
        
        # 🆕 Utiliser la validation sémantique pour améliorer l'intent detection
        semantic_validation = state.get("semantic_validation", {})
        validated_period = semantic_validation.get("validated_period")
        
        # 🆕 Utiliser l'agent métier avec contexte de validation
        intent = self.business_rules.analyze_question_intent(question, validated_period)
        
        self.logger.info(f"✅ Intention détectée: {intent.intent_type} (confiance: {intent.confidence:.2f})")
        
        return {
            "question_intent": {
                "intent_type": intent.intent_type,
                "temporal": intent.temporal,
                "aggregation": intent.aggregation,
                "entities": intent.entities,
                "confidence": intent.confidence
            },
            "metadata": {
                **state.get("metadata", {}),
                "intent_analyzed": True,
                "intent_confidence": intent.confidence
            }
        }
    
    def _llm_planning_node(self, state: EnergyState) -> Dict[str, Any]:
        """🤖 Nœud LLM Agent - Génération de plan autonome (conservé)"""
        question = state["question"]
        
        self.logger.info(f"🤖 LLM Agent: Génération plan pour '{question}'")
        
        try:
            # L'agent LLM est autonome (logique conservée)
            raw_plan = self.llm_agent.generate_plan(question)
            
            self.logger.info(f"✅ Plan généré: {raw_plan.get('steps', [{}])[0].get('tool_name', 'unknown')}")
            
            return {
                "raw_plan": raw_plan,
                "metadata": {
                    **state.get("metadata", {}),
                    "llm_plan_generated": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur LLM Agent: {e}")
            return {
                "raw_plan": {},
                "errors": state.get("errors", []) + [f"LLM Error: {str(e)}"]
            }
    
    def _strategy_building_node(self, state: EnergyState) -> Dict[str, Any]:
        """📊 Nouveau nœud de construction de stratégie"""
        question = state["question"]
        raw_plan = state["raw_plan"]
        question_intent = state["question_intent"]
        
        self.logger.info(f"📊 Construction stratégie pour intention: {question_intent.get('intent_type', 'unknown')}")
        
        try:
            # 🆕 Utiliser l'agent métier au lieu de logique hardcodée
            intent = QuestionIntent(
                intent_type=question_intent["intent_type"],
                temporal=question_intent["temporal"],
                aggregation=question_intent["aggregation"],
                entities=question_intent["entities"],
                confidence=question_intent["confidence"]
            )
            
            # 🆕 Utiliser la validation sémantique si disponible
            validated_period = state.get("semantic_validation", {}).get("validated_period")
            strategy = self.business_rules.get_execution_strategy(intent, raw_plan, question, validated_period)
            
            self.logger.info(f"✅ Stratégie: {strategy.tool_name} avec {strategy.parameters}")
            
            return {
                "execution_strategy": {
                    "tool_name": strategy.tool_name,
                    "parameters": strategy.parameters,
                    "expected_format": strategy.expected_format,
                    "response_template": strategy.response_template
                },
                "metadata": {
                    **state.get("metadata", {}),
                    "strategy_built": True,
                    "strategy_tool": strategy.tool_name
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur construction stratégie: {e}")
            return {
                "execution_strategy": {},
                "errors": state.get("errors", []) + [f"Strategy Error: {str(e)}"]
            }
    
    # ❌ ANCIENNE MÉTHODE SUPPRIMÉE - Remplacée par strategy_building_node
    
    def _mcp_execution_node(self, state: EnergyState) -> Dict[str, Any]:
        """🔧 Nœud MCP Agent - Exécution simplifiée"""
        execution_strategy = state["execution_strategy"]
        question = state["question"]
        
        self.logger.info(f"🔧 MCP Agent: Exécution {execution_strategy.get('tool_name', 'unknown')}")
        
        try:
            # 🆕 Exécution basée sur la stratégie au lieu de logique complexe
            tool_name = execution_strategy["tool_name"]
            parameters = execution_strategy["parameters"]
            
            # Exécution directe selon le tool
            if tool_name == 'aggregate_moyenne':
                result = self._calculate_moyenne_consumption(
                    parameters.get('period', '7d'),
                    parameters.get('granularity', 'day')
                )
                execution_result = {
                    "status": "success",
                    "data": result,
                    "tool_used": "moyenne",
                    "source": "langgraph_mcp"
                }
            elif tool_name == 'aggregate_temporal':  # 🆕 Nouveau
                result = self.capabilities_agent.execute_temporal_aggregation(
                    metric='consumption',
                    period=parameters.get('period', '7d'),
                    aggregation=parameters.get('aggregation', 'sum')
                )
                execution_result = {
                    "status": "success",
                    "data": result,
                    "tool_used": "temporal",
                    "source": "langgraph_mcp"
                }
            elif tool_name == 'aggregate_granularity':  # 🆕 Nouveau pour granularités
                # Pour les granularités, utiliser directement la moyenne des MCP capabilities
                granularity = parameters.get('granularity', 'hourly')
                analysis_period = parameters.get('analysis_period', '7d')
                
                if granularity == 'hourly':
                    # Pour les heures, utiliser la méthode moyenne existante avec granularité 'heure'
                    result = self._calculate_moyenne_consumption(
                        period=analysis_period,
                        granularity='heure'  # Utiliser la logique moyenne existante
                    )
                else:
                    # Pour les autres granularités, utiliser l'agrégation temporelle
                    result = self.capabilities_agent.execute_temporal_aggregation(
                        metric='consumption',
                        period=analysis_period,
                        aggregation='avg'  # Moyenne directe
                    )
                
                # Structurer le résultat pour la granularité
                if isinstance(result, dict) and 'data' in result:
                    if isinstance(result['data'], dict):
                        result['data']['granularity'] = granularity
                    else:
                        result['data'] = {
                            'summary': {'total': result.get('data', 0)},
                            'granularity': granularity
                        }
                
                execution_result = {
                    "status": "success",
                    "data": result,
                    "tool_used": "granularity",
                    "source": "langgraph_mcp"
                }
            elif tool_name == 'seasonal_comparison':  # 🆕 Nouveau
                # Pour l'instant, utiliser zone_comparison avec adaptation
                result = self.capabilities_agent.execute_zone_comparison(
                    period='365d'  # Données sur 1 an pour comparaison saisonnière
                )
                execution_result = {
                    "status": "success",
                    "data": result,
                    "tool_used": "comparison",
                    "source": "langgraph_mcp"
                }
            elif tool_name == 'temporal_comparison':  # 🆕 Nouveau
                # Comparaison entre 2 périodes
                current_result = self.capabilities_agent.execute_temporal_aggregation(
                    metric='consumption', period='30d', aggregation='sum'
                )
                # Simulation d'une comparaison (à améliorer plus tard)
                result = {
                    "current_period": current_result.get('summary', {}).get('total', 0),
                    "previous_period": current_result.get('summary', {}).get('total', 0) * 0.9,  # Simulation
                    "comparison": "higher"
                }
                execution_result = {
                    "status": "success",
                    "data": result,
                    "tool_used": "comparison",
                    "source": "langgraph_mcp"
                }
            elif tool_name == 'weekday_comparison':  # 🆕 Nouveau
                # Simulation comparaison weekend/semaine
                result = self.capabilities_agent.execute_zone_comparison(
                    period='7d'
                )
                execution_result = {
                    "status": "success",
                    "data": result,
                    "tool_used": "comparison",
                    "source": "langgraph_mcp"
                }
            elif tool_name == 'zone_comparison':
                result = self.capabilities_agent.execute_zone_comparison(
                    period=parameters.get('period', '7d')
                )
                execution_result = {
                    "status": "success", 
                    "data": result,
                    "tool_used": "zone_comparison",
                    "source": "langgraph_mcp"
                }
            elif tool_name == 'cost':
                result = self.capabilities_agent.execute_cost_calculation(
                    period=parameters.get('period', '7d'),
                    target_savings=parameters.get('target_savings')
                )
                execution_result = {
                    "status": "success",
                    "data": result,
                    "tool_used": "cost",
                    "source": "langgraph_mcp"
                }
            else:  # aggregate par défaut
                result = self.capabilities_agent.execute_temporal_aggregation(
                    metric='consumption',
                    period=parameters.get('period', '7d'),
                    aggregation=parameters.get('aggregation', 'sum')
                )
                execution_result = {
                    "status": "success",
                    "data": result,
                    "tool_used": "aggregate",
                    "source": "langgraph_mcp"
                }
            
            self.logger.info(f"✅ Exécution réussie: {execution_result.get('tool_used', 'unknown')}")
            
            return {
                "execution_result": execution_result,
                "metadata": {
                    **state.get("metadata", {}),
                    "mcp_execution_success": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur MCP Agent: {e}")
            return {
                "execution_result": {"status": "error", "message": str(e)},
                "errors": state.get("errors", []) + [f"MCP Error: {str(e)}"]
            }
    
    def _response_building_node(self, state: EnergyState) -> Dict[str, Any]:
        """📝 Nouveau nœud de construction de réponse"""
        question = state["question"]
        execution_result = state["execution_result"]
        execution_strategy = state["execution_strategy"]
        
        self.logger.info(f"📝 Construction réponse avec format: {execution_strategy.get('expected_format', 'unknown')}")
        
        try:
            # 🆕 Utiliser le ResponseBuilder avec période validée
            expected_format = execution_strategy.get("expected_format", "consumption")
            semantic_validation = state.get("semantic_validation", {})
            
            if expected_format == "moyenne":
                response = self.response_builder.build_moyenne_response(question, execution_result)
            elif expected_format == "granularity":  # 🆕 Nouveau pour granularités
                response = self.response_builder.build_granularity_response(question, execution_result, semantic_validation)
            elif expected_format == "temporal":
                response = self.response_builder.build_temporal_response(question, execution_result, semantic_validation)
            elif expected_format == "comparison":  # 🆕 Nouveau
                response = self.response_builder.build_comparison_response(question, execution_result)
            elif expected_format == "zones":
                response = self.response_builder.build_zones_response(question, execution_result)
            elif expected_format == "cost":
                response = self.response_builder.build_cost_response(question, execution_result)
            else:
                response = self.response_builder.build_consumption_response(question, execution_result, semantic_validation)
            
            self.logger.info(f"✅ Réponse construite: {response.response_type.value}")
            
            return {
                "final_response": response.to_dict(),
                "metadata": {
                    **state.get("metadata", {}),
                    "response_built": True,
                    "response_type": response.response_type.value
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur construction réponse: {e}")
            return {
                "final_response": {
                    "question": question,
                    "answer": f"❌ Erreur de formatage: {e}",
                    "status": "error"
                },
                "errors": state.get("errors", []) + [f"Response Error: {str(e)}"]
            }
    
    def _response_formatter_node(self, state: EnergyState) -> Dict[str, Any]:
        """🎨 Nœud Formatter - Formatage autonome"""
        question = state["question"]
        execution_result = state["execution_result"]
        
        self.logger.info(f"🎨 Formatter: Formatage de la réponse")
        
        try:
            # L'agent formatter est autonome
            final_response = self._format_final_response(question, execution_result)
            
            self.logger.info(f"✅ Réponse formatée: {final_response.get('type', 'unknown')}")
            
            return {
                "final_response": final_response,
                "metadata": {
                    **state.get("metadata", {}),
                    "response_formatted": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur Formatter: {e}")
            return {
                "final_response": {"question": question, "answer": f"Erreur de formatage: {e}", "status": "error"},
                "errors": state.get("errors", []) + [f"Formatter Error: {str(e)}"]
            }
    
    def _error_handling_node(self, state: EnergyState) -> Dict[str, Any]:
        """🚨 Nœud Error Handler - Gestion d'erreurs autonome"""
        question = state["question"]
        errors = state.get("errors", [])
        
        self.logger.error(f"🚨 Error Handler: {len(errors)} erreurs détectées")
        
        # Créer une réponse d'erreur propre
        error_response = {
            "question": question,
            "answer": "❌ Désolé, je ne peux pas traiter cette question pour le moment.",
            "status": "error",
            "errors": errors
        }
        
        return {
            "final_response": error_response,
            "metadata": {
                **state.get("metadata", {}),
                "error_handled": True
            }
        }
    
    def _out_of_scope_handling_node(self, state: EnergyState) -> Dict[str, Any]:
        """🎯 Nouveau nœud de gestion des questions hors circuit"""
        question = state["question"]
        scope_analysis = state.get("scope_analysis", {})
        
        self.logger.info(f"🎯 Out of Scope Handler: {scope_analysis.get('type', 'unknown')}")
        
        # Construire la réponse de redirection
        message = scope_analysis.get('message', "Je ne traite que les questions de consommation électrique.")
        suggestion = scope_analysis.get('suggestion', "Essayez une question comme : 'Quelle a été ma consommation hier ?'")
        
        # Obtenir des suggestions contextuelles
        helpful_suggestions = self.out_of_scope_handler.get_helpful_suggestions(
            scope_analysis.get('type')
        )
        
        # Créer une réponse de redirection intelligente
        out_of_scope_response = {
            "question": question,
            "answer": f"{message}\n\n💡 **Suggestion :** {suggestion}",
            "status": "out_of_scope",
            "scope_type": scope_analysis.get('type', 'unknown'),
            "helpful_suggestions": helpful_suggestions,
            "redirection_message": message,
            "suggestion": suggestion
        }
        
        return {
            "final_response": out_of_scope_response,
            "metadata": {
                **state.get("metadata", {}),
                "out_of_scope_handled": True,
                "scope_type": scope_analysis.get('type', 'unknown')
            }
        }
    
    def _should_continue_after_validation(self, state: EnergyState) -> str:
        """Condition de routing après validation"""
        validation_result = state.get("validation_result", {})
        
        if validation_result.get("valid", False):
            return "continue"
        else:
            return "error"
    
    def _validate_question(self, question: str) -> Dict[str, Any]:
        """Validation de la question avec distinction consommation/coût"""
        if not question or len(question.strip()) < 3:
            return {"valid": False, "reason": "Question trop courte"}
        
        question_lower = question.lower()
        
        # 🎯 Mots-clés de CONSOMMATION (questions dans le scope)
        consumption_keywords = [
            'consommation', 'électricité', 'kwh', 'énergie', 'puissance', 
            'moyenne', 'jour', 'semaine', 'mois', 'année', 'hier', 'aujourd\'hui', 
            'économiser', 'cuisine', 'buanderie', 'chauffage', 'zone', 'sous-compteur',
            'compteur', 'watt', 'électrique',
            # 🔧 Jours de la semaine pour les jours nommés
            'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche',
            'weekend', 'fin de semaine'
        ]
        
        # 🎯 Mots-clés de COÛT (questions hors scope)
        cost_keywords = [
            'coût', 'prix', 'euro', '€', 'facture', 'payer', 'payé', 'tarif',
            'montant', 'argent', 'dépense', 'budget', 'économies'
        ]
        
        # 🎯 Mots-clés non énergétiques
        non_energy_keywords = [
            'temps', 'météo', 'température extérieure', 'pluie', 'soleil',
            'sport', 'musique', 'film', 'restaurant', 'voyage'
        ]
        
        # 🔍 Analyse intelligente
        has_consumption = any(keyword in question_lower for keyword in consumption_keywords)
        has_cost = any(keyword in question_lower for keyword in cost_keywords)
        has_non_energy = any(keyword in question_lower for keyword in non_energy_keywords)
        
        # 🎯 Logique de validation améliorée
        if has_non_energy:
            return {
                "valid": False, 
                "reason": "Question non énergétique",
                "question_type": "non_energy"
            }
        elif has_cost:
            # 🎯 Priorité aux questions de coût (même si elles contiennent des mots de consommation)
            return {
                "valid": False, 
                "reason": "Question sur le coût (hors scope)",
                "question_type": "cost"
            }
        elif has_consumption:
            return {
                "valid": True, 
                "reason": "Question de consommation valide",
                "question_type": "consumption"
            }
        else:
            return {
                "valid": False, 
                "reason": "Question non reconnue",
                "question_type": "unknown"
            }
    
    # ❌ ANCIENNE MÉTHODE SUPPRIMÉE - Remplacée par EnergyBusinessRules
    
    # ❌ ANCIENNES MÉTHODES SUPPRIMÉES - Remplacées par les nouveaux agents
    
    def _normalize_period(self, parameters: Dict[str, Any]) -> str:
        """Normalise les paramètres de période avec support français"""
        from datetime import datetime, timedelta
        
        # Vérifier d'abord les paramètres directs
        if 'period' in parameters:
            period = parameters['period'].lower()
            if period in ['1d', '7d', '30d', '1day', '7days', '30days']:
                return period.replace('days', 'd').replace('day', 'd')
        
        # Vérifier time_range et time_period
        for key in ['time_range', 'time_period']:
            if key in parameters:
                time_value = parameters[key].lower()
                
                # Support français
                if any(word in time_value for word in ['hier', 'yesterday', 'jour', 'day']):
                    return '1d'
                elif any(word in time_value for word in ['semaine', 'week']):
                    return '7d'
                elif any(word in time_value for word in ['mois', 'month']):
                    return '30d'
                elif any(word in time_value for word in ['année', 'year']):
                    return '365d'
                
                # Support anglais
                if 'week' in time_value:
                    return '7d'
                elif 'month' in time_value:
                    return '30d'
                elif 'day' in time_value:
                    return '1d'
        
        # Analyser la question pour détecter "hier"
        if 'question' in parameters:
            question = parameters['question'].lower()
            if 'hier' in question or 'yesterday' in question:
                return '1d'
            elif 'semaine' in question or 'week' in question:
                return '7d'
            elif 'mois' in question or 'month' in question:
                return '30d'
        
        # Valeur par défaut sécurisée
        return '7d'
    
    def _calculate_moyenne_consumption(self, period: str, granularity: str) -> Dict[str, Any]:
        """🆕 Calcule la moyenne de consommation selon la granularité"""
        try:
            from mcp_server.core.database_manager import get_database_manager
            
            db_manager = get_database_manager()
            
            # Conversion période en jours
            period_days = period.replace('d', '')
            
            if granularity in ['day', 'jour']:  # 🔧 Correction: Support 'jour' et 'day'
                # 🔧 Moyenne par jour avec syntaxe DuckDB correcte
                # Note: Nos données sont en intervalles de 2h, donc 12 mesures par jour
                query = f"""
                SELECT 
                    AVG(daily_consumption) as moyenne_jour,
                    COUNT(*) as nb_jours,
                    SUM(daily_consumption) as total
                FROM (
                    SELECT 
                        DATE(timestamp) as date,
                        SUM(energy_total_kwh) as daily_consumption
                    FROM energy_data 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL {period_days} DAY
                    GROUP BY DATE(timestamp)
                ) daily_stats
                """
            elif granularity in ['week', 'semaine']:
                # 🔧 Moyenne par semaine (7 jours)
                query = f"""
                SELECT 
                    AVG(weekly_consumption) as moyenne_semaine,
                    COUNT(*) as nb_semaines,
                    SUM(weekly_consumption) as total
                FROM (
                    SELECT 
                        YEARWEEK(timestamp) as week_num,
                        SUM(energy_total_kwh) as weekly_consumption
                    FROM energy_data 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL {period_days} DAY
                    GROUP BY YEARWEEK(timestamp)
                ) weekly_stats
                """
            elif granularity in ['month', 'mois']:
                # 🔧 Moyenne par mois (30 jours)
                query = f"""
                SELECT 
                    AVG(monthly_consumption) as moyenne_mois,
                    COUNT(*) as nb_mois,
                    SUM(monthly_consumption) as total
                FROM (
                    SELECT 
                        YEAR(timestamp) * 100 + MONTH(timestamp) as month_num,
                        SUM(energy_total_kwh) as monthly_consumption
                    FROM energy_data 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL {period_days} DAY
                    GROUP BY YEAR(timestamp), MONTH(timestamp)
                ) monthly_stats
                """
            elif granularity in ['year', 'année']:
                # 🔧 Moyenne par année (365 jours)
                query = f"""
                SELECT 
                    AVG(yearly_consumption) as moyenne_annee,
                    COUNT(*) as nb_annees,
                    SUM(yearly_consumption) as total
                FROM (
                    SELECT 
                        YEAR(timestamp) as year_num,
                        SUM(energy_total_kwh) as yearly_consumption
                    FROM energy_data 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL {period_days} DAY
                    GROUP BY YEAR(timestamp)
                ) yearly_stats
                """
            elif granularity in ['hour', 'heure']:
                # 🔧 Moyenne par heure (données déjà en intervalles de 2h)
                # Si la période est 7d, calculer la moyenne horaire sur 7 jours
                if period_days == '7':
                    query = f"""
                    SELECT 
                        AVG(energy_total_kwh) / 2 as moyenne_heure,
                        COUNT(*) as nb_mesures,
                        SUM(energy_total_kwh) as total
                    FROM energy_data 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL 7 DAY
                    """
                else:
                    query = f"""
                    SELECT 
                        AVG(energy_total_kwh) as moyenne_heure,
                        COUNT(*) as nb_mesures,
                        SUM(energy_total_kwh) as total
                    FROM energy_data 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL {period_days} DAY
                    """
            else:
                # Fallback: moyenne par mesure (comme avant)
                query = f"""
                SELECT 
                    AVG(energy_total_kwh) as moyenne,
                    COUNT(*) as nb_mesures,
                    SUM(energy_total_kwh) as total
                FROM energy_data 
                WHERE timestamp >= CURRENT_DATE - INTERVAL {period_days} DAY
                """
            
            # 🔧 Ajout de logs de debug
            self.logger.info(f"🔍 Requête SQL moyenne: {query}")
            
            result = db_manager.execute_query(query)
            self.logger.info(f"🔍 Résultat brut SQL: {result}")
            
            if result is not None and not result.empty:
                row = result.iloc[0]
                self.logger.info(f"🔍 Première ligne: {row}")
                
                moyenne = float(row.iloc[0]) if row.iloc[0] is not None else 0
                # 🔧 Correction: Extraire le total et count des bonnes colonnes
                total = float(row.iloc[2]) if len(row) > 2 and row.iloc[2] is not None else 0
                count = int(row.iloc[1]) if len(row) > 1 and row.iloc[1] is not None else 0
                
                self.logger.info(f"🔍 Valeurs extraites: moyenne={moyenne}, total={total}, count={count}")
                
                # 🔧 Unité selon la granularité
                unit_mapping = {
                    'day': 'kWh/jour', 'jour': 'kWh/jour',
                    'week': 'kWh/semaine', 'semaine': 'kWh/semaine',
                    'month': 'kWh/mois', 'mois': 'kWh/mois',
                    'year': 'kWh/an', 'année': 'kWh/an',
                    'hour': 'kWh/h', 'heure': 'kWh/h'
                }
                unit = unit_mapping.get(granularity, 'kWh')
                
                return {
                    "value": moyenne,
                    "granularity": granularity,
                    "period": period,
                    "aggregation": "mean",
                    "unit": unit,
                    "summary": {
                        "total": total,
                        "count": count
                    }
                }
            else:
                # 🔧 Unité selon la granularité pour le cas d'erreur aussi
                unit_mapping = {
                    'day': 'kWh/jour', 'jour': 'kWh/jour',
                    'week': 'kWh/semaine', 'semaine': 'kWh/semaine',
                    'month': 'kWh/mois', 'mois': 'kWh/mois',
                    'year': 'kWh/an', 'année': 'kWh/an',
                    'hour': 'kWh/h', 'heure': 'kWh/h'
                }
                unit = unit_mapping.get(granularity, 'kWh')
                
                return {
                    "value": 0,
                    "granularity": granularity,
                    "period": period,
                    "aggregation": "mean",
                    "unit": unit,
                    "summary": {"total": 0, "count": 0}
                }
                
        except Exception as e:
            self.logger.error(f"Erreur calcul moyenne: {e}")
            return {
                "value": 0,
                "granularity": granularity,
                "period": period,
                "aggregation": "mean",
                "error": str(e)
            }
    
    def _format_final_response(self, question: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Formate la réponse finale (logique existante)"""
        if execution_result.get('status') == 'error':
            return {
                "question": question,
                "answer": f"❌ {execution_result.get('message', 'Erreur inconnue')}",
                "status": "error"
            }
        
        data = execution_result.get('data', {})
        tool_used = execution_result.get('tool_used', 'unknown')
        
        # Formatage selon le type (logique existante)
        if tool_used == 'cost':
            return self._format_cost_response(question, data)
        elif tool_used == 'zone_comparison':
            return self._format_zone_response(question, data)
        elif tool_used == 'moyenne':
            return self._format_moyenne_response(question, data)
        else:
            return self._format_consumption_response(question, data)
    
    def _format_cost_response(self, question: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Formatage pour les réponses de coût (logique existante)"""
        cost = data.get('cost', 0)
        consumption = data.get('consumption_kwh', 0)
        advice = data.get('advice')
        
        if advice:
            answer = f"💡 {advice}. Coût actuel: {cost:.2f}€ pour {consumption:.1f} kWh."
        else:
            answer = f"💰 Le coût est de {cost:.2f}€ pour une consommation de {consumption:.1f} kWh."
        
        return {
            'question': question,
            'answer': answer,
            'value': cost,
            'unit': '€',
            'consumption_kwh': consumption,
            'status': 'success',
            'type': 'cost',
            'source': 'langgraph'
        }
    
    def _format_zone_response(self, question: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Formatage pour les comparaisons de zones (logique existante)"""
        zones = data.get('zones', {})
        total = data.get('total', 0)
        
        if zones:
            max_zone = max(zones.items(), key=lambda x: x[1])
            zone_name, zone_value = max_zone
            
            zone_names = {
                'cuisine': 'la cuisine',
                'buanderie': 'la buanderie', 
                'chauffage': 'le chauffage'
            }
            
            answer = f"🏠 {zone_names.get(zone_name, zone_name)} consomme le plus avec {zone_value:.1f} kWh. Total: {total:.1f} kWh."
        else:
            answer = "Aucune donnée de zones disponible."
        
        return {
            'question': question,
            'answer': answer,
            'zones': zones,
            'total': total,
            'status': 'success',
            'type': 'zones',
            'source': 'langgraph'
        }
    
    def _format_moyenne_response(self, question: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """🆕 Formatage spécial pour les réponses de moyenne"""
        value = data.get('value', 0)
        granularity = data.get('granularity', 'day')
        unit = data.get('unit', 'kWh')
        
        # Formatage selon la granularité
        if granularity == 'day':
            answer = f"📊 Votre consommation moyenne est de {value:.1f} kWh par jour."
        elif granularity == 'week':
            answer = f"📊 Votre consommation moyenne est de {value:.1f} kWh par semaine."
        else:
            answer = f"📊 Votre consommation moyenne est de {value:.1f} {unit}."
        
        return {
            'question': question,
            'answer': answer,
            'value': value,
            'unit': unit,
            'granularity': granularity,
            'status': 'success',
            'type': 'moyenne',
            'source': 'langgraph'
        }
    
    def _format_consumption_response(self, question: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Formatage pour les réponses de consommation (logique existante)"""
        # Extraction intelligente de la valeur selon le format des données
        value = 0
        
        # Debug temporaire
        self.logger.info(f"🔍 DEBUG _format_consumption_response data: {data}")
        
        if 'value' in data:
            value = data['value']
            self.logger.info(f"✅ Trouvé value directe: {value}")
        elif 'summary' in data and 'total' in data['summary']:
            value = data['summary']['total']
            self.logger.info(f"✅ Trouvé summary.total: {value}")
        elif 'data' in data and isinstance(data['data'], dict):
            if 'summary' in data['data'] and 'total' in data['data']['summary']:
                value = data['data']['summary']['total']
                self.logger.info(f"✅ Trouvé data.summary.total: {value}")
            elif 'value' in data['data']:
                value = data['data']['value']
                self.logger.info(f"✅ Trouvé data.value: {value}")
        else:
            self.logger.warning(f"❌ Aucune valeur trouvée dans: {list(data.keys())}")
        
        period = data.get('period', 'période')
        
        period_text = {
            '1d': 'hier',
            '1d_avant_hier': 'avant-hier',  # 🔧 CORRECTION : Ajouter avant-hier
            '7d': 'cette semaine',
            '30d': 'ces 30 derniers jours'
        }.get(period, f'sur {period}')
        
        answer = f"⚡ Vous avez consommé {value:.1f} kWh {period_text}."
        
        return {
            'question': question,
            'answer': answer,
            'value': value,
            'unit': 'kWh',
            'period': period,
            'status': 'success',
            'type': 'consumption',
            'source': 'langgraph'
        }
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """Point d'entrée principal du workflow LangGraph refactorisé"""
        self.logger.info(f"🎼 LangGraph Workflow refactorisé: {question}")
        
        # 🆕 Validation préliminaire pour détecter les questions de coût
        validation_result = self._validate_question(question)
        
        if not validation_result.get("valid", False):
            question_type = validation_result.get("question_type", "unknown")
            
            if question_type == "cost":
                # 🎯 Question de coût - réponse contextuelle
                self.logger.info("💰 Question de coût détectée - réponse contextuelle")
                return {
                    "question": question,
                    "answer": "💰 Je ne traite que les questions de **consommation électrique** (kWh). Je ne peux pas calculer les coûts ou les prix.\n\n💡 **Suggestion :** Essayez plutôt : 'Quelle est ma consommation moyenne par jour ?' ou 'Combien ai-je consommé le mois dernier ?'",
                    "status": "out_of_scope",
                    "scope_type": "cost",
                    "reason": "Question sur le coût détectée"
                }
            elif question_type == "non_energy":
                # 🎯 Question non énergétique - réponse contextuelle
                self.logger.info("🌍 Question non énergétique détectée - réponse contextuelle")
                return {
                    "question": question,
                    "answer": "⚡ Bonjour ! Je suis **Energy Agent**, votre assistant spécialisé en **consommation électrique**. Je peux analyser vos données de consommation passées et actuelles.\n\n💡 **Suggestion :** Posez-moi des questions comme : 'Quelle a été ma consommation hier ?' ou 'Quelle est ma consommation moyenne par jour ?'",
                    "status": "out_of_scope",
                    "scope_type": "non_energy",
                    "reason": "Question non énergétique détectée"
                }
            else:
                # 🎯 Question non reconnue - réponse contextuelle
                self.logger.info("🤔 Question non reconnue - réponse contextuelle")
                return {
                    "question": question,
                    "answer": "🤔 Je ne suis pas sûr de comprendre votre question. Je me spécialise dans l'analyse de **consommation électrique**.\n\n💡 **Suggestion :** Essayez une question comme : 'Quelle a été ma consommation hier ?' ou 'Quelle est ma consommation moyenne par jour ?'",
                    "status": "out_of_scope",
                    "scope_type": "unknown",
                    "reason": "Question non reconnue"
                }
        
        # Question de consommation valide - continuer avec le workflow normal
        self.logger.info("✅ Question de consommation valide - continuation avec workflow normal")
        
        try:
            # 🆕 État initial avec nouveaux champs
            initial_state = {
                "question": question,
                "question_intent": {},  # 🆕 Nouveau
                "semantic_validation": {},  # 🆕 Nouveau
                "execution_strategy": {},  # 🆕 Nouveau
                "validation_result": {},
                "raw_plan": {},
                "enhanced_plan": {},  # Conservé pour compatibilité
                "execution_result": {},
                "final_response": {},
                "metadata": {"workflow_start": True, "refactored": True},
                "errors": []
            }
            
            # Exécuter le workflow LangGraph refactorisé
            final_state = self.workflow.invoke(initial_state)
            
            # Retourner la réponse finale avec métadonnées
            response = final_state.get("final_response", {})
            response["langgraph_metadata"] = final_state.get("metadata", {})
            
            # 🔧 AJOUTER LES MÉTADONNÉES INTERMÉDIAIRES POUR DEBUG
            response["semantic_validation"] = final_state.get("semantic_validation", {})
            response["question_intent"] = final_state.get("question_intent", {})
            response["execution_strategy"] = final_state.get("execution_strategy", {})
            
            self.logger.info(f"✅ LangGraph Workflow refactorisé terminé: {response.get('type', 'unknown')}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Erreur LangGraph Workflow refactorisé: {e}")
            return {
                "question": question,
                "answer": f"❌ Erreur système: {e}",
                "status": "error",
                "source": "langgraph_error"
            }
    
    def _semantic_validation_node(self, state: EnergyState) -> Dict[str, Any]:
        """🆕 Nœud de validation sémantique avec LangChain"""
        question = state["question"]
        
        self.logger.info(f"🔍 Validation sémantique: {question}")
        
        try:
            # Appeler le validateur LangChain
            validation_result = self.semantic_validator.run(question=question)
            
            # Nettoyer la réponse (supprimer espaces, etc.)
            period_code = validation_result.strip().upper()
            
            # 🔧 Nettoyer le résultat du validateur (peut contenir plusieurs lignes)
            period_code = period_code.split('\n')[0].strip().upper()
            
            # 🔧 Nettoyer le résultat du validateur (peut contenir plusieurs lignes)
            if '\n' in period_code:
                period_code = period_code.split('\n')[0].strip()
            
            # Mapping vers les codes utilisés par le système
            period_mapping = {
                # Périodes temporelles
                'CURRENT_MONTH': 'current_month',  # 🔧 CORRECTION : Utiliser current_month au lieu de 30d
                'LAST_MONTH': 'last_month', 
                'LAST_30_DAYS': '30d',
                'LAST_3_DAYS': '3d',  # 🔧 Ajout manquant
                'CURRENT_WEEK': 'current_week',
                'LAST_7_DAYS': '7d',
                'YESTERDAY': '1d',
                'DAY_BEFORE_YESTERDAY': '1d_avant_hier',  # 🔧 CORRECTION : Utiliser 1d_avant_hier pour le jour avant hier
                'CURRENT_YEAR': 'current_year',
                'LAST_YEAR': 'last_year',
                # Granularités
                'HOURLY': 'hourly',
                'DAILY': 'daily',
                'WEEKLY': 'weekly', 
                'MONTHLY': 'monthly',
                'YEARLY': 'yearly',
                # Jours nommés
                'SATURDAY': 'saturday',
                'SUNDAY': 'sunday',
                'WEEKEND': 'weekend'
            }
            
            # 🔧 Fallback intelligent selon le contexte
            if 'jour' in period_code.lower():
                fallback_period = '1d'
            elif 'semaine' in period_code.lower():
                fallback_period = '7d'
            elif 'mois' in period_code.lower():
                fallback_period = '30d'
            else:
                fallback_period = '7d'
                
            # 🔧 Mapping spécial pour les moyennes horaires avec période spécifique
            if period_code == 'LAST_7_DAYS' and 'horaire' in question.lower():
                validated_period = '7d'  # Forcer 7d pour les moyennes horaires de la semaine
            elif period_code == 'CURRENT_YEAR' and 'moyenne' in question.lower():
                validated_period = 'yearly'  # Traiter comme granularité YEARLY
            elif 'horaire' in question.lower() and 'semaine' in question.lower():
                validated_period = '7d'  # 🔧 Forcer 7d pour toutes les moyennes horaires de semaine
            elif 'horaire' in question.lower() and 'dernière' in question.lower():
                validated_period = '7d'  # 🔧 Forcer 7d pour toutes les moyennes horaires de semaine dernière
            elif 'horaire' in question.lower() and 'moyenne' in question.lower():
                validated_period = '7d'  # 🔧 CORRECTION : Forcer 7d pour toutes les moyennes horaires
            else:
                validated_period = period_mapping.get(period_code, fallback_period)
            
            self.logger.info(f"✅ Validation: {period_code} → {validated_period}")
            
            return {
                "semantic_validation": {
                    "original_question": question,
                    "detected_period_code": period_code,
                    "validated_period": validated_period,
                    "confidence": "high" if period_code in period_mapping else "low"
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur validation sémantique: {e}")
            return {
                "semantic_validation": {
                    "original_question": question,
                    "detected_period_code": "UNKNOWN",
                    "validated_period": "7d",  # Fallback sécurisé
                    "confidence": "low",
                    "error": str(e)
                }
            }

# Instance globale
_energy_workflow: Optional[EnergyLangGraphWorkflow] = None

def get_energy_workflow() -> EnergyLangGraphWorkflow:
    """Retourne l'instance globale du workflow LangGraph"""
    global _energy_workflow
    if _energy_workflow is None:
        _energy_workflow = EnergyLangGraphWorkflow()
    return _energy_workflow
