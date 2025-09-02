#!/usr/bin/env python3
"""
📋 SCHÉMA PYDANTIC - PLANS JSON LLM
===================================

Schéma de validation pour les plans JSON générés par le LLM.
Garantit la cohérence et la validité des plans avant exécution.

Critères d'acceptation :
- Plan JSON valide (schéma Pydantic)
- Structure standardisée
- Validation automatique
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ToolStep(BaseModel):
    """Étape d'outil dans le plan"""
    
    step_id: int = Field(..., description="Identifiant unique de l'étape")
    tool_name: str = Field(..., description="Nom de l'outil MCP à utiliser")
    description: str = Field(..., description="Description de l'action")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Paramètres de l'outil")
    depends_on: Optional[List[int]] = Field(default=None, description="Étapes préalables")
    
    @validator('tool_name')
    def validate_tool_name(cls, v):
        """Valide le nom de l'outil"""
        valid_tools = [
            'query_energy_data',
            'calculate_statistics', 
            'generate_forecast',
            'create_visualization',
            'estimate_costs',
            'detect_anomalies',
            'compare_periods'
        ]
        if v not in valid_tools:
            raise ValueError(f"Outil invalide: {v}. Outils valides: {valid_tools}")
        return v

class PlanMetadata(BaseModel):
    """Métadonnées du plan"""
    
    plan_id: str = Field(..., description="Identifiant unique du plan")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")
    question_type: str = Field(..., description="Type de question (history, forecast, comparison, etc.)")
    complexity: Literal["simple", "medium", "complex"] = Field(..., description="Complexité du plan")
    estimated_duration: Optional[int] = Field(None, description="Durée estimée en secondes")

class LLMPlan(BaseModel):
    """Plan JSON complet généré par le LLM"""
    
    metadata: PlanMetadata = Field(..., description="Métadonnées du plan")
    steps: List[ToolStep] = Field(..., description="Liste des étapes d'outils")
    summary: str = Field(..., description="Résumé du plan")
    
    @validator('steps')
    def validate_steps(cls, v):
        """Valide la cohérence des étapes"""
        if not v:
            raise ValueError("Le plan doit contenir au moins une étape")
        
        # Vérifier les dépendances
        step_ids = [step.step_id for step in v]
        
        # Vérifier les IDs dupliqués
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Les IDs d'étapes doivent être uniques")
        
        for step in v:
            if step.depends_on:
                for dep_id in step.depends_on:
                    if dep_id not in step_ids:
                        raise ValueError(f"Étape {step.step_id} dépend de l'étape {dep_id} qui n'existe pas")
        
        # Vérifier les dépendances circulaires
        if cls._has_circular_dependencies(v):
            raise ValueError("Dépendances circulaires détectées")
        
        return v
    
    @staticmethod
    def _has_circular_dependencies(steps):
        """Vérifie s'il y a des dépendances circulaires"""
        def has_cycle(node, visited, rec_stack, graph):
            visited[node] = True
            rec_stack[node] = True
            
            for neighbor in graph.get(node, []):
                if not visited[neighbor]:
                    if has_cycle(neighbor, visited, rec_stack, graph):
                        return True
                elif rec_stack[neighbor]:
                    return True
            
            rec_stack[node] = False
            return False
        
        # Construire le graphe de dépendances
        graph = {}
        for step in steps:
            if step.depends_on:
                graph[step.step_id] = step.depends_on
            else:
                graph[step.step_id] = []
        
        # Vérifier les cycles
        visited = {step.step_id: False for step in steps}
        rec_stack = {step.step_id: False for step in steps}
        
        for step in steps:
            if not visited[step.step_id]:
                if has_cycle(step.step_id, visited, rec_stack, graph):
                    return True
        
        return False
    
    def get_execution_order(self) -> List[int]:
        """Retourne l'ordre d'exécution des étapes"""
        # Tri topologique simple basé sur les dépendances
        execution_order = []
        completed = set()
        
        while len(execution_order) < len(self.steps):
            for step in self.steps:
                if step.step_id in completed:
                    continue
                
                # Vérifier si toutes les dépendances sont complétées
                if not step.depends_on or all(dep in completed for dep in step.depends_on):
                    execution_order.append(step.step_id)
                    completed.add(step.step_id)
            
            # Éviter les boucles infinies
            if len(execution_order) == len(completed):
                break
        
        return execution_order

# Exemples de plans valides pour les tests
EXAMPLE_SIMPLE_PLAN = {
    "metadata": {
        "plan_id": "plan_001",
        "question_type": "history",
        "complexity": "simple",
        "estimated_duration": 2
    },
    "steps": [
        {
            "step_id": 1,
            "tool_name": "query_energy_data",
            "description": "Récupérer les données de consommation des 7 derniers jours",
            "parameters": {
                "period": "7d",
                "aggregation": "2h"
            }
        }
    ],
    "summary": "Plan simple pour récupérer l'historique de consommation"
}

EXAMPLE_COMPLEX_PLAN = {
    "metadata": {
        "plan_id": "plan_002", 
        "question_type": "forecast",
        "complexity": "complex",
        "estimated_duration": 10
    },
    "steps": [
        {
            "step_id": 1,
            "tool_name": "query_energy_data",
            "description": "Récupérer l'historique complet pour l'entraînement",
            "parameters": {
                "period": "90d",
                "aggregation": "2h"
            }
        },
        {
            "step_id": 2,
            "tool_name": "generate_forecast",
            "description": "Générer les prévisions pour les 7 prochains jours",
            "parameters": {
                "horizon": "7d",
                "model": "prophet"
            },
            "depends_on": [1]
        },
        {
            "step_id": 3,
            "tool_name": "create_visualization",
            "description": "Créer un graphique des prévisions",
            "parameters": {
                "chart_type": "line",
                "include_history": True
            },
            "depends_on": [1, 2]
        }
    ],
    "summary": "Plan complexe pour générer et visualiser des prévisions"
}
