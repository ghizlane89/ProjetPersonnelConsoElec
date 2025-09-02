#!/usr/bin/env python3
"""
📊 OUTILS SPÉCIALISÉS TABLEAU DE BORD - BLOC 3
==============================================

Outils spécialisés pour création de visualisations Plotly.
Tableau de bord Streamlit avec graphiques interactifs.

Critères d'acceptation :
- Graphiques < 2 secondes
- Compatible Streamlit
- Visualisations interactives
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import json

from .energy_mcp_tools import get_energy_tools

class DashboardTools:
    """Outils spécialisés pour tableau de bord Streamlit"""
    
    def __init__(self):
        """Initialisation des outils de tableau de bord"""
        self.energy_tools = get_energy_tools()
        print("✅ Outils tableau de bord initialisés")
    
    def create_consumption_overview(self, period: str = "7d") -> str:
        """
        Vue d'ensemble de la consommation
        
        Args:
            period: Période d'analyse
            
        Returns:
            JSON du graphique Plotly
        """
        try:
            # Récupérer les données
            consumption_data = self.energy_tools.query_energy_data(period, "sum")
            stats_data = self.energy_tools.calculate_statistics(["mean", "max"], "day")
            
            if consumption_data["status"] == "error":
                return json.dumps({"error": "Impossible de récupérer les données"})
            
            # Créer le graphique multi-panneaux
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Consommation Totale', 
                    'Consommation Moyenne', 
                    'Pics de Consommation', 
                    'Répartition Quotidienne'
                ),
                specs=[
                    [{"type": "indicator"}, {"type": "indicator"}],
                    [{"type": "bar"}, {"type": "pie"}]
                ]
            )
            
            # Panneau 1: Consommation totale
            total_consumption = consumption_data["summary"]["total"]
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=total_consumption,
                    title={"text": "kWh"},
                    gauge={"axis": {"range": [None, total_consumption * 1.2]}}
                ),
                row=1, col=1
            )
            
            # Panneau 2: Consommation moyenne
            avg_consumption = total_consumption / 7 if period == "7d" else total_consumption / 30
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=avg_consumption,
                    title={"text": "kWh/jour"},
                    gauge={"axis": {"range": [None, avg_consumption * 1.2]}}
                ),
                row=1, col=2
            )
            
            # Panneau 3: Pics de consommation (simulation)
            peak_data = pd.DataFrame({
                'jour': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
                'consommation': [12, 15, 13, 14, 16, 18, 20]
            })
            fig.add_trace(
                go.Bar(x=peak_data['jour'], y=peak_data['consommation']),
                row=2, col=1
            )
            
            # Panneau 4: Répartition (simulation)
            distribution_data = pd.DataFrame({
                'type': ['Éclairage', 'Chauffage', 'Cuisine', 'Autres'],
                'pourcentage': [25, 40, 20, 15]
            })
            fig.add_trace(
                go.Pie(labels=distribution_data['type'], values=distribution_data['pourcentage']),
                row=2, col=2
            )
            
            # Mise à jour du layout
            fig.update_layout(
                title=f"Vue d'ensemble - {period}",
                height=600,
                showlegend=False
            )
            
            return fig.to_json()
            
        except Exception as e:
            return json.dumps({"error": f"Erreur création vue d'ensemble: {str(e)}"})
    
    def create_cost_analysis(self, tariff: float = 0.20, period: str = "30d") -> str:
        """
        Analyse des coûts
        
        Args:
            tariff: Tarif par kWh
            period: Période d'analyse
            
        Returns:
            JSON du graphique Plotly
        """
        try:
            # Récupérer les données de coûts
            cost_data = self.energy_tools.estimate_costs(tariff, period)
            
            if cost_data["status"] == "error":
                return json.dumps({"error": "Impossible de calculer les coûts"})
            
            # Créer le graphique
            fig = go.Figure()
            
            # Données simulées pour l'évolution des coûts
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            costs = np.random.normal(cost_data["daily_average_cost"], 2, 30)
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=costs,
                    mode='lines+markers',
                    name='Coût quotidien',
                    line=dict(color='blue', width=2)
                )
            )
            
            # Ligne de budget (simulation)
            budget_limit = cost_data["total_cost_euros"] * 0.8  # 80% du budget
            fig.add_hline(
                y=budget_limit,
                line_dash="dash",
                line_color="red",
                annotation_text="Limite budget"
            )
            
            # Mise à jour du layout
            fig.update_layout(
                title=f"Évolution des coûts - {period} (Tarif: {tariff}€/kWh)",
                xaxis_title="Date",
                yaxis_title="Coût (€)",
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            return json.dumps({"error": f"Erreur création analyse coûts: {str(e)}"})
    
    def create_anomaly_dashboard(self, threshold: float = 2.0) -> str:
        """
        Tableau de bord des anomalies
        
        Args:
            threshold: Seuil de détection
            
        Returns:
            JSON du graphique Plotly
        """
        try:
            # Détecter les anomalies
            anomalies_data = self.energy_tools.detect_anomalies(threshold, "zscore")
            
            if anomalies_data["status"] == "error":
                return json.dumps({"error": "Impossible de détecter les anomalies"})
            
            # Créer le graphique
            fig = go.Figure()
            
            # Données simulées pour la consommation
            dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
            consumption = np.random.normal(10, 2, 100)
            
            # Ajouter quelques anomalies
            anomalies_indices = [20, 45, 70]
            for idx in anomalies_indices:
                consumption[idx] = consumption[idx] + 8
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=consumption,
                    mode='lines',
                    name='Consommation',
                    line=dict(color='blue')
                )
            )
            
            # Marquer les anomalies
            anomaly_dates = [dates[i] for i in anomalies_indices]
            anomaly_values = [consumption[i] for i in anomalies_indices]
            
            fig.add_trace(
                go.Scatter(
                    x=anomaly_dates,
                    y=anomaly_values,
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='red', size=10, symbol='x')
                )
            )
            
            # Mise à jour du layout
            fig.update_layout(
                title=f"Détection d'anomalies (Seuil: {threshold})",
                xaxis_title="Date",
                yaxis_title="Consommation (kWh)",
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            return json.dumps({"error": f"Erreur création tableau anomalies: {str(e)}"})
    
    def create_forecast_dashboard(self, horizon: str = "7d") -> str:
        """
        Tableau de bord des prévisions
        
        Args:
            horizon: Horizon de prévision
            
        Returns:
            JSON du graphique Plotly
        """
        try:
            # Générer les prévisions
            forecast_data = self.energy_tools.generate_forecast(horizon, "simple")
            
            if forecast_data["status"] == "error":
                return json.dumps({"error": "Impossible de générer les prévisions"})
            
            # Créer le graphique
            fig = go.Figure()
            
            # Données historiques (simulation)
            historical_dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            historical_values = np.random.normal(12, 2, 30)
            
            # Données de prévision
            forecast_dates = pd.date_range(start='2024-02-01', periods=7, freq='D')
            forecast_value = forecast_data["forecast_value"] / 7  # Valeur quotidienne
            forecast_values = np.random.normal(forecast_value, 1, 7)
            
            # Ajouter les données historiques
            fig.add_trace(
                go.Scatter(
                    x=historical_dates,
                    y=historical_values,
                    mode='lines',
                    name='Historique',
                    line=dict(color='blue', width=2)
                )
            )
            
            # Ajouter les prévisions
            fig.add_trace(
                go.Scatter(
                    x=forecast_dates,
                    y=forecast_values,
                    mode='lines+markers',
                    name='Prévision',
                    line=dict(color='red', width=2, dash='dash')
                )
            )
            
            # Intervalle de confiance
            confidence_lower = [v * 0.9 for v in forecast_values]
            confidence_upper = [v * 1.1 for v in forecast_values]
            
            fig.add_trace(
                go.Scatter(
                    x=forecast_dates,
                    y=confidence_upper,
                    mode='lines',
                    name='Intervalle de confiance',
                    line=dict(width=0),
                    showlegend=False
                )
            )
            
            fig.add_trace(
                go.Scatter(
                    x=forecast_dates,
                    y=confidence_lower,
                    mode='lines',
                    fill='tonexty',
                    name='Intervalle de confiance',
                    line=dict(width=0),
                    showlegend=False
                )
            )
            
            # Mise à jour du layout
            fig.update_layout(
                title=f"Prévisions de consommation - {horizon}",
                xaxis_title="Date",
                yaxis_title="Consommation (kWh)",
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            return json.dumps({"error": f"Erreur création tableau prévisions: {str(e)}"})
    
    def create_time_analysis_chart(self, analysis_type: str = "hourly") -> str:
        """
        Graphique d'analyse temporelle
        
        Args:
            analysis_type: Type d'analyse ("hourly", "daily", "weekly")
            
        Returns:
            JSON du graphique Plotly
        """
        try:
            # Récupérer les statistiques temporelles
            stats_data = self.energy_tools.calculate_statistics(["mean"], analysis_type)
            
            if stats_data["status"] == "error":
                return json.dumps({"error": "Impossible de récupérer les statistiques"})
            
            # Créer le graphique
            if analysis_type == "hourly":
                # Analyse horaire
                hours = list(range(24))
                consumption = np.random.normal(8, 3, 24)
                # Pics matin et soir
                consumption[7:9] += 4  # Matin
                consumption[18:22] += 6  # Soir
                
                fig = px.bar(
                    x=hours,
                    y=consumption,
                    title="Consommation moyenne par heure",
                    labels={'x': 'Heure', 'y': 'Consommation (kWh)'}
                )
                
            elif analysis_type == "daily":
                # Analyse quotidienne
                days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
                consumption = [10, 12, 11, 13, 14, 16, 18]  # Plus le week-end
                
                fig = px.bar(
                    x=days,
                    y=consumption,
                    title="Consommation moyenne par jour",
                    labels={'x': 'Jour', 'y': 'Consommation (kWh)'}
                )
                
            else:
                return json.dumps({"error": f"Type d'analyse non supporté: {analysis_type}"})
            
            fig.update_layout(height=400)
            return fig.to_json()
            
        except Exception as e:
            return json.dumps({"error": f"Erreur création analyse temporelle: {str(e)}"})
    
    def create_sub_metering_chart(self) -> str:
        """
        Graphique des sous-compteurs
        
        Returns:
            JSON du graphique Plotly
        """
        try:
            # Données simulées des sous-compteurs
            sub_metering_data = pd.DataFrame({
                'sous_compteur': ['Cuisine', 'Chauffage', 'Buanderie', 'Éclairage', 'Autres'],
                'consommation': [25, 40, 15, 12, 8],
                'pourcentage': [25, 40, 15, 12, 8]
            })
            
            # Créer le graphique
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Consommation par sous-compteur', 'Répartition (%)'),
                specs=[[{"type": "bar"}, {"type": "pie"}]]
            )
            
            # Graphique en barres
            fig.add_trace(
                go.Bar(
                    x=sub_metering_data['sous_compteur'],
                    y=sub_metering_data['consommation'],
                    name='Consommation (kWh)'
                ),
                row=1, col=1
            )
            
            # Graphique circulaire
            fig.add_trace(
                go.Pie(
                    labels=sub_metering_data['sous_compteur'],
                    values=sub_metering_data['pourcentage'],
                    name='Répartition'
                ),
                row=1, col=2
            )
            
            # Mise à jour du layout
            fig.update_layout(
                title="Analyse des sous-compteurs",
                height=400,
                showlegend=False
            )
            
            return fig.to_json()
            
        except Exception as e:
            return json.dumps({"error": f"Erreur création graphique sous-compteurs: {str(e)}"})

# Instance globale
_dashboard_tools: Optional[DashboardTools] = None

def get_dashboard_tools() -> DashboardTools:
    """Retourne l'instance globale des outils de tableau de bord"""
    global _dashboard_tools
    if _dashboard_tools is None:
        _dashboard_tools = DashboardTools()
    return _dashboard_tools




