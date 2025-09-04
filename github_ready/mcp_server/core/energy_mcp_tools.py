#!/usr/bin/env python3
"""
🔧 OUTILS LANGCHAIN GÉNÉRIQUES - BLOC 3
=======================================

Outils MCP génériques basés sur LangChain pour analyse énergétique.
Agents intelligents pour requêtes et analyses.

Critères d'acceptation :
- Outils génériques et puissants
- Performance < 2 secondes
- Compatible avec tous les types de questions
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents import initialize_agent
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.llms import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

from .database_manager import get_database_manager

class EnergyMCPTools:
    """Outils MCP génériques pour analyse énergétique"""
    
    def __init__(self, duckdb_path: str):
        """Initialisation des outils LangChain"""
        self.duckdb_path = duckdb_path
        self.logger = logging.getLogger(__name__)
        
        # Gestionnaire de base de données
        self.db_manager = get_database_manager()
        
        # DataFrame en mémoire pour performance
        self._load_dataframe()
        
        print("✅ Outils LangChain génériques initialisés")
    
    def _initialize_agents(self):
        """Initialiser les agents LangChain"""
        try:
            # Pour l'instant, pas d'agents LangChain pour éviter les conflits de connexion
            # Les agents seront initialisés plus tard quand nécessaire
            print("✅ Agents LangChain désactivés temporairement")
            
        except Exception as e:
            self.logger.error(f"Erreur d'initialisation des agents: {e}")
            raise
    
    def _load_dataframe(self):
        """Charger les données en mémoire pour performance"""
        try:
            # Charger un échantillon pour les tests
            self.df = self.db_manager.get_sample_data(limit=1000)
            
            print(f"✅ DataFrame chargé: {len(self.df)} lignes")
            
        except Exception as e:
            self.logger.error(f"Erreur de chargement du DataFrame: {e}")
            raise
    
    def query_energy_data(self, period: str, aggregation: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Requête générique sur les données énergétiques
        
        Args:
            period: Période d'analyse ("1d", "7d", "30d", "month", "year")
            aggregation: Type d'agrégation ("sum", "mean", "max", "min")
            filters: Filtres optionnels
            
        Returns:
            Résultats de la requête
        """
        try:
            # Validation des paramètres avec valeurs par défaut sécurisées
            valid_periods = ["1d", "7d", "30d", "month", "year", "current_day", "current_week", "current_month", "current_year", "last_day", "last_week", "last_month", "last_year"]
            valid_aggregations = ["sum", "mean", "max", "min"]
            
            # Validation souple avec valeurs par défaut
            validated_period = period
            validated_aggregation = aggregation
            
            if period not in valid_periods:
                validated_period = "7d"  # Valeur par défaut sécurisée
            if aggregation not in valid_aggregations:
                validated_aggregation = "sum"  # Valeur par défaut sécurisée
            
            # Construction de la requête SQL
            query = self._build_energy_query(validated_period, validated_aggregation, filters)
            
            # Exécution via le gestionnaire sécurisé
            result_df = self.db_manager.execute_query(query)
            
            # Conversion en format JSON avec sérialisation des timestamps
            result = {
                "status": "success",
                "period": validated_period,  # Utiliser la valeur validée
                "aggregation": validated_aggregation,  # Utiliser la valeur validée
                "data": result_df.to_dict('records'),
                "summary": {
                    "count": len(result_df),
                    "total": float(result_df.iloc[0, 0]) if len(result_df) > 0 else 0
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur de requête énergétique: {e}")
            return {"status": "error", "message": str(e)}
    
    def _build_energy_query(self, period: str, aggregation: str, filters: Optional[Dict] = None) -> str:
        """Construire une requête SQL sécurisée"""
        
        # Mapping des périodes avec logique temporelle DYNAMIQUE
        # Basé sur CURRENT_DATE pour être relatif à la date système réelle
        period_mapping = {
            "1d": "DATE(timestamp) = CURRENT_DATE - INTERVAL 1 DAY",
            "7d": "timestamp >= CURRENT_DATE - INTERVAL 7 DAY AND timestamp <= CURRENT_DATE",
            "30d": "timestamp >= CURRENT_DATE - INTERVAL 30 DAY AND timestamp <= CURRENT_DATE",
            "month": "timestamp >= DATE_TRUNC('month', CURRENT_DATE) AND timestamp <= CURRENT_DATE",
            "year": "timestamp >= DATE_TRUNC('year', CURRENT_DATE) AND timestamp <= CURRENT_DATE",
            "current_day": "DATE(timestamp) = CURRENT_DATE",
            "current_week": "timestamp >= DATE_TRUNC('week', CURRENT_DATE) AND timestamp <= CURRENT_DATE",
            "current_month": "timestamp >= DATE_TRUNC('month', CURRENT_DATE) AND timestamp <= CURRENT_DATE",
            "current_year": "timestamp >= DATE_TRUNC('year', CURRENT_DATE) AND timestamp <= CURRENT_DATE",
            "last_day": "DATE(timestamp) = CURRENT_DATE - INTERVAL 1 DAY",
            "last_week": "timestamp >= DATE_TRUNC('week', CURRENT_DATE) - INTERVAL 7 DAY AND timestamp < DATE_TRUNC('week', CURRENT_DATE)",
            "last_month": "timestamp >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL 1 MONTH) AND timestamp < DATE_TRUNC('month', CURRENT_DATE)",
            "last_year": "timestamp >= DATE_TRUNC('year', CURRENT_DATE - INTERVAL 1 YEAR) AND timestamp < DATE_TRUNC('year', CURRENT_DATE)"
        }
        
        # Mapping des agrégations (sécurisé - validation déjà faite)
        agg_mapping = {
            "sum": "SUM(energy_total_kwh)",
            "mean": "AVG(energy_total_kwh)",
            "max": "MAX(energy_total_kwh)",
            "min": "MIN(energy_total_kwh)"
        }
        
        # Construction de la requête (sécurisée)
        where_clause = period_mapping[period]  # Validation garantie
        agg_function = agg_mapping[aggregation]  # Validation garantie
        
        query = f"""
            SELECT 
                {agg_function} as value,
                COUNT(*) as count,
                MIN(timestamp) as start_date,
                MAX(timestamp) as end_date
            FROM energy_data 
            WHERE {where_clause}
        """
        
        return query
    
    def calculate_statistics(self, metrics: List[str], group_by: str) -> Dict[str, Any]:
        """
        Calculs statistiques génériques
        
        Args:
            metrics: Métriques à calculer ("mean", "std", "min", "max", "sum")
            group_by: Groupement ("hour", "hourly", "day", "daily", "week", "weekly", "month", "monthly")
            
        Returns:
            Statistiques calculées
        """
        try:
            # Normalisation des types de groupement
            group_mapping = {
                "hour": "hour",
                "hourly": "hour",
                "day": "day", 
                "daily": "day",
                "week": "week",
                "weekly": "week",
                "month": "month",
                "monthly": "month"
            }
            
            normalized_group = group_mapping.get(group_by, group_by)
            
            # Utilisation de Pandas pour les calculs
            if normalized_group == "hour":
                grouped = self.df.groupby(self.df['timestamp'].dt.hour)
            elif normalized_group == "day":
                grouped = self.df.groupby(self.df['timestamp'].dt.day)
            elif normalized_group == "week":
                grouped = self.df.groupby(self.df['timestamp'].dt.isocalendar().week)
            elif normalized_group == "month":
                grouped = self.df.groupby(self.df['timestamp'].dt.month)
            else:
                # Fallback pour les autres types
                grouped = self.df.groupby(group_by)
            
            # Calcul des statistiques
            stats = {}
            for metric in metrics:
                if metric == "mean":
                    stats[metric] = grouped['global_active_power_kw'].mean().to_dict()
                elif metric == "std":
                    stats[metric] = grouped['global_active_power_kw'].std().to_dict()
                elif metric == "min":
                    stats[metric] = grouped['global_active_power_kw'].min().to_dict()
                elif metric == "max":
                    stats[metric] = grouped['global_active_power_kw'].max().to_dict()
                elif metric == "sum":
                    stats[metric] = grouped['global_active_power_kw'].sum().to_dict()
            
            return {
                "status": "success",
                "metrics": metrics,
                "group_by": group_by,
                "statistics": stats
            }
            
        except Exception as e:
            self.logger.error(f"Erreur de calcul statistiques: {e}")
            return {"status": "error", "message": str(e)}
    
    def compare_periods(self, period1: str, period2: str, metric: str) -> Dict[str, Any]:
        """
        Comparaison générique de périodes
        
        Args:
            period1: Première période
            period2: Deuxième période
            metric: Métrique à comparer
            
        Returns:
            Résultats de la comparaison
        """
        try:
            # Calcul pour chaque période
            result1 = self.query_energy_data(period1, "mean")
            result2 = self.query_energy_data(period2, "mean")
            
            if result1["status"] == "error" or result2["status"] == "error":
                return {"status": "error", "message": "Erreur lors du calcul des périodes"}
            
            # Calcul de la différence
            value1 = result1["summary"]["total"]
            value2 = result2["summary"]["total"]
            difference = value2 - value1
            percentage_change = (difference / value1 * 100) if value1 != 0 else 0
            
            return {
                "status": "success",
                "period1": {
                    "name": period1,
                    "value": value1
                },
                "period2": {
                    "name": period2,
                    "value": value2
                },
                "comparison": {
                    "difference": difference,
                    "percentage_change": percentage_change,
                    "higher_period": period2 if difference > 0 else period1
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erreur de comparaison: {e}")
            return {"status": "error", "message": str(e)}
    
    def detect_anomalies(self, threshold: float, method: str) -> Dict[str, Any]:
        """
        Détection générique d'anomalies
        
        Args:
            threshold: Seuil de détection (peut être string ou float)
            method: Méthode ("zscore", "iqr", "threshold")
            
        Returns:
            Anomalies détectées
        """
        try:
            # Conversion et validation du threshold
            try:
                threshold_float = float(threshold)
            except (ValueError, TypeError):
                return {"status": "error", "message": f"Seuil invalide: {threshold}. Doit être un nombre."}
            
            # Validation de la méthode
            valid_methods = ["zscore", "iqr", "threshold"]
            if method not in valid_methods:
                return {"status": "error", "message": f"Méthode non supportée: {method}. Méthodes valides: {valid_methods}"}
            
            if method == "zscore":
                # Détection par Z-score
                z_scores = np.abs((self.df['global_active_power_kw'] - self.df['global_active_power_kw'].mean()) / self.df['global_active_power_kw'].std())
                anomalies = self.df[z_scores > threshold_float]
                
            elif method == "iqr":
                # Détection par IQR
                Q1 = self.df['global_active_power_kw'].quantile(0.25)
                Q3 = self.df['global_active_power_kw'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold_float * IQR
                upper_bound = Q3 + threshold_float * IQR
                anomalies = self.df[(self.df['global_active_power_kw'] < lower_bound) | (self.df['global_active_power_kw'] > upper_bound)]
                
            elif method == "threshold":
                # Détection par seuil simple
                anomalies = self.df[self.df['global_active_power_kw'] > threshold_float]
            
            return {
                "status": "success",
                "method": method,
                "threshold": threshold_float,
                "anomalies_count": len(anomalies),
                "anomalies": anomalies.to_dict('records') if len(anomalies) > 0 else []
            }
            
        except Exception as e:
            self.logger.error(f"Erreur de détection d'anomalies: {e}")
            return {"status": "error", "message": str(e)}
    
    def estimate_costs(self, tariff: float, period: str) -> Dict[str, Any]:
        """
        Estimation générique de coûts
        
        Args:
            tariff: Tarif par kWh (peut être string ou float)
            period: Période de calcul
            
        Returns:
            Estimation des coûts
        """
        try:
            # Conversion et validation du tarif
            try:
                tariff_float = float(tariff)
            except (ValueError, TypeError):
                return {"status": "error", "message": f"Tarif invalide: {tariff}. Doit être un nombre."}
            
            # Récupérer la consommation
            consumption_result = self.query_energy_data(period, "sum")
            
            if consumption_result["status"] == "error":
                return consumption_result
            
            # Calcul du coût
            total_consumption = consumption_result["summary"]["total"]  # kWh
            total_cost = total_consumption * tariff_float
            
            return {
                "status": "success",
                "period": period,
                "tariff": tariff_float,
                "consumption_kwh": total_consumption,
                "total_cost_euros": total_cost,
                "daily_average_cost": total_cost / 30 if period == "month" else total_cost / 7 if period == "7d" else total_cost
            }
            
        except Exception as e:
            self.logger.error(f"Erreur d'estimation de coûts: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_forecast(self, horizon: str, model: str) -> Dict[str, Any]:
        """
        Prévision générique
        
        Args:
            horizon: Horizon de prévision ("7d", "30d", "90d")
            model: Modèle à utiliser ("simple", "trend", "seasonal")
            
        Returns:
            Prévisions générées
        """
        try:
            # Pour l'instant, prévision simple basée sur la moyenne
            if model == "simple":
                # Moyenne des 7 derniers jours
                recent_data = self.query_energy_data("7d", "mean")
                if recent_data["status"] == "error":
                    return recent_data
                
                average_consumption = recent_data["summary"]["total"]
                
                # Prévision simple
                if horizon == "7d":
                    forecast_value = average_consumption * 7
                elif horizon == "30d":
                    forecast_value = average_consumption * 30
                elif horizon == "90d":
                    forecast_value = average_consumption * 90
                else:
                    return {"status": "error", "message": f"Horizon non supporté: {horizon}"}
                
                return {
                    "status": "success",
                    "horizon": horizon,
                    "model": model,
                    "forecast_value": forecast_value,
                    "confidence_interval": [forecast_value * 0.9, forecast_value * 1.1]
                }
            
            else:
                return {"status": "error", "message": f"Modèle non supporté: {model}"}
                
        except Exception as e:
            self.logger.error(f"Erreur de prévision: {e}")
            return {"status": "error", "message": str(e)}


# ========== NOUVELLES CAPACITÉS GÉNÉRIQUES ==========

class EnergyCapabilities:
    """🆕 Nouvelles capacités génériques pour évolutivité"""
    
    def __init__(self, energy_tools):
        self.energy_tools = energy_tools
        self.db_manager = energy_tools.db_manager
        
    def execute_temporal_aggregation(self, 
                                   metric: str = "consumption",
                                   period: str = "7d", 
                                   aggregation: str = "sum",
                                   zone: str = None) -> Dict[str, Any]:
        """
        🆕 CAPACITÉ GÉNÉRIQUE : Agrégation temporelle universelle
        
        Peut traiter des milliers de questions :
        - "Consommation hier" → metric="consumption", period="1d", aggregation="sum"
        - "Puissance max semaine" → metric="power", period="7d", aggregation="max"
        - "Cuisine ce mois" → metric="consumption", period="30d", zone="cuisine"
        """
        
        # Si c'est une requête simple, utiliser la méthode existante
        if metric == "consumption" and not zone:
            return self.energy_tools.query_energy_data(period, aggregation)
        
        # Mapping métrique → colonne DuckDB réelle
        metric_columns = {
            "consumption": "energy_total_kwh",
            "power": "global_active_power_kw",
            "voltage": "voltage_v",
            "intensity": "global_intensity_a",
            "cuisine": "sub_metering_1_kwh",
            "buanderie": "sub_metering_2_kwh",
            "chauffage": "sub_metering_3_kwh"
        }
        
        column = metric_columns.get(zone or metric, "energy_total_kwh")
        
        try:
            # Requête générique avec syntaxe DuckDB correcte
            period_days = period.replace('d', '').replace('month', '30')
            sql = f"""
            SELECT 
                {aggregation.upper()}({column}) as value,
                COUNT(*) as records_count
            FROM energy_data
            WHERE timestamp >= CURRENT_DATE - INTERVAL '{period_days} days'
            """
            
            result = self.db_manager.execute_query(sql)
            
            return {
                "value": result[0][0] if result else 0,
                "records_count": result[0][1] if result else 0,
                "metric": metric,
                "zone": zone,
                "aggregation": aggregation,
                "period": period,
                "source": "generic_capability"
            }
            
        except Exception as e:
            # Fallback vers méthode existante
            return self.energy_tools.query_energy_data(period, aggregation)
    
    def execute_cost_calculation(self, 
                               consumption_kwh: float = None,
                               period: str = None,
                               tariff: float = 0.20,
                               target_savings: float = None) -> Dict[str, Any]:
        """
        🆕 CAPACITÉ GÉNÉRIQUE : Calculs financiers
        
        Questions supportées :
        - "Coût cette semaine"
        - "Combien pour économiser 5€" (Question 41 critique!)
        """
        
        # Si pas de consommation fournie, la récupérer
        if consumption_kwh is None and period:
            consumption_data = self.execute_temporal_aggregation("consumption", period, "sum")
            consumption_kwh = consumption_data.get("value", 0)
        
        if consumption_kwh is None:
            consumption_kwh = 0
            
        # Calcul de base
        cost = consumption_kwh * tariff
        
        result = {
            "consumption_kwh": consumption_kwh,
            "tariff": tariff,
            "cost": cost,
            "formatted_cost": f"{cost:.2f}€",
            "period": period,
            "source": "generic_capability"
        }
        
        # Question 41 spéciale : "Pour économiser X€, réduire de combien ?"
        if target_savings:
            reduction_kwh = target_savings / tariff
            
            result.update({
                "target_savings": target_savings,
                "reduction_needed_kwh": reduction_kwh,
                "reduction_percentage": (reduction_kwh / consumption_kwh * 100) if consumption_kwh > 0 else 0,
                "advice": f"Réduire de {reduction_kwh:.1f} kWh pour économiser {target_savings}€"
            })
        
        return result

    def execute_zone_comparison(self, period: str = "30d") -> Dict[str, Any]:
        """
        🆕 CAPACITÉ GÉNÉRIQUE : Comparaison zones
        
        Questions supportées :
        - "Quel sous-compteur consomme le plus ?"
        - "Répartition par zones"
        - "Cuisine vs buanderie"
        """
        
        try:
            period_days = period.replace('d', '').replace('month', '30')
            sql = f"""
            SELECT 
                SUM(sub_metering_1_kwh) as cuisine,
                SUM(sub_metering_2_kwh) as buanderie,
                SUM(sub_metering_3_kwh) as chauffage,
                SUM(energy_total_kwh) as total
            FROM energy_data
            WHERE timestamp >= CURRENT_DATE - INTERVAL '{period_days} days'
            """
            
            result = self.db_manager.execute_query(sql)
            
            if result:
                cuisine, buanderie, chauffage, total = result[0]
                autres = max(0, total - (cuisine + buanderie + chauffage))
                
                return {
                    "zones": {
                        "cuisine": cuisine,
                        "buanderie": buanderie,
                        "chauffage": chauffage,
                        "autres": autres
                    },
                    "total": total,
                    "percentages": {
                        "cuisine": (cuisine / total * 100) if total > 0 else 0,
                        "buanderie": (buanderie / total * 100) if total > 0 else 0,
                        "chauffage": (chauffage / total * 100) if total > 0 else 0,
                        "autres": (autres / total * 100) if total > 0 else 0
                    },
                    "period": period,
                    "source": "generic_capability"
                }
            else:
                return {"error": "Aucune donnée trouvée", "period": period}
                
        except Exception as e:
            return {"error": str(e), "period": period}


# Instance globale
_energy_tools: Optional[EnergyMCPTools] = None

def get_energy_tools() -> EnergyMCPTools:
    """Retourne l'instance globale des outils énergétiques"""
    global _energy_tools
    if _energy_tools is None:
        # Gérer les chemins relatifs depuis différents répertoires
        base_path = os.getenv('DUCKDB_PATH', 'data_genere/processed/energy_fictional_2h.duckdb')
        if not os.path.exists(base_path):
            # Essayer depuis le répertoire parent
            parent_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data_genere/processed/energy_fictional_2h.duckdb')
            if os.path.exists(parent_path):
                duckdb_path = parent_path
            else:
                duckdb_path = base_path
        else:
            duckdb_path = base_path
        _energy_tools = EnergyMCPTools(duckdb_path)
    return _energy_tools


# Instance globale des nouvelles capacités
_energy_capabilities = None

def get_energy_capabilities():
    """Retourne l'instance globale des nouvelles capacités"""
    global _energy_capabilities
    if _energy_capabilities is None:
        energy_tools = get_energy_tools()
        _energy_capabilities = EnergyCapabilities(energy_tools)
    return _energy_capabilities
