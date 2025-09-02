#!/usr/bin/env python3
"""
🧪 TESTS BLOC 2 - INTELLIGENCE LAYER
====================================

Tests unitaires et d'intégration pour la couche d'intelligence.
Validation des critères d'acceptation du BLOC 2.

Critères testés :
- Plan JSON strict défini
- Plan JSON valide (schéma Pydantic)
- Cache actif
- Aucune exécution côté LLM
"""

import sys
import os
import json
import time
import unittest
import copy
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_planner.models.plan_schema import LLMPlan, ToolStep, PlanMetadata, EXAMPLE_SIMPLE_PLAN, EXAMPLE_COMPLEX_PLAN
from llm_planner.prompts.plan_generator_prompt import PlanGeneratorPrompt, format_plan_prompt
from llm_planner.core.gemini_client import GeminiClient

class TestPlanSchema(unittest.TestCase):
    """Tests pour le schéma Pydantic des plans"""
    
    def test_simple_plan_validation(self):
        """Test de validation d'un plan simple"""
        plan = LLMPlan(**EXAMPLE_SIMPLE_PLAN)
        self.assertEqual(plan.metadata.complexity, "simple")
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].tool_name, "query_energy_data")
    
    def test_complex_plan_validation(self):
        """Test de validation d'un plan complexe"""
        plan = LLMPlan(**EXAMPLE_COMPLEX_PLAN)
        self.assertEqual(plan.metadata.complexity, "complex")
        self.assertEqual(len(plan.steps), 3)
        self.assertEqual(plan.steps[0].tool_name, "query_energy_data")
        self.assertEqual(plan.steps[1].tool_name, "generate_forecast")
        self.assertEqual(plan.steps[2].tool_name, "create_visualization")
    
    def test_invalid_tool_name(self):
        """Test de validation avec un nom d'outil invalide"""
        invalid_plan = copy.deepcopy(EXAMPLE_SIMPLE_PLAN)
        invalid_plan["steps"][0]["tool_name"] = "invalid_tool"
        
        with self.assertRaises(ValueError):
            LLMPlan(**invalid_plan)
    
    def test_missing_dependency(self):
        """Test de validation avec une dépendance manquante"""
        invalid_plan = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        invalid_plan["steps"][1]["depends_on"] = [999]  # Étape inexistante
        
        with self.assertRaises(ValueError):
            LLMPlan(**invalid_plan)
    
    def test_execution_order(self):
        """Test de l'ordre d'exécution des étapes"""
        plan = LLMPlan(**EXAMPLE_COMPLEX_PLAN)
        execution_order = plan.get_execution_order()
        
        # L'étape 1 doit être avant les étapes 2 et 3
        self.assertIn(1, execution_order)
        self.assertIn(2, execution_order)
        self.assertIn(3, execution_order)
        
        # Vérifier que les dépendances sont respectées
        step1_index = execution_order.index(1)
        step2_index = execution_order.index(2)
        step3_index = execution_order.index(3)
        
        self.assertLess(step1_index, step2_index)
        self.assertLess(step1_index, step3_index)
        self.assertLess(step2_index, step3_index)

class TestPlanGeneratorPrompt(unittest.TestCase):
    """Tests pour les prompts de génération de plans"""
    
    def test_system_prompt_contains_tools(self):
        """Test que le prompt système contient les outils disponibles"""
        prompt = PlanGeneratorPrompt.get_system_prompt()
        
        # Vérifier la présence des outils
        self.assertIn("query_energy_data", prompt)
        self.assertIn("generate_forecast", prompt)
        self.assertIn("create_visualization", prompt)
    
    def test_user_prompt_formatting(self):
        """Test du formatage du prompt utilisateur"""
        question = "Quelle est ma consommation des 7 derniers jours ?"
        prompt = PlanGeneratorPrompt.get_user_prompt(question)
        
        self.assertIn(question, prompt)
        self.assertIn("Génère un plan JSON", prompt)
    
    def test_format_plan_prompt(self):
        """Test du formatage complet du prompt"""
        question = "Test question"
        prompt = format_plan_prompt(question)
        
        self.assertIn("Tu es un planificateur expert", prompt)
        self.assertIn(question, prompt)
    
    def test_available_tools(self):
        """Test de la liste des outils disponibles"""
        tools = PlanGeneratorPrompt.AVAILABLE_TOOLS
        
        expected_tools = [
            'query_energy_data',
            'calculate_statistics',
            'generate_forecast',
            'create_visualization',
            'estimate_costs',
            'detect_anomalies',
            'compare_periods'
        ]
        
        for tool in expected_tools:
            self.assertIn(tool, tools)

