"""
Configuration de l'Orchestration Layer (Bloc 4)
==============================================

Paramètres de configuration pour l'orchestrateur LangGraph.
"""

from typing import Dict, List, Any

class OrchestrationConfig:
    """Configuration de l'orchestration"""
    
    # Mapping des périodes invalides vers les périodes valides
    PERIOD_MAPPING = {
        "week": "7d",
        "2h": "1d",  # Période minimale supportée
        "all": "current_year",
        "hier": "last_day",
        "aujourd'hui": "current_day",
        "ce mois": "current_month",
        "mois dernier": "last_month",
        "cette semaine": "current_week",
        "semaine dernière": "last_week"
    }
    
    # Mapping des agrégations invalides vers les agrégations valides
    AGGREGATION_MAPPING = {
        "mean": "sum",  # Sera post-traité pour les moyennes
        "count": "sum",  # Sera post-traité pour les comptages
        "average": "sum"
    }
    
    # Agrégations supportées par le système
    VALID_AGGREGATIONS = ["sum", "max", "min"]
    
    # Périodes supportées par le système
    VALID_PERIODS = [
        "1d", "7d", "30d", "month", "year",
        "current_day", "current_week", "current_month", "current_year",
        "last_day", "last_week", "last_month", "last_year"
    ]
    
    # Post-processing pour les moyennes
    POST_PROCESSING_MAPPING = {
        "mean": "divide_by_days",
        "count": "divide_by_period",
        "average": "divide_by_days"
    }
    
    # Règles métier pour la correction automatique
    BUSINESS_RULES = {
        "moyenne par jour": {
            "period": "current_year",
            "aggregation": "sum",
            "post_processing": "divide_by_days"
        },
        "consommation quotidienne": {
            "period": "current_year", 
            "aggregation": "sum",
            "post_processing": "divide_by_days"
        },
        "moyenne journalière": {
            "period": "current_year",
            "aggregation": "sum", 
            "post_processing": "divide_by_days"
        },
        "cette semaine": {
            "period": "current_week",
            "aggregation": "sum",
            "post_processing": None
        },
        "semaine": {
            "period": "current_week",
            "aggregation": "sum",
            "post_processing": None
        },
        "consommation totale": {
            "period": "current_year",
            "aggregation": "sum",
            "post_processing": None
        },
        "consommation d'hier": {
            "period": "last_day",
            "aggregation": "sum",
            "post_processing": None
        },
        "hier": {
            "period": "last_day",
            "aggregation": "sum",
            "post_processing": None
        }
    }
    
    # Configuration des retries
    RETRY_CONFIG = {
        "max_retries": 3,
        "retry_delay": 1.0,  # secondes
        "backoff_factor": 2.0
    }
    
    # Configuration des timeouts
    TIMEOUT_CONFIG = {
        "plan_generation": 10.0,  # secondes
        "step_execution": 5.0,    # secondes
        "total_execution": 30.0   # secondes
    }
    
    # Configuration du formatage
    FORMATTING_CONFIG = {
        "decimal_places": 2,
        "currency_symbol": "€",
        "energy_unit": "kWh",
        "power_unit": "kW"
    }
    
    @classmethod
    def get_period_mapping(cls, period: str) -> str:
        """Retourne la période corrigée"""
        return cls.PERIOD_MAPPING.get(period, period)
    
    @classmethod
    def get_aggregation_mapping(cls, aggregation: str) -> str:
        """Retourne l'agrégation corrigée"""
        return cls.AGGREGATION_MAPPING.get(aggregation, aggregation)
    
    @classmethod
    def get_post_processing(cls, original_aggregation: str) -> str:
        """Retourne le post-processing nécessaire"""
        return cls.POST_PROCESSING_MAPPING.get(original_aggregation, None)
    
    @classmethod
    def is_valid_period(cls, period: str) -> bool:
        """Vérifie si une période est valide"""
        return period in cls.VALID_PERIODS
    
    @classmethod
    def is_valid_aggregation(cls, aggregation: str) -> bool:
        """Vérifie si une agrégation est valide"""
        return aggregation in cls.VALID_AGGREGATIONS
    
    @classmethod
    def get_business_rule(cls, question: str) -> Dict[str, Any]:
        """Retourne la règle métier applicable"""
        question_lower = question.lower()
        for key, rule in cls.BUSINESS_RULES.items():
            if key in question_lower:
                return rule
        return {}
