#!/usr/bin/env python3
"""
🧠 LLM PLANNER - INTELLIGENCE LAYER
==================================

Couche d'intelligence pour la génération de plans JSON.
Utilise Gemini 1.5 Flash pour planifier les opérations.

Critères d'acceptation :
- Plan JSON strict défini
- Plan JSON valide (schéma Pydantic)
- Cache actif
- Aucune exécution côté LLM
"""

from .core.gemini_client import get_gemini_client, GeminiClient
from .models.plan_schema import LLMPlan, ToolStep, PlanMetadata
from .prompts.plan_generator_prompt import PlanGeneratorPrompt, format_plan_prompt

__version__ = "1.0.0"
__author__ = "Energy Agent Team"

# Exports principaux
__all__ = [
    'get_gemini_client',
    'GeminiClient', 
    'LLMPlan',
    'ToolStep',
    'PlanMetadata',
    'PlanGeneratorPrompt',
    'format_plan_prompt'
]














