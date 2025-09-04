#!/usr/bin/env python3
"""
📋 SCHÉMA PYDANTIC AGENTIQUE - VALIDATION MINIMALE
=================================================

Validation ultra-simple pour architecture agentique.
L'orchestrateur gère la complexité métier.

Principe : Valider la structure, pas le contenu.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class ToolStep(BaseModel):
    """Étape d'outil - Validation minimale"""
    
    step_id: int = Field(..., description="ID de l'étape")
    tool_name: str = Field(..., description="Nom de l'outil")
    description: str = Field(..., description="Description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Paramètres")
    depends_on: Optional[List[int]] = Field(default=None, description="Dépendances")
    
    @validator('tool_name')
    def validate_tool_name_basic(cls, v):
        """Validation basique - L'orchestrateur validera le contenu"""
        if not v or not isinstance(v, str):
            raise ValueError("Nom d'outil requis")
        return v.strip()

    @validator('step_id')
    def validate_step_id(cls, v):
        """Validation de l'ID"""
        if v <= 0:
            raise ValueError("ID d'étape doit être positif")
        return v

class PlanMetadata(BaseModel):
    """Métadonnées optionnelles - L'orchestrateur les enrichira"""
    
    plan_id: Optional[str] = Field(None, description="ID du plan")
    complexity: Optional[str] = Field(None, description="Complexité")

class LLMPlan(BaseModel):
    """Plan JSON agentique - Validation structurelle uniquement"""
    
    steps: List[ToolStep] = Field(..., description="Étapes du plan")
    summary: str = Field(..., description="Résumé")
    metadata: Optional[PlanMetadata] = Field(None, description="Métadonnées optionnelles")
    
    @validator('steps')
    def validate_steps_basic(cls, v):
        """Validation basique des étapes"""
        if not v:
            raise ValueError("Au moins une étape requise")
        
        # Vérifier IDs uniques
        step_ids = [step.step_id for step in v]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("IDs d'étapes doivent être uniques")
        
        return v
    
    @validator('summary')
    def validate_summary(cls, v):
        """Validation du résumé"""
        if not v or not v.strip():
            raise ValueError("Résumé requis")
        return v.strip()

# Exemple simple pour les tests
EXAMPLE_PLAN = {
    "steps": [
        {
            "step_id": 1,
            "tool_name": "aggregate",
            "description": "Agrégation des données",
            "parameters": {"period": "week"}
        }
    ],
    "summary": "Plan simple d'agrégation"
}