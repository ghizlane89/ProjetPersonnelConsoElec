#!/usr/bin/env python3
"""
🔧 LOGIQUE MÉTIER ÉLECTRIQUE - BLOC 4 (ORCHESTRATION)
======================================================

Validation et correction des paramètres métier pour l'analyse énergétique.
Garantit la cohérence des calculs kW vs kWh.

Critères d'acceptation :
- Validation stricte des paramètres
- Correction automatique des erreurs métier
- Logique électrique centralisée
"""

from typing import Dict, Any, Optional, List
import logging

class EnergyBusinessLogic:
    """Logique métier pour l'analyse énergétique"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Constantes métier
        self.AGGREGATION_PERIOD_HOURS = 2  # Agrégation par 2h
        self.KW_TO_KWH_FACTOR = self.AGGREGATION_PERIOD_HOURS  # Conversion kW → kWh
        
        # Mapping des corrections métier
        self.BUSINESS_CORRECTIONS = {
            "consumption_average_per_day": {
                "description": "Consommation moyenne par jour",
                "correction": {
                    "aggregation": "sum",  # Sommer les consommations
                    "post_processing": "divide_by_days"  # Diviser par le nombre de jours
                }
            },
            "consumption_average_per_hour": {
                "description": "Consommation moyenne par heure",
                "correction": {
                    "aggregation": "sum",
                    "post_processing": "divide_by_hours"
                }
            },
            "consumption_average_per_week": {
                "description": "Consommation moyenne par semaine",
                "correction": {
                    "aggregation": "sum",
                    "post_processing": "divide_by_weeks"
                }
            }
        }
    
    def validate_and_correct_parameters(self, parameters: Dict[str, Any], question_context: str = "") -> Dict[str, Any]:
        """
        Valide et corrige les paramètres selon la logique métier
        
        Args:
            parameters: Paramètres d'agrégation
            question_context: Contexte de la question pour détecter les cas spéciaux
            
        Returns:
            Paramètres corrigés
        """
        try:
            corrected_params = parameters.copy()
            
            # Détection des cas métier spéciaux
            business_case = self._detect_business_case(parameters, question_context)
            
            if business_case:
                corrected_params = self._apply_business_correction(corrected_params, business_case)
                self.logger.info(f"Correction métier appliquée: {business_case}")
            
            # Validation des paramètres corrigés
            validated_params = self._validate_parameters(corrected_params)
            
            return validated_params
            
        except Exception as e:
            self.logger.error(f"Erreur de validation métier: {e}")
            return parameters  # Retourner les paramètres originaux en cas d'erreur
    
    def _detect_business_case(self, parameters: Dict[str, Any], question_context: str) -> Optional[str]:
        """
        Détecte les cas métier spéciaux nécessitant une correction
        """
        aggregation = parameters.get("aggregation", "")
        period = parameters.get("period", "")
        question_lower = question_context.lower()
        
        # Cas 1: Moyenne de consommation (pas de puissance)
        if aggregation == "mean" and any(keyword in question_lower for keyword in ["moyenne", "average", "consommation", "consumption"]):
            if "jour" in question_lower or "day" in question_lower:
                return "consumption_average_per_day"
            elif "heure" in question_lower or "hour" in question_lower:
                return "consumption_average_per_hour"
            elif "semaine" in question_lower or "week" in question_lower:
                return "consumption_average_per_week"
        
        # Cas 2: Période "year" avec "mean" (souvent incorrect)
        if period == "year" and aggregation == "mean":
            return "consumption_average_per_day"
        
        return None
    
    def _apply_business_correction(self, parameters: Dict[str, Any], business_case: str) -> Dict[str, Any]:
        """
        Applique la correction métier appropriée
        """
        if business_case in self.BUSINESS_CORRECTIONS:
            correction = self.BUSINESS_CORRECTIONS[business_case]["correction"]
            
            # Appliquer la correction
            parameters["aggregation"] = correction["aggregation"]
            parameters["post_processing"] = correction["post_processing"]
            
            # Ajouter des métadonnées pour le post-traitement
            parameters["business_correction"] = business_case
            parameters["original_aggregation"] = parameters.get("original_aggregation", parameters.get("aggregation"))
        
        return parameters
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide les paramètres selon les règles métier
        """
        # Validation des périodes
        valid_periods = ["1d", "7d", "30d", "month", "year", "current_day", "current_week", "current_month", "current_year", "last_day", "last_week", "last_month", "last_year"]
        period = parameters.get("period", "")
        
        if period not in valid_periods:
            parameters["period"] = "7d"  # Valeur par défaut sécurisée
            self.logger.warning(f"Période invalide '{period}', utilisation de '7d'")
        
        # Validation des agrégations
        valid_aggregations = ["sum", "max", "min", "mean", "count"]
        aggregation = parameters.get("aggregation", "")
        
        if aggregation not in valid_aggregations:
            parameters["aggregation"] = "sum"  # Valeur par défaut sécurisée
            self.logger.warning(f"Agrégation invalide '{aggregation}', utilisation de 'sum'")
        
        return parameters
    
    def apply_post_processing(self, result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applique le post-traitement métier si nécessaire
        """
        try:
            post_processing = parameters.get("post_processing")
            
            if not post_processing:
                return result
            
            # Extraire la valeur brute
            if "data" in result and len(result["data"]) > 0:
                raw_value = result["data"][0].get("value", 0)
                
                # Appliquer le post-traitement
                if post_processing == "divide_by_days":
                    # Calculer le nombre de jours dans la période
                    days_count = self._calculate_days_count(parameters.get("period", "7d"))
                    processed_value = raw_value / days_count if days_count > 0 else raw_value
                    
                    # Mettre à jour le résultat
                    result["data"][0]["value"] = processed_value
                    result["summary"]["total"] = processed_value
                    result["business_processing"] = f"Consommation totale divisée par {days_count} jours"
                
                elif post_processing == "divide_by_hours":
                    # Calculer le nombre d'heures dans la période
                    hours_count = self._calculate_hours_count(parameters.get("period", "7d"))
                    processed_value = raw_value / hours_count if hours_count > 0 else raw_value
                    
                    result["data"][0]["value"] = processed_value
                    result["summary"]["total"] = processed_value
                    result["business_processing"] = f"Consommation totale divisée par {hours_count} heures"
                
                elif post_processing == "divide_by_weeks":
                    # Calculer le nombre de semaines dans la période
                    weeks_count = self._calculate_weeks_count(parameters.get("period", "7d"))
                    processed_value = raw_value / weeks_count if weeks_count > 0 else raw_value
                    
                    result["data"][0]["value"] = processed_value
                    result["summary"]["total"] = processed_value
                    result["business_processing"] = f"Consommation totale divisée par {weeks_count} semaines"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur de post-traitement: {e}")
            return result
    
    def _calculate_days_count(self, period: str) -> int:
        """Calcule le nombre de jours dans une période"""
        from datetime import datetime, timedelta
        
        # Pour les périodes fixes
        fixed_periods = {
            "1d": 1,
            "7d": 7,
            "30d": 30,
            "month": 30,
            "current_month": 30,
            "last_month": 30
        }
        
        if period in fixed_periods:
            return fixed_periods[period]
        
        # Pour "year", calculer dynamiquement selon les données réelles
        if period == "year":
            try:
                # Importer le gestionnaire de base de données
                from mcp_server.core.database_manager import get_database_manager
                db_manager = get_database_manager()
                
                # Calculer le nombre réel de jours dans les données
                query = """
                SELECT COUNT(DISTINCT DATE(timestamp)) as days_count
                FROM energy_data
                """
                result = db_manager.execute_query(query)
                if result is not None and not result.empty:
                    return int(result.iloc[0]['days_count'])  # Accès DataFrame correct
                else:
                    return 365  # Fallback
            except Exception as e:
                self.logger.warning(f"Impossible de calculer les jours dynamiquement: {e}")
                return 365  # Fallback
        
        return 7  # Valeur par défaut
    
    def _calculate_hours_count(self, period: str) -> int:
        """Calcule le nombre d'heures dans une période"""
        return self._calculate_days_count(period) * 24
    
    def _calculate_weeks_count(self, period: str) -> int:
        """Calcule le nombre de semaines dans une période"""
        return max(1, self._calculate_days_count(period) // 7)

# Instance globale pour utilisation dans l'Orchestrateur
energy_business_logic = EnergyBusinessLogic()
