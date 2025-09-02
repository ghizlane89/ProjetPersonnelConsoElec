#!/usr/bin/env python3
"""
🧪 TESTS PUSHÉS BLOC 2 - INTELLIGENCE LAYER
==========================================

Tests avancés de robustesse, performance et edge cases.
Validation approfondie des critères d'acceptation.

Tests inclus :
- Tests de robustesse (erreurs, edge cases)
- Tests de performance (charge, mémoire)
- Tests de sécurité (injection, validation)
- Tests d'intégration avancés
- Tests de cache avancés
"""

import sys
import os
import json
import time
import copy
import hashlib
import unittest
import threading
import concurrent.futures
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_planner.models.plan_schema import LLMPlan, ToolStep, PlanMetadata, EXAMPLE_SIMPLE_PLAN, EXAMPLE_COMPLEX_PLAN
from llm_planner.prompts.plan_generator_prompt import PlanGeneratorPrompt, format_plan_prompt
from llm_planner.core.gemini_client import GeminiClient

class TestRobustness(unittest.TestCase):
    """Tests de robustesse et edge cases"""
    
    def test_malformed_json_response(self):
        """Test avec une réponse JSON malformée du LLM"""
        client = GeminiClient()
        
        # Mock d'une réponse malformée
        mock_response = Mock()
        mock_response.text = '{"invalid": json}'
        
        with patch.object(client.model, 'generate_content', return_value=mock_response):
            with self.assertRaises(ValueError):
                client.generate_plan("Test question", use_cache=False)
    
    def test_empty_llm_response(self):
        """Test avec une réponse vide du LLM"""
        client = GeminiClient()
        
        mock_response = Mock()
        mock_response.text = ""
        
        with patch.object(client.model, 'generate_content', return_value=mock_response):
            with self.assertRaises(ValueError):
                client.generate_plan("Test question", use_cache=False)
    
    def test_llm_api_error(self):
        """Test avec une erreur API du LLM"""
        client = GeminiClient()
        
        with patch.object(client.model, 'generate_content', side_effect=Exception("API Error")):
            with self.assertRaises(Exception):
                client.generate_plan("Test question", use_cache=False)
    
    def test_extremely_large_plan(self):
        """Test avec un plan extrêmement volumineux"""
        large_plan = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        
        # Ajouter 100 étapes supplémentaires
        for i in range(4, 104):
            large_plan["steps"].append({
                "step_id": i,
                "tool_name": "query_energy_data",
                "description": f"Étape {i}",
                "parameters": {"period": "1d"},
                "depends_on": [i-1] if i > 4 else None
            })
        
        # Test de validation
        plan = LLMPlan(**large_plan)
        self.assertEqual(len(plan.steps), 103)
        
        # Test de performance
        start_time = time.time()
        execution_order = plan.get_execution_order()
        execution_time = time.time() - start_time
        
        self.assertLess(execution_time, 1.0)  # Moins d'1 seconde
        self.assertEqual(len(execution_order), 103)
    
    def test_circular_dependencies(self):
        """Test avec des dépendances circulaires"""
        circular_plan = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        circular_plan["steps"][0]["depends_on"] = [3]  # Créer un cycle
        
        with self.assertRaises(ValueError):
            LLMPlan(**circular_plan)
    
    def test_duplicate_step_ids(self):
        """Test avec des IDs d'étapes dupliqués"""
        duplicate_plan = copy.deepcopy(EXAMPLE_SIMPLE_PLAN)
        duplicate_plan["steps"].append(duplicate_plan["steps"][0].copy())
        
        with self.assertRaises(ValueError):
            LLMPlan(**duplicate_plan)

class TestPerformance(unittest.TestCase):
    """Tests de performance avancés"""
    
    def test_cache_performance_under_load(self):
        """Test de performance du cache sous charge"""
        client = GeminiClient()
        
        # Générer 1000 clés de cache différentes
        start_time = time.time()
        cache_keys = []
        for i in range(1000):
            prompt = f"Question {i} avec du contenu variable {hashlib.md5(str(i).encode()).hexdigest()}"
            cache_key = client._generate_cache_key(prompt)
            cache_keys.append(cache_key)
        
        generation_time = time.time() - start_time
        self.assertLess(generation_time, 0.1)  # Moins de 100ms
        
        # Vérifier l'unicité des clés
        unique_keys = set(cache_keys)
        self.assertEqual(len(unique_keys), 1000)
    
    def test_concurrent_cache_access(self):
        """Test d'accès concurrent au cache"""
        client = GeminiClient()
        
        def cache_operation(thread_id):
            for i in range(100):
                prompt = f"Thread {thread_id} - Question {i}"
                cache_key = client._generate_cache_key(prompt)
                client._cache[cache_key] = {
                    'plan': {'thread': thread_id, 'question': i},
                    'timestamp': time.time(),
                    'generation_time': 0.001
                }
        
        # Exécuter 5 threads en parallèle
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(cache_operation, i) for i in range(5)]
            concurrent.futures.wait(futures)
        
        # Vérifier qu'il n'y a pas de corruption
        self.assertGreater(len(client._cache), 0)
        for entry in client._cache.values():
            self.assertIn('plan', entry)
            self.assertIn('timestamp', entry)
    
    def test_memory_usage_large_cache(self):
        """Test d'utilisation mémoire avec un gros cache"""
        client = GeminiClient()
        
        # Remplir le cache avec 10000 entrées
        for i in range(10000):
            prompt = f"Question {i} avec contenu détaillé"
            cache_key = client._generate_cache_key(prompt)
            client._cache[cache_key] = {
                'plan': {
                    'metadata': {'plan_id': f'plan_{i}'},
                    'steps': [{'step_id': 1, 'tool_name': 'query_energy_data'}],
                    'summary': f'Plan pour question {i}'
                },
                'timestamp': time.time(),
                'generation_time': 0.001
            }
        
        # Vérifier les statistiques
        stats = client.get_cache_stats()
        self.assertEqual(stats['total_entries'], 10000)
        self.assertGreater(stats['cache_size_mb'], 0)
        
        # Nettoyer
        client.clear_cache()
        self.assertEqual(len(client._cache), 0)

