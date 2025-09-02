"""
Orchestration Layer (Bloc 4) - Energy Agent
===========================================

Orchestrateur LangGraph pour coordonner les Blocs 2 (LLM) et 3 (MCP).
Gère la validation, l'exécution, la correction d'erreurs et le formatage.

Architecture:
- langgraph_orchestrator.py: Orchestrateur principal
- plan_validator.py: Validation et correction des plans
- error_handler.py: Gestion d'erreurs et retries
- result_formatter.py: Formatage des résultats
- config/: Configuration
"""

from .langgraph_orchestrator import LangGraphOrchestrator
from .plan_validator import PlanValidator
from .error_handler import ErrorHandler
from .result_formatter import ResultFormatter

__all__ = [
    'LangGraphOrchestrator',
    'PlanValidator', 
    'ErrorHandler',
    'ResultFormatter'
]




