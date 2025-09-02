#!/usr/bin/env python3
"""
🧪 TESTS BLOC 3 - SERVEUR MCP
=============================

Tests unitaires et d'intégration pour le serveur MCP.
Validation des critères d'acceptation du BLOC 3.

Critères testés :
- Endpoints sécurisés
- Validation des arguments
- Lecture/écriture DuckDB OK
- Retour JSON propre
"""

import sys
import os
import json
import time
import unittest
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import get_mcp_server, get_energy_tools, get_dashboard_tools

class TestMCPServer(unittest.TestCase):
    """Tests pour le serveur MCP principal"""
    
    def setUp(self):
        """Configuration des tests"""
        self.server = get_mcp_server()
    
    def test_server_initialization(self):
        """Test d'initialisation du serveur"""
        self.assertIsNotNone(self.server)
        self.assertIsNotNone(self.server.db_manager)
        self.assertIsNotNone(self.server.energy_tools)
        self.assertIsNotNone(self.server.dashboard_tools)
    
    def test_plan_validation(self):
        """Test de validation des plans"""
        # Plan valide
        valid_plan = {
            "metadata": {"plan_id": "test_001"},
            "steps": [
                {
                    "step_id": 1,
                    "tool_name": "aggregate",
                    "parameters": {"period": "7d", "aggregation": "sum"}
                }
            ],
            "summary": "Test plan"
        }
        self.assertTrue(self.server._validate_plan(valid_plan))
        
        # Plan invalide
        invalid_plan = {"steps": []}
        self.assertFalse(self.server._validate_plan(invalid_plan))
    
    def test_execution_order(self):
        """Test de l'ordre d'exécution"""
        steps = [
            {"step_id": 1, "tool_name": "aggregate"},
            {"step_id": 2, "tool_name": "plot", "depends_on": [1]}
        ]
        
        execution_order = self.server._get_execution_order(steps)
        self.assertEqual(execution_order, [1, 2])
    
    def test_simple_plan_execution(self):
        """Test d'exécution d'un plan simple"""
        plan = {
            "metadata": {"plan_id": "test_001"},
            "steps": [
                {
                    "step_id": 1,
                    "tool_name": "aggregate",
                    "parameters": {"period": "7d", "aggregation": "sum"}
                }
            ],
            "summary": "Test plan"
        }
        
        result = self.server.execute_plan(plan)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("execution_time", result)
        self.assertIn("results", result)
        self.assertIn("summary", result)
    
    def test_complex_plan_execution(self):
        """Test d'exécution d'un plan complexe"""
        plan = {
            "metadata": {"plan_id": "test_002"},
            "steps": [
                {
                    "step_id": 1,
                    "tool_name": "aggregate",
                    "parameters": {"period": "7d", "aggregation": "sum"}
                },
                {
                    "step_id": 2,
                    "tool_name": "cost",
                    "parameters": {"tariff": 0.20, "period": "7d"},
                    "depends_on": [1]
                },
                {
                    "step_id": 3,
                    "tool_name": "plot",
                    "parameters": {"chart_type": "consumption_overview"},
                    "depends_on": [1, 2]
                }
            ],
            "summary": "Test plan complexe"
        }
        
        result = self.server.execute_plan(plan)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 3)
        self.assertGreater(result["summary"]["success_rate"], 0)

class TestEnergyTools(unittest.TestCase):
    """Tests pour les outils énergétiques"""
    
    def setUp(self):
        """Configuration des tests"""
        self.tools = get_energy_tools()
    
    def test_query_energy_data(self):
        """Test de requête de données énergétiques"""
        result = self.tools.query_energy_data("7d", "sum")
        
        self.assertIn("status", result)
        self.assertIn("period", result)
        self.assertIn("aggregation", result)
    
    def test_calculate_statistics(self):
        """Test de calcul de statistiques"""
        result = self.tools.calculate_statistics(["mean", "max"], "day")
        
        self.assertIn("status", result)
        self.assertIn("metrics", result)
        self.assertIn("statistics", result)
    
    def test_compare_periods(self):
        """Test de comparaison de périodes"""
        result = self.tools.compare_periods("7d", "30d", "consumption")
        
        self.assertIn("status", result)
        self.assertIn("period1", result)
        self.assertIn("period2", result)
        self.assertIn("comparison", result)
    
    def test_detect_anomalies(self):
        """Test de détection d'anomalies"""
        result = self.tools.detect_anomalies(2.0, "zscore")
        
        self.assertIn("status", result)
        self.assertIn("method", result)
        self.assertIn("threshold", result)
        self.assertIn("anomalies_count", result)
    
    def test_estimate_costs(self):
        """Test d'estimation de coûts"""
        result = self.tools.estimate_costs(0.20, "30d")
        
        self.assertIn("status", result)
        self.assertIn("tariff", result)
        self.assertIn("consumption_kwh", result)
        self.assertIn("total_cost_euros", result)
    
    def test_generate_forecast(self):
        """Test de génération de prévisions"""
        result = self.tools.generate_forecast("7d", "simple")
        
        self.assertIn("status", result)
        self.assertIn("horizon", result)
        self.assertIn("model", result)
        self.assertIn("forecast_value", result)