class TestSecurity(unittest.TestCase):
    """Tests de sécurité et validation"""
    
    def test_sql_injection_in_prompt(self):
        """Test d'injection SQL dans les prompts"""
        malicious_questions = [
            "'; DROP TABLE energy_data; --",
            "SELECT * FROM energy_data WHERE 1=1;",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for question in malicious_questions:
            prompt = format_plan_prompt(question)
            # Le prompt doit être généré sans erreur
            self.assertIsInstance(prompt, str)
            self.assertIn(question, prompt)
    
    def test_xss_in_prompt(self):
        """Test d'injection XSS dans les prompts"""
        malicious_questions = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for question in malicious_questions:
            prompt = format_plan_prompt(question)
            self.assertIsInstance(prompt, str)
            self.assertIn(question, prompt)
    
    def test_plan_validation_against_malicious_input(self):
        """Test de validation contre des entrées malveillantes"""
        malicious_plans = [
            {"malicious": "data"},
            {"metadata": None, "steps": [], "summary": ""},
            {"metadata": {}, "steps": [{"step_id": 1, "tool_name": "malicious_tool"}], "summary": ""},
            {"metadata": {}, "steps": [], "summary": None}
        ]
        
        client = GeminiClient()
        for plan in malicious_plans:
            self.assertFalse(client.validate_plan(plan))
    
    def test_tool_name_validation(self):
        """Test de validation stricte des noms d'outils"""
        invalid_tools = [
            "query_energy_data'",
            "generate_forecast; DROP TABLE;",
            "create_visualization<script>",
            "estimate_costs' OR '1'='1"
        ]
        
        for tool in invalid_tools:
            with self.assertRaises(ValueError):
                ToolStep(
                    step_id=1,
                    tool_name=tool,
                    description="Test",
                    parameters={}
                )

class TestIntegrationAdvanced(unittest.TestCase):
    """Tests d'intégration avancés"""
    
    def test_end_to_end_plan_generation_simulation(self):
        """Simulation complète de génération de plan"""
        # Simuler une question utilisateur
        question = "Quelle est ma consommation des 30 derniers jours et prévois pour les 7 prochains ?"
        
        # Générer le prompt
        prompt = format_plan_prompt(question)
        
        # Vérifier la structure du prompt
        self.assertIn("RÈGLES STRICTES", prompt)
        self.assertIn("OUTILS DISPONIBLES", prompt)
        self.assertIn("STRUCTURE JSON OBLIGATOIRE", prompt)
        self.assertIn(question, prompt)
        
        # Simuler une réponse LLM (exemple complexe)
        simulated_plan = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        simulated_plan["metadata"]["plan_id"] = "plan_simulated"
        simulated_plan["metadata"]["question_type"] = "forecast"
        
        # Valider le plan
        plan = LLMPlan(**simulated_plan)
        self.assertEqual(plan.metadata.question_type, "forecast")
        self.assertEqual(len(plan.steps), 3)
        
        # Vérifier l'ordre d'exécution
        execution_order = plan.get_execution_order()
        self.assertEqual(execution_order, [1, 2, 3])
    
    def test_cache_integration_with_plan_generation(self):
        """Test d'intégration cache avec génération de plans"""
        client = GeminiClient()
        
        # Simuler une génération de plan
        question = "Test question for cache"
        prompt = format_plan_prompt(question)
        cache_key = client._generate_cache_key(prompt)
        
        # Ajouter au cache
        test_plan = copy.deepcopy(EXAMPLE_SIMPLE_PLAN)
        client._cache[cache_key] = {
            'plan': test_plan,
            'timestamp': time.time(),
            'generation_time': 0.001
        }
        
        # Vérifier la récupération
        self.assertIn(cache_key, client._cache)
        cached_entry = client._cache[cache_key]
        self.assertEqual(cached_entry['plan'], test_plan)
    
    def test_prompt_variations(self):
        """Test avec différentes variations de questions"""
        questions = [
            "Quelle est ma consommation ?",
            "Montre-moi l'historique de consommation",
            "Je veux voir mes données énergétiques",
            "Prévois ma consommation future",
            "Compare ma consommation avec la semaine dernière",
            "Détecte les anomalies dans ma consommation",
            "Calcule le coût de ma consommation"
        ]
        
        for question in questions:
            prompt = format_plan_prompt(question)
            self.assertIsInstance(prompt, str)
            self.assertIn(question, prompt)
            self.assertIn("RÈGLES STRICTES", prompt)

class TestEdgeCases(unittest.TestCase):
    """Tests des cas limites"""
    
    def test_empty_question(self):
        """Test avec une question vide"""
        prompt = format_plan_prompt("")
        self.assertIsInstance(prompt, str)
        self.assertIn("Question utilisateur : \"\"", prompt)
    
    def test_very_long_question(self):
        """Test avec une question très longue"""
        long_question = "A" * 10000  # 10k caractères
        prompt = format_plan_prompt(long_question)
        self.assertIsInstance(prompt, str)
        self.assertIn(long_question, prompt)
    
    def test_special_characters_in_question(self):
        """Test avec des caractères spéciaux"""
        special_question = "Consommation avec émojis 🏠⚡💡 et caractères spéciaux: éàçù€£¥"
        prompt = format_plan_prompt(special_question)
        self.assertIsInstance(prompt, str)
        self.assertIn(special_question, prompt)
    
    def test_unicode_characters(self):
        """Test avec des caractères Unicode"""
        unicode_question = "Consommation avec Unicode: αβγδε, 中文, русский, العربية"
        prompt = format_plan_prompt(unicode_question)
        self.assertIsInstance(prompt, str)
        self.assertIn(unicode_question, prompt)
    
    def test_plan_with_maximum_complexity(self):
        """Test avec un plan de complexité maximale"""
        max_complex_plan = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        max_complex_plan["metadata"]["complexity"] = "complex"
        max_complex_plan["metadata"]["estimated_duration"] = 60
        
        plan = LLMPlan(**max_complex_plan)
        self.assertEqual(plan.metadata.complexity, "complex")
        self.assertEqual(plan.metadata.estimated_duration, 60)

def run_stress_tests():
    """Tests de stress"""
    print("\n🔥 TESTS DE STRESS")
    print("=" * 50)
    
    # Test de stress sur la validation de plans
    start_time = time.time()
    for i in range(10000):
        plan_data = copy.deepcopy(EXAMPLE_SIMPLE_PLAN)
        plan_data["metadata"]["plan_id"] = f"stress_test_{i}"
        LLMPlan(**plan_data)
    stress_time = time.time() - start_time
    print(f"✅ Validation de 10000 plans (stress): {stress_time:.3f}s")
    
    # Test de stress sur la génération de clés de cache
    start_time = time.time()
    for i in range(10000):
        hashlib.md5(f"stress_prompt_{i}".encode()).hexdigest()
    cache_stress_time = time.time() - start_time
    print(f"✅ Génération de 10000 clés de cache (stress): {cache_stress_time:.3f}s")
    
    # Test de stress sur les prompts
    start_time = time.time()
    for i in range(1000):
        format_plan_prompt(f"Stress question {i}")
    prompt_stress_time = time.time() - start_time
    print(f"✅ Génération de 1000 prompts (stress): {prompt_stress_time:.3f}s")

def run_memory_tests():
    """Tests de mémoire"""
    print("\n💾 TESTS DE MÉMOIRE")
    print("=" * 50)
    
    import psutil
    import gc
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Créer beaucoup d'objets
    plans = []
    for i in range(1000):
        plan_data = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        plan_data["metadata"]["plan_id"] = f"memory_test_{i}"
        plan = LLMPlan(**plan_data)
        plans.append(plan)
    
    memory_after_creation = process.memory_info().rss / 1024 / 1024
    memory_used = memory_after_creation - initial_memory
    
    print(f"✅ Mémoire utilisée pour 1000 plans: {memory_used:.2f} MB")
    
    # Nettoyer
    del plans
    gc.collect()
    
    memory_after_cleanup = process.memory_info().rss / 1024 / 1024
    memory_cleaned = memory_after_creation - memory_after_cleanup
    
    print(f"✅ Mémoire libérée après nettoyage: {memory_cleaned:.2f} MB")

if __name__ == '__main__':
    print("🧪 DÉMARRAGE DES TESTS PUSHÉS BLOC 2")
    print("=" * 60)
    
    # Tests unitaires avancés
    unittest.main(verbosity=2, exit=False)
    
    # Tests de stress
    run_stress_tests()
    
    # Tests de mémoire
    try:
        run_memory_tests()
    except ImportError:
        print("⚠️ psutil non installé, tests de mémoire ignorés")
    
    print("\n✅ TOUS LES TESTS PUSHÉS BLOC 2 TERMINÉS")
    print("=" * 60)





