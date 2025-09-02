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

import json
from typing import Dict, Any
from datetime import datetime, timedelta

class PlanGeneratorPrompt:
    """Générateur de prompts JSON stricts pour le LLM"""
    
    # Outils MCP disponibles (correspondent exactement aux outils du BLOC 3)
    AVAILABLE_TOOLS = {
        'aggregate': {
            'description': 'Agréger les données énergétiques par période',
            'parameters': {
                'period': 'Période (ex: "1d", "7d", "30d", "month", "year", "current_day", "current_week", "current_month", "current_year", "last_day", "last_week", "last_month", "last_year")',
                'aggregation': 'Type d\'agrégation (ex: "sum", "mean", "max", "min")',
                'filters': 'Filtres optionnels'
            }
        },
        'forecast': {
            'description': 'Générer des prévisions énergétiques',
            'parameters': {
                'horizon': 'Horizon de prévision (ex: "7d", "30d", "90d")',
                'model': 'Modèle à utiliser (ex: "simple", "trend", "seasonal")'
            }
        },
        'peak': {
            'description': 'Détecter les pics de consommation',
            'parameters': {
                'threshold': 'Seuil de détection (ex: 2.0)',
                'period': 'Période d\'analyse (ex: "7d", "30d")'
            }
        },
        'cost': {
            'description': 'Estimer les coûts énergétiques',
            'parameters': {
                'tariff': 'Tarif par kWh (ex: 0.20)',
                'period': 'Période de calcul (ex: "7d", "30d", "month")'
            }
        },
        'anomaly': {
            'description': 'Détecter les anomalies de consommation',
            'parameters': {
                'threshold': 'Seuil de détection (nombre décimal, ex: 2.0)',
                'method': 'Méthode (ex: "zscore", "iqr", "threshold")'
            }
        },
        'plot': {
            'description': 'Créer des visualisations',
            'parameters': {
                'chart_type': 'Type de graphique (ex: "consumption_overview", "cost_analysis", "anomaly_dashboard", "forecast_dashboard", "time_analysis", "sub_metering")',
                'period': 'Période pour le graphique (optionnel)',
                'tariff': 'Tarif pour les graphiques de coûts (optionnel)',
                'threshold': 'Seuil pour les graphiques d\'anomalies (optionnel)'
            }
        }
    }
    
    @classmethod
    def _get_dynamic_dates(cls) -> Dict[str, str]:
        """Calcule les dates dynamiques basées sur la date réelle"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        last_week_start = today - timedelta(days=7)
        last_month_start = today - timedelta(days=30)
        
        return {
            "today": today.strftime("%d/%m/%Y"),
            "yesterday": yesterday.strftime("%d/%m/%Y"),
            "last_week_start": last_week_start.strftime("%d/%m/%Y"),
            "last_month_start": last_month_start.strftime("%d/%m/%Y"),
            "current_month": today.strftime("%B %Y"),
            "last_month": yesterday.replace(day=1).strftime("%B %Y")
        }
    
    @classmethod
    def _get_db_period(cls) -> Dict[str, str]:
        """Récupère la période depuis DuckDB"""
        try:
            from mcp_server.core.database_manager import get_database_manager
            db_manager = get_database_manager()
            
            query = "SELECT MIN(timestamp), MAX(timestamp) FROM energy_data"
            result = db_manager.execute_query(query)
            
            if result is not None and not result.empty:
                start_date = result.iloc[0]['MIN(timestamp)'].strftime('%d/%m/%Y')
                end_date = result.iloc[0]['MAX(timestamp)'].strftime('%d/%m/%Y')
                
                return {
                    "start": start_date,
                    "end": end_date
                }
        except Exception as e:
            # Fallback en cas d'erreur
            return {
                "start": "16/12/2023",
                "end": "30/08/2025"
            }
        
        # Fallback par défaut
        return {
            "start": "16/12/2023",
            "end": "30/08/2025"
        }
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Retourne le prompt système principal avec dates dynamiques"""
        
        # Calculer les dates dynamiques
        dates = cls._get_dynamic_dates()
        db_period = cls._get_db_period()
        
        return f"""Tu es un planificateur expert pour l'analyse énergétique. Tu génères des plans JSON structurés pour répondre aux questions des utilisateurs.

CONTEXTE DES DONNÉES :
- Période : {db_period['start']} → {db_period['end']}
- Granularité : Agrégation 2h
- Données : Consommation électrique en kWh

LOGIQUE TEMPORELLE DYNAMIQUE (basée sur la date réelle {dates['today']}) :
- "aujourd'hui" = {dates['today']} → utiliser "current_day"
- "hier" = {dates['yesterday']} → utiliser "last_day"
- "cette semaine" = {dates['last_week_start']} → {dates['today']} → utiliser "current_week"
- "ce mois" = {dates['current_month']} → utiliser "current_month"
- "cette année" = {dates['current_month']} → utiliser "current_year"
- "mois dernier" = {dates['last_month']} → utiliser "last_month"

HEURISTIQUES INTELLIGENTES :
- "moyenne par jour" → utiliser "current_year" (année en cours)
- "consommation quotidienne" → utiliser "current_year"
- "par jour" → utiliser "current_year"

RÈGLES STRICTES :
1. Tu génères UNIQUEMENT des plans JSON valides
2. Tu n'exécutes JAMAIS d'outils directement
3. Tu utilises SEULEMENT les outils disponibles
4. Tu respectes les dépendances entre étapes
5. Tu estimes la complexité et la durée
6. Tu respectes la logique temporelle dynamique ci-dessus
7. Tu utilises TOUJOURS des périodes relatives ("1d", "7d", "month") et JAMAIS de dates fixes

OUTILS DISPONIBLES :
{json.dumps(cls.AVAILABLE_TOOLS, indent=2, ensure_ascii=False)}

STRUCTURE JSON OBLIGATOIRE :
{{
    "metadata": {{
        "plan_id": "plan_XXX",
        "question_type": "history|forecast|comparison|costs|anomalies",
        "complexity": "simple|medium|complex",
        "estimated_duration": <secondes>
    }},
    "steps": [
        {{
            "step_id": <numéro>,
            "tool_name": "<nom_outil>",
            "description": "<description_claire>",
            "parameters": {{<paramètres>}},
            "depends_on": [<étapes_préalables>]
        }}
    ],
    "summary": "<résumé_du_plan>"
}}

EXEMPLES DE PLANS VALIDES :
1. Question simple : "Quelle est ma consommation des 7 derniers jours ?"
   → Plan simple avec 1 étape (aggregate avec period: "7d")

2. Question complexe : "Prévois ma consommation pour les 30 prochains jours"
   → Plan complexe avec 3 étapes (aggregate → forecast → plot)

IMPORTANT : 
- Réponds UNIQUEMENT avec le JSON du plan, sans commentaires supplémentaires
- Utilise TOUJOURS des périodes relatives (1d, 7d, month, year) et JAMAIS de dates fixes
- Les dates dynamiques ci-dessus sont basées sur la date réelle d'exécution : {dates['today']}"""

    @classmethod
    def get_user_prompt(cls, question: str) -> str:
        """Retourne le prompt utilisateur pour une question donnée"""
        return f"""Question utilisateur : "{question}"

CONTEXTE MÉTIER IMPORTANT :
- Pour les moyennes de consommation : utiliser "sum" + post_processing
- Pour les moyennes de puissance : utiliser "mean" directement
- Pour les coûts : inclure le tarif (0.20€/kWh par défaut)
- Pour les comparaisons : utiliser des périodes cohérentes
- Pour les prévisions : vérifier que le modèle est supporté

Génère un plan JSON pour répondre à cette question.
Utilise les outils appropriés et respecte les dépendances.
Estime la complexité et la durée d'exécution.
Utilise TOUJOURS des périodes relatives et JAMAIS de dates fixes.

Réponds UNIQUEMENT avec le JSON du plan :"""

    @classmethod
    def get_validation_prompt(cls) -> str:
        """Retourne le prompt de validation"""
        return """Valide ce plan JSON généré :

1. Structure JSON valide ?
2. Outils utilisés existent ?
3. Dépendances cohérentes ?
4. Paramètres corrects ?
5. Complexité estimée réaliste ?
6. Utilise-t-il des périodes relatives (pas de dates fixes) ?

Si le plan est invalide, explique pourquoi et propose une correction."""

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