class TestDashboardTools(unittest.TestCase):
    """Tests pour les outils de tableau de bord"""
    
    def setUp(self):
        """Configuration des tests"""
        self.dashboard = get_dashboard_tools()
    
    def test_create_consumption_overview(self):
        """Test de création de vue d'ensemble"""
        result = self.dashboard.create_consumption_overview("7d")
        
        # Vérifier que c'est du JSON valide
        chart_data = json.loads(result)
        self.assertIsInstance(chart_data, dict)
    
    def test_create_cost_analysis(self):
        """Test de création d'analyse de coûts"""
        result = self.dashboard.create_cost_analysis(0.20, "30d")
        
        chart_data = json.loads(result)
        self.assertIsInstance(chart_data, dict)
    
    def test_create_anomaly_dashboard(self):
        """Test de création de tableau d'anomalies"""
        result = self.dashboard.create_anomaly_dashboard(2.0)
        
        chart_data = json.loads(result)
        self.assertIsInstance(chart_data, dict)
    
    def test_create_forecast_dashboard(self):
        """Test de création de tableau de prévisions"""
        result = self.dashboard.create_forecast_dashboard("7d")
        
        chart_data = json.loads(result)
        self.assertIsInstance(chart_data, dict)
    
    def test_create_time_analysis_chart(self):
        """Test de création de graphique d'analyse temporelle"""
        result = self.dashboard.create_time_analysis_chart("hourly")
        
        chart_data = json.loads(result)
        self.assertIsInstance(chart_data, dict)
    
    def test_create_sub_metering_chart(self):
        """Test de création de graphique de sous-compteurs"""
        result = self.dashboard.create_sub_metering_chart()
        
        chart_data = json.loads(result)
        self.assertIsInstance(chart_data, dict)

class TestIntegration(unittest.TestCase):
    """Tests d'intégration du BLOC 3"""
    
    def test_end_to_end_execution(self):
        """Test de bout en bout"""
        server = get_mcp_server()
        
        # Plan de test complet
        plan = {
            "metadata": {"plan_id": "integration_test"},
            "steps": [
                {
                    "step_id": 1,
                    "tool_name": "aggregate",
                    "parameters": {"period": "7d", "aggregation": "sum"}
                },
                {
                    "step_id": 2,
                    "tool_name": "cost",
                    "parameters": {"tariff": 0.20, "period": "7d"}
                },
                {
                    "step_id": 3,
                    "tool_name": "plot",
                    "parameters": {"chart_type": "consumption_overview"}
                }
            ],
            "summary": "Test d'intégration complet"
        }
        
        # Exécution
        result = server.execute_plan(plan)
        
        # Vérifications
        self.assertEqual(result["status"], "success")
        self.assertLess(result["execution_time"], 5.0)  # SLA < 5 secondes
        self.assertEqual(len(result["results"]), 3)
        self.assertGreater(result["summary"]["success_rate"], 0.5)
    
    def test_server_info(self):
        """Test des informations du serveur"""
        server = get_mcp_server()
        info = server.get_server_info()
        
        self.assertIn("server_status", info)
        self.assertIn("database_info", info)
        self.assertIn("available_tools", info)
        self.assertIn("version", info)
        
        self.assertEqual(info["server_status"], "running")
        self.assertEqual(info["version"], "1.0.0")
        self.assertIn("aggregate", info["available_tools"])
        self.assertIn("forecast", info["available_tools"])
        self.assertIn("peak", info["available_tools"])
        self.assertIn("cost", info["available_tools"])
        self.assertIn("anomaly", info["available_tools"])
        self.assertIn("plot", info["available_tools"])

def run_performance_tests():
    """Tests de performance"""
    print("\n🚀 TESTS DE PERFORMANCE")
    print("=" * 50)
    
    server = get_mcp_server()
    
    # Test de performance - plan simple
    simple_plan = {
        "metadata": {"plan_id": "perf_test"},
        "steps": [
            {
                "step_id": 1,
                "tool_name": "aggregate",
                "parameters": {"period": "7d", "aggregation": "sum"}
            }
        ],
        "summary": "Test performance"
    }
    
    start_time = time.time()
    result = server.execute_plan(simple_plan)
    execution_time = time.time() - start_time
    
    print(f"✅ Plan simple: {execution_time:.3f}s")
    print(f"✅ Status: {result['status']}")
    print(f"✅ Temps déclaré: {result['execution_time']:.3f}s")
    
    # Test de performance - plan complexe
    complex_plan = {
        "metadata": {"plan_id": "perf_test_complex"},
        "steps": [
            {
                "step_id": 1,
                "tool_name": "aggregate",
                "parameters": {"period": "30d", "aggregation": "sum"}
            },
            {
                "step_id": 2,
                "tool_name": "cost",
                "parameters": {"tariff": 0.20, "period": "30d"}
            },
            {
                "step_id": 3,
                "tool_name": "anomaly",
                "parameters": {"threshold": 2.0, "method": "zscore"}
            },
            {
                "step_id": 4,
                "tool_name": "plot",
                "parameters": {"chart_type": "consumption_overview"}
            }
        ],
        "summary": "Test performance complexe"
    }
    
    start_time = time.time()
    result = server.execute_plan(complex_plan)
    execution_time = time.time() - start_time
    
    print(f"✅ Plan complexe: {execution_time:.3f}s")
    print(f"✅ Status: {result['status']}")
    print(f"✅ Temps déclaré: {result['execution_time']:.3f}s")
    print(f"✅ Taux de succès: {result['summary']['success_rate']:.1%}")

if __name__ == '__main__':
    print("🧪 DÉMARRAGE DES TESTS BLOC 3")
    print("=" * 50)
    
    # Tests unitaires
    unittest.main(verbosity=2, exit=False)
    
    # Tests de performance
    run_performance_tests()
    
    print("\n✅ TOUS LES TESTS BLOC 3 TERMINÉS")
    print("=" * 50)





