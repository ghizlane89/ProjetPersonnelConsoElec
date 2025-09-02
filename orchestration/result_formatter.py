"""
Formateur de Résultats - Orchestration Layer (Bloc 4)
====================================================

Formate les résultats d'exécution en réponses claires et compréhensibles.
Génère des réponses en français avec formatage approprié.
"""

import logging
from typing import Dict, List, Any, Optional
from .config.orchestration_config import OrchestrationConfig

class ResultFormatter:
    """Formateur de résultats pour l'interface utilisateur"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = OrchestrationConfig()
    
    def format_final_response(self, 
                            question: str,
                            plan: Dict[str, Any],
                            execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate la réponse finale pour l'utilisateur
        
        Args:
            question: Question utilisateur originale
            plan: Plan exécuté (avec corrections)
            execution_results: Résultats d'exécution
            
        Returns:
            Réponse formatée pour l'interface utilisateur
        """
        try:
            # Extraire les données principales
            step_results = execution_results.get('results', [])
            execution_time = execution_results.get('execution_time', 0)
            status = execution_results.get('status', 'unknown')
            
            # Formater la réponse selon le type de question
            formatted_response = self._format_by_question_type(question, step_results)
            
            # Ajouter les métadonnées
            response = {
                'question': question,
                'answer': formatted_response['answer'],
                'value': formatted_response.get('value'),
                'unit': formatted_response.get('unit'),
                'period': formatted_response.get('period'),
                'status': status,
                'execution_time': execution_time,
                'corrections_applied': plan.get('corrections', []),
                'business_processing': formatted_response.get('business_processing'),
                'graph_data': formatted_response.get('graph_data')
            }
            
            self.logger.info(f"Réponse formatée pour: {question}")
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur lors du formatage: {e}")
            return {
                'question': question,
                'answer': f"Erreur lors du traitement: {str(e)}",
                'status': 'error',
                'execution_time': 0
            }
    
    def _format_by_question_type(self, question: str, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Formate la réponse selon le type de question
        
        Returns:
            Réponse formatée avec métadonnées
        """
        question_lower = question.lower()
        
        # Consommation par période
        if any(word in question_lower for word in ['consommé', 'consommation', 'kwh']):
            return self._format_consumption_response(question, step_results)
        
        # Moyenne par jour
        elif any(word in question_lower for word in ['moyenne', 'moyen', 'par jour', 'quotidien']):
            return self._format_average_response(question, step_results)
        
        # Coût
        elif any(word in question_lower for word in ['coût', 'euro', '€', 'prix']):
            return self._format_cost_response(question, step_results)
        
        # Comparaison
        elif any(word in question_lower for word in ['comparer', 'différence', 'plus', 'moins']):
            return self._format_comparison_response(question, step_results)
        
        # Réponse générique
        else:
            return self._format_generic_response(question, step_results)
    
    def _format_consumption_response(self, question: str, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formate une réponse de consommation"""
        if not step_results:
            return {'answer': 'Aucune donnée disponible'}
        
        result = step_results[0].get('result', {})
        data = result.get('data', [])
        
        if not data:
            return {'answer': 'Aucune donnée de consommation trouvée'}
        
        value = data[0].get('value', 0)
        period = result.get('period', 'période')
        
        # Formater la valeur
        formatted_value = self._format_value(value)
        
        # Déterminer la période
        period_text = self._get_period_text(period)
        
        answer = f"Vous avez consommé {formatted_value} kWh {period_text}."
        
        return {
            'answer': answer,
            'value': value,
            'unit': 'kWh',
            'period': period,
            'graph_data': self._prepare_graph_data(data, period)
        }
    
    def _format_average_response(self, question: str, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formate une réponse de moyenne"""
        if not step_results:
            return {'answer': 'Aucune donnée disponible'}
        
        # Chercher le résultat final (post-processing)
        final_result = None
        for step_result in step_results:
            result = step_result.get('result', {})
            if 'business_processing' in result:
                final_result = result
                break
        
        if not final_result:
            # Utiliser le premier résultat
            final_result = step_results[0].get('result', {})
        
        data = final_result.get('data', [])
        if not data:
            return {'answer': 'Aucune donnée de moyenne trouvée'}
        
        value = data[0].get('value', 0)
        formatted_value = self._format_value(value)
        
        answer = f"Votre consommation moyenne par jour est de {formatted_value} kWh."
        
        return {
            'answer': answer,
            'value': value,
            'unit': 'kWh/jour',
            'business_processing': final_result.get('business_processing'),
            'graph_data': self._prepare_graph_data(data, 'daily_average')
        }
    
    def _format_cost_response(self, question: str, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formate une réponse de coût"""
        if not step_results:
            return {'answer': 'Aucune donnée disponible'}
        
        result = step_results[0].get('result', {})
        data = result.get('data', [])
        
        if not data:
            return {'answer': 'Aucune donnée de coût trouvée'}
        
        consumption = data[0].get('value', 0)
        cost = consumption * 0.20  # Tarif 0.20€/kWh
        
        formatted_cost = self._format_value(cost, is_currency=True)
        formatted_consumption = self._format_value(consumption)
        
        answer = f"Le coût de votre consommation est de {formatted_cost} ({formatted_consumption} kWh × 0.20€/kWh)."
        
        return {
            'answer': answer,
            'value': cost,
            'unit': '€',
            'consumption_kwh': consumption,
            'graph_data': self._prepare_graph_data(data, 'cost')
        }
    
    def _format_comparison_response(self, question: str, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formate une réponse de comparaison"""
        if len(step_results) < 2:
            return {'answer': 'Données insuffisantes pour la comparaison'}
        
        # Extraire les deux valeurs à comparer
        value1 = step_results[0].get('result', {}).get('data', [{}])[0].get('value', 0)
        value2 = step_results[1].get('result', {}).get('data', [{}])[0].get('value', 0)
        
        if value2 == 0:
            return {'answer': 'Impossible de calculer la comparaison (division par zéro)'}
        
        difference = value1 - value2
        percentage = (difference / value2) * 100
        
        formatted_value1 = self._format_value(value1)
        formatted_value2 = self._format_value(value2)
        formatted_diff = self._format_value(abs(difference))
        
        if difference > 0:
            answer = f"La première période ({formatted_value1} kWh) est supérieure de {formatted_diff} kWh (+{percentage:.1f}%) par rapport à la seconde ({formatted_value2} kWh)."
        elif difference < 0:
            answer = f"La première période ({formatted_value1} kWh) est inférieure de {formatted_diff} kWh ({percentage:.1f}%) par rapport à la seconde ({formatted_value2} kWh)."
        else:
            answer = f"Les deux périodes ont la même consommation : {formatted_value1} kWh."
        
        return {
            'answer': answer,
            'value1': value1,
            'value2': value2,
            'difference': difference,
            'percentage': percentage,
            'unit': 'kWh'
        }
    
    def _format_generic_response(self, question: str, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formate une réponse générique"""
        if not step_results:
            return {'answer': 'Aucune donnée disponible pour répondre à votre question.'}
        
        result = step_results[0].get('result', {})
        data = result.get('data', [])
        
        if not data:
            return {'answer': 'Aucune donnée trouvée pour votre question.'}
        
        value = data[0].get('value', 0)
        formatted_value = self._format_value(value)
        
        answer = f"La valeur calculée est de {formatted_value} kWh."
        
        return {
            'answer': answer,
            'value': value,
            'unit': 'kWh'
        }
    
    def _format_value(self, value: float, is_currency: bool = False) -> str:
        """Formate une valeur numérique"""
        if is_currency:
            return f"{value:.2f}€"
        else:
            return f"{value:.2f}"
    
    def _get_period_text(self, period: str) -> str:
        """Convertit une période en texte français"""
        period_mapping = {
            'last_day': 'hier',
            'current_day': 'aujourd\'hui',
            'current_week': 'cette semaine',
            'current_month': 'ce mois',
            'current_year': 'cette année',
            'last_month': 'le mois dernier',
            'last_year': 'l\'année dernière',
            '7d': 'cette semaine',
            '30d': 'ces 30 derniers jours',
            '1d': 'aujourd\'hui'
        }
        
        return period_mapping.get(period, f"sur la période {period}")
    
    def _prepare_graph_data(self, data: List[Dict[str, Any]], graph_type: str) -> Optional[Dict[str, Any]]:
        """Prépare les données pour les graphiques"""
        if not data or len(data) < 2:
            return None
        
        # Données pour graphique simple
        return {
            'type': graph_type,
            'data': data,
            'chart_type': 'bar' if graph_type == 'cost' else 'line'
        }




