"""
Validateur de Plans - Orchestration Layer (Bloc 4)
=================================================

Valide et corrige automatiquement les plans générés par le Bloc 2 (LLM).
Applique les règles métier et les mappings de correction.
"""

import logging
from typing import Dict, List, Any, Optional
from .config.orchestration_config import OrchestrationConfig

class PlanValidator:
    """Validateur et correcteur de plans"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = OrchestrationConfig()
    
    def validate_and_correct_plan(self, plan: Dict[str, Any], question: str) -> Dict[str, Any]:
        """
        Valide et corrige un plan complet
        
        Args:
            plan: Plan JSON généré par le LLM
            question: Question utilisateur originale
            
        Returns:
            Plan corrigé avec métadonnées de correction
        """
        try:
            # Validation de la question
            question_validation = self._validate_question(question)
            if not question_validation['valid']:
                return {
                    'error': True,
                    'error_type': 'invalid_question',
                    'error_message': question_validation['message'],
                    'corrections': [f"Question invalide: {question_validation['message']}"],
                    'original_plan': plan
                }
            
            corrected_plan = plan.copy()
            corrections = []
            
            # Vérifier les règles métier spécifiques
            business_rule = self.config.get_business_rule(question)
            if business_rule:
                corrected_plan = self._apply_business_rule(corrected_plan, business_rule)
                corrections.append(f"Règle métier appliquée: {business_rule}")
            
            # Valider et corriger chaque étape
            if 'steps' in corrected_plan:
                for i, step in enumerate(corrected_plan['steps']):
                    corrected_step, step_corrections = self._validate_and_correct_step(step)
                    corrected_plan['steps'][i] = corrected_step
                    corrections.extend(step_corrections)
            
            # Ajouter les métadonnées de correction
            corrected_plan['corrections'] = corrections
            corrected_plan['original_plan'] = plan
            
            self.logger.info(f"Plan corrigé avec {len(corrections)} corrections")
            return corrected_plan
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation du plan: {e}")
            return plan
    
    def _validate_and_correct_step(self, step: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
        """
        Valide et corrige une étape individuelle
        
        Returns:
            (step_corrigé, liste_des_corrections)
        """
        corrected_step = step.copy()
        corrections = []
        
        if 'parameters' not in corrected_step:
            return corrected_step, corrections
        
        params = corrected_step['parameters']
        
        # Correction de la période
        if 'period' in params:
            original_period = params['period']
            corrected_period = self.config.get_period_mapping(original_period)
            
            if not self.config.is_valid_period(corrected_period):
                corrected_period = "7d"  # Fallback sécurisé
                corrections.append(f"Période invalide '{original_period}' → '7d'")
            elif original_period != corrected_period:
                corrections.append(f"Période mappée '{original_period}' → '{corrected_period}'")
            
            params['period'] = corrected_period
        
        # Correction de l'agrégation
        if 'aggregation' in params:
            original_aggregation = params['aggregation']
            corrected_aggregation = self.config.get_aggregation_mapping(original_aggregation)
            
            if not self.config.is_valid_aggregation(corrected_aggregation):
                corrected_aggregation = "sum"  # Fallback sécurisé
                corrections.append(f"Agrégation invalide '{original_aggregation}' → 'sum'")
            elif original_aggregation != corrected_aggregation:
                corrections.append(f"Agrégation mappée '{original_aggregation}' → '{corrected_aggregation}'")
            
            params['aggregation'] = corrected_aggregation
            
            # Ajouter le post-processing si nécessaire
            post_processing = self.config.get_post_processing(original_aggregation)
            if post_processing:
                params['post_processing'] = post_processing
                corrections.append(f"Post-processing ajouté: {post_processing}")
        
        corrected_step['parameters'] = params
        return corrected_step, corrections
    
    def _apply_business_rule(self, plan: Dict[str, Any], business_rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applique une règle métier spécifique au plan
        
        Args:
            plan: Plan à modifier
            business_rule: Règle métier à appliquer
            
        Returns:
            Plan modifié selon la règle métier
        """
        corrected_plan = plan.copy()
        
        # Si c'est une question de moyenne par jour, créer un plan en 2 étapes
        if 'post_processing' in business_rule and business_rule['post_processing'] == 'divide_by_days':
            corrected_plan['steps'] = [
                {
                    'step_id': 1,
                    'tool_name': 'aggregate',
                    'description': 'Calculer la consommation totale',
                    'parameters': {
                        'period': business_rule['period'],
                        'aggregation': business_rule['aggregation']
                    },
                    'depends_on': []
                },
                {
                    'step_id': 2,
                    'tool_name': 'post_process',
                    'description': 'Calculer la moyenne par jour',
                    'parameters': {
                        'operation': business_rule['post_processing'],
                        'depends_on_step': 1
                    },
                    'depends_on': [1]
                }
            ]
        
        return corrected_plan
    
    def validate_plan_structure(self, plan: Dict[str, Any]) -> bool:
        """
        Valide la structure générale du plan
        
        Returns:
            True si le plan est valide, False sinon
        """
        required_fields = ['metadata', 'steps', 'summary']
        
        for field in required_fields:
            if field not in plan:
                self.logger.error(f"Champ requis manquant: {field}")
                return False
        
        if not isinstance(plan['steps'], list) or len(plan['steps']) == 0:
            self.logger.error("Le plan doit contenir au moins une étape")
            return False
        
        return True
    
    def _validate_question(self, question: str) -> Dict[str, Any]:
        """
        Valide une question utilisateur
        
        Args:
            question: Question à valider
            
        Returns:
            Dict avec 'valid' (bool) et 'message' (str)
        """
        # Question vide
        if not question or question.strip() == "":
            return {
                'valid': False,
                'message': 'Question vide ou non fournie'
            }
        
        # Question trop courte
        if len(question.strip()) < 3:
            return {
                'valid': False,
                'message': 'Question trop courte (minimum 3 caractères)'
            }
        
        # Question trop longue
        if len(question) > 1000:
            return {
                'valid': False,
                'message': 'Question trop longue (maximum 1000 caractères)'
            }
        
        # Caractères spéciaux suspects
        special_chars = ['@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '[', ']', '{', '}', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '?', '/']
        special_char_count = sum(1 for char in question if char in special_chars)
        
        if special_char_count > len(question) * 0.3:  # Plus de 30% de caractères spéciaux
            return {
                'valid': False,
                'message': 'Question contient trop de caractères spéciaux'
            }
        
        # Question ne contient pas de mots-clés énergétiques
        energy_keywords = ['consommation', 'électricité', 'kwh', 'énergie', 'puissance', 'coût', 'prix', 'euro', '€', 'moyenne', 'jour', 'semaine', 'mois', 'année', 'hier', 'aujourd\'hui', 'demain']
        question_lower = question.lower()
        
        if not any(keyword in question_lower for keyword in energy_keywords):
            return {
                'valid': False,
                'message': 'Question non liée à l\'énergie'
            }
        
        return {
            'valid': True,
            'message': 'Question valide'
        }
