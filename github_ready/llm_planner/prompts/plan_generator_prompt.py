#!/usr/bin/env python3
"""
🎯 PROMPT JSON STRICT - GÉNÉRATEUR DE PLANS LLM
===============================================

Template de prompt strict pour générer des plans JSON valides.
Garantit la cohérence et la qualité des plans générés par le LLM.

Critères d'acceptation :
- Prompt JSON strict défini
- Instructions claires
- Exemples de plans valides
- Dates dynamiques basées sur la date réelle
"""

from typing import Dict, Any

class PlanGeneratorPrompt:
    """Générateur de prompts JSON stricts pour le LLM"""
    
    # Outils disponibles - Compatible avec les nouvelles capacités génériques
    AVAILABLE_TOOLS = [
        "aggregate",           # → execute_temporal_aggregation (consommation par période)
        "cost",               # → execute_cost_calculation (coûts et économies)
        "zone_comparison",    # → execute_zone_comparison (sous-compteurs)
        "forecast",           # → capacité future
        "plot"                # → visualisation
    ]
    

    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Retourne le prompt système agentique minimal"""
        return f"""RÔLE: Traducteur question → JSON

OUTILS: {', '.join(cls.AVAILABLE_TOOLS)}

STRUCTURE:
{{
  "steps": [{{"step_id": 1, "tool_name": "outil", "parameters": {{}}, "description": "action"}}],
  "summary": "résumé"
}}

RÈGLE: JSON uniquement."""

    @classmethod
    def get_user_prompt(cls, question: str) -> str:
        """Retourne le prompt utilisateur pour une question donnée"""
        return f'"{question}" → JSON:'

    @classmethod
    def get_validation_prompt(cls) -> str:
        """Retourne le prompt de validation"""
        return "JSON valide?"

    @classmethod
    def get_example_plans(cls) -> Dict[str, Any]:
        """Retourne des exemples de plans pour l'apprentissage"""
        return {
            "simple_history": {
                "metadata": {
                    "plan_id": "plan_001",
                    "question_type": "history",
                    "complexity": "simple",
                    "estimated_duration": 2
                },
                "steps": [
                    {
                        "step_id": 1,
                        "tool_name": "aggregate",
                        "description": "Récupérer les données de consommation des 7 derniers jours",
                        "parameters": {
                            "period": "7d",
                            "aggregation": "sum"
                        }
                    }
                ],
                "summary": "Plan simple pour récupérer l'historique de consommation"
            },
            "complex_forecast": {
                "metadata": {
                    "plan_id": "plan_002",
                    "question_type": "forecast",
                    "complexity": "complex",
                    "estimated_duration": 10
                },
                "steps": [
                    {
                        "step_id": 1,
                        "tool_name": "aggregate",
                        "description": "Récupérer l'historique complet pour l'entraînement",
                        "parameters": {
                            "period": "90d",
                            "aggregation": "sum"
                        }
                    },
                    {
                        "step_id": 2,
                        "tool_name": "forecast",
                        "description": "Générer les prévisions pour les 7 prochains jours",
                        "parameters": {
                            "horizon": "7d",
                            "model": "simple"
                        },
                        "depends_on": [1]
                    },
                    {
                        "step_id": 3,
                        "tool_name": "plot",
                        "description": "Créer un graphique des prévisions",
                        "parameters": {
                            "chart_type": "forecast_dashboard",
                            "period": "7d"
                        },
                        "depends_on": [1, 2]
                    }
                ],
                "summary": "Plan complexe pour générer et visualiser des prévisions"
            }
        }

# Fonction utilitaire pour formater les prompts
def format_plan_prompt(question: str) -> str:
    """Formate le prompt complet pour une question avec dates dynamiques"""
    system_prompt = PlanGeneratorPrompt.get_system_prompt()
    user_prompt = PlanGeneratorPrompt.get_user_prompt(question)
    
    return f"{system_prompt}\n\n{user_prompt}"
