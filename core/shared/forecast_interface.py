#!/usr/bin/env python3
"""
Interface stable pour les prévisions
Permet d'ajouter Prophet plus tard sans casser l'application
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import math

class ForecastInterface:
    """
    Interface stable pour les prévisions
    Compatible avec l'architecture technique et le cahier des charges
    """
    
    def __init__(self):
        self.forecast_mode = "mock"  # "mock" ou "prophet"
        self.is_available = False  # False en Phase 1, True en Phase 2
        
    def is_forecast_available(self) -> bool:
        """
        Vérifie si les prévisions sont disponibles
        """
        return self.is_available
    
    def generate_forecast(self, horizon: str, model: str = "simple") -> Dict[str, Any]:
        """
        Interface stable pour les prévisions
        Conforme au cahier des charges - Section 3.3
        """
        try:
            # Phase 1: Mock (prévisions non disponibles)
            if not self.is_forecast_available():
                return {
                    "status": "unavailable",
                    "message": "Prévisions non encore disponibles",
                    "mode": "mock",
                    "suggestions": [
                        "Consultez l'historique de consommation",
                        "Analysez les tendances passées",
                        "Prévisions disponibles dans la prochaine version"
                    ]
                }
            
            # Phase 2: Prophet (à implémenter plus tard)
            elif self.forecast_mode == "prophet":
                return self._prophet_forecast(horizon, model)
            
            # Mode mock (fallback)
            else:
                return self._mock_forecast(horizon, model)
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Erreur lors de la génération des prévisions : {str(e)}",
                "mode": self.forecast_mode
            }
    
    def _mock_forecast(self, horizon: str, model: str) -> Dict[str, Any]:
        """
        Prévisions mock pour Phase 1
        """
        return {
            "status": "mock",
            "message": "Prévisions en mode démonstration",
            "horizon": horizon,
            "model": model,
            "predictions": [],
            "confidence_intervals": [],
            "trends": [],
            "mode": "mock",
            "note": "Prévisions réelles disponibles dans la prochaine version"
        }
    
    def _prophet_forecast(self, horizon: str, model: str) -> Dict[str, Any]:
        """
        Prévisions Prophet (Phase 2)
        """
        # TODO: Implémenter Prophet
        return {
            "status": "error",
            "message": "Prophet non encore implémenté",
            "mode": "prophet"
        }
    
    def enable_forecasts(self):
        """
        Active les prévisions (Phase 2)
        """
        self.is_available = True
    
    def disable_forecasts(self):
        """
        Désactive les prévisions (Phase 1)
        """
        self.is_available = False
    
    def get_forecast_status(self) -> Dict[str, Any]:
        """
        Retourne le statut des prévisions
        """
        return {
            "available": self.is_forecast_available(),
            "mode": self.forecast_mode,
            "phase": "1" if not self.is_forecast_available() else "2"
        }

# Instance globale
forecast_interface = ForecastInterface()




