"""
Gestionnaire d'Erreurs - Orchestration Layer (Bloc 4)
===================================================

Gère les erreurs d'exécution, les retries et les fallbacks automatiques.
Assure la robustesse de l'orchestration.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from .config.orchestration_config import OrchestrationConfig

class ErrorHandler:
    """Gestionnaire d'erreurs avec retry et fallback"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = OrchestrationConfig()
    
    def execute_with_retry(self, 
                          func: Callable, 
                          *args, 
                          max_retries: Optional[int] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        Exécute une fonction avec retry automatique
        
        Args:
            func: Fonction à exécuter
            *args: Arguments de la fonction
            max_retries: Nombre maximum de retries (défaut: config)
            **kwargs: Arguments nommés de la fonction
            
        Returns:
            Résultat de l'exécution avec métadonnées
        """
        if max_retries is None:
            max_retries = self.config.RETRY_CONFIG['max_retries']
        
        retry_delay = self.config.RETRY_CONFIG['retry_delay']
        backoff_factor = self.config.RETRY_CONFIG['backoff_factor']
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                return {
                    'status': 'success',
                    'result': result,
                    'attempts': attempt + 1,
                    'execution_time': execution_time,
                    'error': None
                }
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Tentative {attempt + 1} échouée: {e}")
                
                if attempt < max_retries:
                    # Calculer le délai avec backoff exponentiel
                    delay = retry_delay * (backoff_factor ** attempt)
                    self.logger.info(f"Retry dans {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Échec après {max_retries + 1} tentatives")
        
        return {
            'status': 'error',
            'result': None,
            'attempts': max_retries + 1,
            'execution_time': 0,
            'error': str(last_error)
        }
    
    def handle_step_error(self, 
                         step: Dict[str, Any], 
                         error: Exception,
                         step_results: Dict[int, Any]) -> Dict[str, Any]:
        """
        Gère une erreur d'étape avec fallback
        
        Args:
            step: Étape qui a échoué
            error: Erreur survenue
            step_results: Résultats des étapes précédentes
            
        Returns:
            Résultat de fallback ou erreur
        """
        step_id = step.get('step_id', 'unknown')
        tool_name = step.get('tool_name', 'unknown')
        
        self.logger.error(f"Erreur dans l'étape {step_id} ({tool_name}): {error}")
        
        # Fallback pour les agrégations
        if tool_name == 'aggregate':
            return self._handle_aggregate_fallback(step, error, step_results)
        
        # Fallback pour les post-processing
        elif tool_name == 'post_process':
            return self._handle_post_process_fallback(step, error, step_results)
        
        # Fallback générique
        else:
            return self._handle_generic_fallback(step, error, step_results)
    
    def _handle_aggregate_fallback(self, 
                                  step: Dict[str, Any], 
                                  error: Exception,
                                  step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Fallback pour les erreurs d'agrégation"""
        params = step.get('parameters', {})
        
        # Si l'agrégation échoue, essayer avec des paramètres simplifiés
        fallback_params = {
            'period': '7d',  # Période sécurisée
            'aggregation': 'sum',  # Agrégation sécurisée
            'filters': None
        }
        
        self.logger.info(f"Fallback agrégation: {params} → {fallback_params}")
        
        return {
            'status': 'fallback',
            'tool': 'aggregate',
            'parameters': fallback_params,
            'original_parameters': params,
            'error': str(error),
            'fallback_reason': 'Paramètres simplifiés'
        }
    
    def _handle_post_process_fallback(self, 
                                     step: Dict[str, Any], 
                                     error: Exception,
                                     step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Fallback pour les erreurs de post-processing"""
        params = step.get('parameters', {})
        depends_on_step = params.get('depends_on_step', 1)
        
        # Si le post-processing échoue, retourner le résultat brut
        if depends_on_step in step_results:
            original_result = step_results[depends_on_step]
            
            self.logger.info(f"Fallback post-processing: résultat brut utilisé")
            
            return {
                'status': 'fallback',
                'tool': 'post_process',
                'parameters': params,
                'result': original_result,
                'error': str(error),
                'fallback_reason': 'Résultat brut sans post-processing'
            }
        
        return {
            'status': 'error',
            'tool': 'post_process',
            'parameters': params,
            'error': str(error),
            'fallback_reason': 'Pas de résultat source disponible'
        }
    
    def _handle_generic_fallback(self, 
                                step: Dict[str, Any], 
                                error: Exception,
                                step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Fallback générique pour les autres outils"""
        return {
            'status': 'error',
            'tool': step.get('tool_name', 'unknown'),
            'parameters': step.get('parameters', {}),
            'error': str(error),
            'fallback_reason': 'Pas de fallback disponible'
        }
    
    def validate_dependencies(self, steps: List[Dict[str, Any]]) -> bool:
        """
        Valide les dépendances entre étapes
        
        Args:
            steps: Liste des étapes du plan
            
        Returns:
            True si les dépendances sont valides
        """
        step_ids = {step['step_id'] for step in steps}
        
        for step in steps:
            depends_on = step.get('depends_on', [])
            
            for dep_id in depends_on:
                if dep_id not in step_ids:
                    self.logger.error(f"Étape {step['step_id']} dépend de {dep_id} qui n'existe pas")
                    return False
                
                # Vérifier qu'il n'y a pas de dépendance circulaire
                if self._has_circular_dependency(step['step_id'], dep_id, steps):
                    self.logger.error(f"Dépendance circulaire détectée: {step['step_id']} ↔ {dep_id}")
                    return False
        
        return True
    
    def _has_circular_dependency(self, 
                                step_id: int, 
                                dep_id: int, 
                                steps: List[Dict[str, Any]]) -> bool:
        """Vérifie s'il y a une dépendance circulaire"""
        # Implémentation simplifiée - vérifier si dep_id dépend de step_id
        for step in steps:
            if step['step_id'] == dep_id:
                depends_on = step.get('depends_on', [])
                if step_id in depends_on:
                    return True
        return False
    
    def get_execution_order(self, steps: List[Dict[str, Any]]) -> List[int]:
        """
        Détermine l'ordre d'exécution des étapes
        
        Returns:
            Liste des IDs d'étapes dans l'ordre d'exécution
        """
        # Tri topologique simple
        execution_order = []
        completed = set()
        
        while len(execution_order) < len(steps):
            for step in steps:
                step_id = step['step_id']
                if step_id in completed:
                    continue
                
                depends_on = step.get('depends_on', [])
                if all(dep_id in completed for dep_id in depends_on):
                    execution_order.append(step_id)
                    completed.add(step_id)
            
            # Éviter les boucles infinies
            if len(execution_order) == len(execution_order):
                break
        
        return execution_order




