#!/usr/bin/env python3
"""
Interface stable pour les prévisions
Permet d'ajouter Prophet plus tard sans casser l'application
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import random
import math

class ForecastInterface:
    """
    Interface stable pour les prévisions
    """
    
    def __init__(self):
        self.forecast_mode = "mock"  # "mock" ou "prophet"
        self.config = {
            "mock": {
                "enabled": True,
                "realistic_patterns": True
            },
            "prophet": {
                "enabled": False,
                "model_path": None
            }
        }
    
    def generate_forecast(self, horizon: str, model: str = "simple") -> Dict[str, Any]:
        """
        Interface stable pour les prévisions
        """
        try:
            # Phase 1: Mock simple
            if self.forecast_mode == "mock":
                return self._mock_forecast(horizon, model)
            
            # Phase 2: Prophet réel (à implémenter plus tard)
            elif self.forecast_mode == "prophet":
                return self._prophet_forecast(horizon, model)
            
            else:
                return {"status": "error", "message": "Mode de prévision non reconnu"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _mock_forecast(self, horizon: str, model: str) -> Dict[str, Any]:
        """
        Prévisions mock basées sur les patterns historiques
        """
        # Déterminer le contexte
        context = self._get_forecast_context()
        
        # Générer des prévisions réalistes
        predictions = self._generate_realistic_predictions(horizon, context)
        
        return {
            "status": "success",
            "forecast": "Prévision basée sur les patterns historiques",
            "horizon": horizon,
            "model": model,
            "predictions": predictions,
            "confidence": "Moyenne",
            "context": context,
            "mode": "mock"
        }
    
    def _prophet_forecast(self, horizon: str, model: str) -> Dict[str, Any]:
        """
        Prévisions Prophet (à implémenter plus tard)
        """
        # TODO: Implémenter Prophet
        return {
            "status": "error", 
            "message": "Prophet non encore implémenté"
        }
    
    def _get_forecast_context(self) -> Dict[str, Any]:
        """
        Détermine le contexte pour les prévisions
        """
        current_date = datetime.now()
        
        # Date de la dernière donnée réelle (30/08/2025 10:30:00)
        last_real_data = datetime(2025, 8, 30, 10, 30, 0)
        
        if current_date > last_real_data:
            return {
                "mode": "simulation",
                "simulation_date": last_real_data,
                "real_date": current_date,
                "message": "Mode démonstration : Données simulées",
                "is_demo": True
            }
        else:
            return {
                "mode": "normal",
                "current_date": current_date,
                "is_demo": False
            }
    
    def _generate_realistic_predictions(self, horizon: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère des prévisions réalistes basées sur les patterns
        """
        predictions = []
        
        # Déterminer le nombre de périodes
        if horizon == "1d":
            periods = 24  # 24 heures
        elif horizon == "7d":
            periods = 168  # 7 jours * 24 heures
        elif horizon == "30d":
            periods = 720  # 30 jours * 24 heures
        else:
            periods = 24  # Par défaut
        
        # Valeurs de base réalistes
        base_consumption = 1.2  # kWh moyen par heure
        hourly_pattern = [
            0.8, 0.7, 0.6, 0.5, 0.4, 0.3,  # 0-6h (nuit)
            0.4, 0.6, 0.8, 1.0, 1.2, 1.4,  # 6-12h (matin)
            1.3, 1.1, 1.0, 1.2, 1.5, 1.8,  # 12-18h (après-midi)
            1.9, 2.0, 1.8, 1.6, 1.3, 1.0   # 18-24h (soir)
        ]
        
        # Date de départ
        start_date = context.get("simulation_date", datetime.now())
        
        for i in range(periods):
            # Calculer l'heure de la journée
            current_hour = (start_date + timedelta(hours=i)).hour
            
            # Pattern horaire
            hour_factor = hourly_pattern[current_hour]
            
            # Variation saisonnière (été vs hiver)
            day_of_year = (start_date + timedelta(hours=i)).timetuple().tm_yday
            seasonal_factor = 1.0 + 0.2 * abs(math.sin(2 * math.pi * day_of_year / 365))
            
            # Bruit aléatoire
            noise = random.uniform(-0.1, 0.1)
            
            # Consommation finale
            consumption = base_consumption * hour_factor * seasonal_factor * (1 + noise)
            
            # Date de la prédiction
            prediction_date = start_date + timedelta(hours=i)
            
            predictions.append({
                "date": prediction_date.strftime("%Y-%m-%d %H:%M:%S"),
                "value": round(consumption, 3),
                "confidence_lower": round(consumption * 0.9, 3),
                "confidence_upper": round(consumption * 1.1, 3)
            })
        
        return predictions
    
    def switch_mode(self, mode: str):
        """
        Change le mode de prévision
        """
        if mode in ["mock", "prophet"]:
            self.forecast_mode = mode
            return {"status": "success", "message": f"Mode changé vers {mode}"}
        else:
            return {"status": "error", "message": "Mode non reconnu"}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retourne le statut actuel
        """
        return {
            "current_mode": self.forecast_mode,
            "config": self.config,
            "context": self._get_forecast_context()
        }

# Instance globale
forecast_tool = ForecastInterface()