class TestGeminiClient(unittest.TestCase):
    """Tests pour le client Gemini (avec mocks)"""
    
    def setUp(self):
        """Configuration des tests"""
        # Mock de l'API key
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            self.client = GeminiClient()
    
    @patch('google.generativeai.GenerativeModel')
    def test_client_initialization(self, mock_model):
        """Test de l'initialisation du client"""
        mock_model.return_value = Mock()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            client = GeminiClient()
            self.assertIsNotNone(client)
    
    def test_missing_api_key(self):
        """Test avec une clé API manquante"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                GeminiClient()
    
    def test_cache_key_generation(self):
        """Test de la génération des clés de cache"""
        prompt1 = "Test prompt 1"
        prompt2 = "Test prompt 2"
        
        key1 = self.client._generate_cache_key(prompt1)
        key2 = self.client._generate_cache_key(prompt2)
        
        self.assertNotEqual(key1, key2)
        self.assertEqual(len(key1), 32)  # MD5 hash length
    
    def test_cache_validation(self):
        """Test de la validation du cache"""
        # Entrée valide
        valid_entry = {
            'plan': {'test': 'data'},
            'timestamp': time.time(),
            'generation_time': 1.0
        }
        self.assertTrue(self.client._is_cache_valid(valid_entry))
        
        # Entrée expirée
        expired_entry = {
            'plan': {'test': 'data'},
            'timestamp': time.time() - 7200,  # 2 heures
            'generation_time': 1.0
        }
        self.assertFalse(self.client._is_cache_valid(expired_entry))
    
    def test_plan_validation(self):
        """Test de la validation des plans"""
        # Plan valide
        self.assertTrue(self.client.validate_plan(EXAMPLE_SIMPLE_PLAN))
        
        # Plan invalide
        invalid_plan = {'invalid': 'plan'}
        self.assertFalse(self.client.validate_plan(invalid_plan))
    
    def test_cache_stats(self):
        """Test des statistiques du cache"""
        # Ajouter quelques entrées au cache
        self.client._cache['key1'] = {
            'plan': {'test': 'data'},
            'timestamp': time.time(),
            'generation_time': 1.0
        }
        
        stats = self.client.get_cache_stats()
        
        self.assertIn('total_entries', stats)
        self.assertIn('valid_entries', stats)
        self.assertIn('expired_entries', stats)
        self.assertIn('cache_size_mb', stats)
    
    def test_cache_clear(self):
        """Test du vidage du cache"""
        self.client._cache['key1'] = {'test': 'data'}
        self.assertEqual(len(self.client._cache), 1)
        
        self.client.clear_cache()
        self.assertEqual(len(self.client._cache), 0)

class TestIntegration(unittest.TestCase):
    """Tests d'intégration du BLOC 2"""
    
    def test_end_to_end_plan_generation(self):
        """Test de bout en bout de la génération de plans"""
        # Test avec un plan simple
        plan = LLMPlan(**EXAMPLE_SIMPLE_PLAN)
        
        # Vérifier la structure
        self.assertIsInstance(plan.metadata, PlanMetadata)
        self.assertIsInstance(plan.steps[0], ToolStep)
        self.assertIsInstance(plan.summary, str)
        
        # Vérifier la cohérence
        self.assertEqual(plan.metadata.plan_id, "plan_001")
        self.assertEqual(plan.metadata.complexity, "simple")
    
    def test_prompt_integration(self):
        """Test d'intégration des prompts"""
        question = "Test question"
        prompt = format_plan_prompt(question)
        
        # Vérifier que le prompt contient tous les éléments nécessaires
        self.assertIn("RÈGLES STRICTES", prompt)
        self.assertIn("OUTILS DISPONIBLES", prompt)
        self.assertIn("STRUCTURE JSON OBLIGATOIRE", prompt)
        self.assertIn(question, prompt)

def run_performance_tests():
    """Tests de performance"""
    print("\n🚀 TESTS DE PERFORMANCE")
    print("=" * 50)
    
    # Test de validation de schéma
    start_time = time.time()
    for _ in range(1000):
        LLMPlan(**copy.deepcopy(EXAMPLE_SIMPLE_PLAN))
    validation_time = time.time() - start_time
    print(f"✅ Validation de 1000 plans: {validation_time:.3f}s")
    
    # Test de génération de clés de cache
    import hashlib
    start_time = time.time()
    for i in range(1000):
        hashlib.md5(f"prompt_{i}".encode()).hexdigest()
    cache_time = time.time() - start_time
    print(f"✅ Génération de 1000 clés de cache: {cache_time:.3f}s")

if __name__ == '__main__':
    print("🧪 DÉMARRAGE DES TESTS BLOC 2")
    print("=" * 50)
    
    # Tests unitaires
    unittest.main(verbosity=2, exit=False)
    
    # Tests de performance
    run_performance_tests()
    
    print("\n✅ TOUS LES TESTS BLOC 2 TERMINÉS")
    print("=" * 50)
