#!/usr/bin/env python3
"""
🔥 TESTS DE CHARGE RÉELLE - BLOC 2
==================================

Tests de charge réelle avec des questions variées.
Simulation d'utilisation intensive du système.

Tests inclus :
- Tests de charge avec questions réelles
- Tests de performance en conditions réelles
- Tests de robustesse avec données variées
"""

import sys
import os
import time
import copy
import random
from typing import List, Dict, Any

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_planner.models.plan_schema import LLMPlan, EXAMPLE_SIMPLE_PLAN, EXAMPLE_COMPLEX_PLAN
from llm_planner.prompts.plan_generator_prompt import format_plan_prompt
from llm_planner.core.gemini_client import GeminiClient

# Questions réelles pour les tests de charge
REAL_QUESTIONS = [
    "Quelle est ma consommation électrique des 7 derniers jours ?",
    "Montre-moi l'historique de ma consommation sur le mois dernier",
    "Prévois ma consommation pour les 30 prochains jours",
    "Compare ma consommation de cette semaine avec la semaine dernière",
    "Détecte les anomalies dans ma consommation électrique",
    "Calcule le coût de ma consommation du mois dernier",
    "Quelle est ma consommation moyenne par jour de la semaine ?",
    "Montre-moi les pics de consommation de ce mois",
    "Prévois ma facture électrique pour le trimestre",
    "Analyse ma consommation par heure de la journée",
    "Compare ma consommation avec la moyenne nationale",
    "Détecte les périodes de surconsommation",
    "Calcule mes économies potentielles",
    "Montre-moi ma consommation par appareil",
    "Prévois ma consommation pour l'été prochain",
    "Analyse l'impact de la météo sur ma consommation",
    "Détecte les fuites électriques potentielles",
    "Calcule mon empreinte carbone électrique",
    "Montre-moi ma consommation en temps réel",
    "Prévois ma consommation pour les fêtes de fin d'année"
]

def run_load_test_with_real_questions():
    """Test de charge avec des questions réelles"""
    print("\n🔥 TEST DE CHARGE AVEC QUESTIONS RÉELLES")
    print("=" * 60)
    
    # Test de génération de prompts
    print("📝 Test de génération de prompts...")
    start_time = time.time()
    
    prompts = []
    for i, question in enumerate(REAL_QUESTIONS):
        prompt = format_plan_prompt(question)
        prompts.append(prompt)
        
        if (i + 1) % 5 == 0:
            elapsed = time.time() - start_time
            print(f"   ✅ {i + 1}/20 prompts générés en {elapsed:.3f}s")
    
    total_time = time.time() - start_time
    print(f"✅ Génération de {len(prompts)} prompts: {total_time:.3f}s")
    print(f"📊 Temps moyen par prompt: {total_time/len(prompts):.3f}s")
    
    # Test de validation de plans
    print("\n🔍 Test de validation de plans...")
    start_time = time.time()
    
    valid_plans = 0
    for i in range(100):
        # Alterner entre plans simples et complexes
        if i % 2 == 0:
            plan_data = copy.deepcopy(EXAMPLE_SIMPLE_PLAN)
            plan_data["metadata"]["plan_id"] = f"load_test_simple_{i}"
        else:
            plan_data = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
            plan_data["metadata"]["plan_id"] = f"load_test_complex_{i}"
        
        try:
            plan = LLMPlan(**plan_data)
            valid_plans += 1
        except Exception as e:
            print(f"   ❌ Plan {i} invalide: {e}")
    
    total_time = time.time() - start_time
    print(f"✅ Validation de {valid_plans}/100 plans: {total_time:.3f}s")
    print(f"📊 Taux de succès: {valid_plans/100*100:.1f}%")
    
    # Test de performance du cache
    print("\n💾 Test de performance du cache...")
    client = GeminiClient()
    
    # Remplir le cache avec des données variées
    start_time = time.time()
    for i in range(1000):
        question = f"Question de charge {i} avec contenu variable"
        prompt = format_plan_prompt(question)
        cache_key = client._generate_cache_key(prompt)
        
        # Simuler différents types de plans
        plan_type = i % 3
        if plan_type == 0:
            plan_data = copy.deepcopy(EXAMPLE_SIMPLE_PLAN)
        elif plan_type == 1:
            plan_data = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        else:
            # Plan moyen
            plan_data = copy.deepcopy(EXAMPLE_SIMPLE_PLAN)
            plan_data["steps"].append({
                "step_id": 2,
                "tool_name": "calculate_statistics",
                "description": "Calculer des statistiques",
                "parameters": {"metrics": ["mean", "max"]},
                "depends_on": [1]
            })
        
        client._cache[cache_key] = {
            'plan': plan_data,
            'timestamp': time.time(),
            'generation_time': random.uniform(0.1, 2.0)
        }
    
    fill_time = time.time() - start_time
    print(f"✅ Remplissage du cache (1000 entrées): {fill_time:.3f}s")
    
    # Test de récupération du cache
    start_time = time.time()
    cache_hits = 0
    for i in range(500):
        question = f"Question de charge {i % 1000}"
        prompt = format_plan_prompt(question)
        cache_key = client._generate_cache_key(prompt)
        
        if cache_key in client._cache:
            cache_hits += 1
    
    retrieval_time = time.time() - start_time
    print(f"✅ Récupération du cache (500 requêtes): {retrieval_time:.3f}s")
    print(f"📊 Taux de hit: {cache_hits/500*100:.1f}%")
    
    # Nettoyer
    client.clear_cache()

def run_stress_test_with_variations():
    """Test de stress avec variations de données"""
    print("\n🔥 TEST DE STRESS AVEC VARIATIONS")
    print("=" * 60)
    
    # Test avec des plans de différentes tailles
    print("📊 Test avec plans de différentes tailles...")
    
    plan_sizes = [1, 5, 10, 20, 50]
    for size in plan_sizes:
        start_time = time.time()
        
        # Créer un plan avec le nombre d'étapes spécifié
        plan_data = copy.deepcopy(EXAMPLE_SIMPLE_PLAN)
        plan_data["steps"] = []
        
        for i in range(size):
            step = {
                "step_id": i + 1,
                "tool_name": "query_energy_data",
                "description": f"Étape {i + 1}",
                "parameters": {"period": f"{i+1}d"},
                "depends_on": [i] if i > 0 else None
            }
            plan_data["steps"].append(step)
        
        # Valider le plan
        plan = LLMPlan(**plan_data)
        validation_time = time.time() - start_time
        
        # Calculer l'ordre d'exécution
        start_time = time.time()
        execution_order = plan.get_execution_order()
        execution_time = time.time() - start_time
        
        print(f"   ✅ Plan {size} étapes - Validation: {validation_time:.3f}s, Exécution: {execution_time:.3f}s")
    
    # Test avec des questions de différentes longueurs
    print("\n📏 Test avec questions de différentes longueurs...")
    
    question_lengths = [10, 50, 100, 200, 500]
    for length in question_lengths:
        question = "A" * length
        start_time = time.time()
        
        for _ in range(100):
            prompt = format_plan_prompt(question)
        
        total_time = time.time() - start_time
        print(f"   ✅ Question {length} caractères - 100 prompts: {total_time:.3f}s")

def run_edge_case_stress_test():
    """Test de stress avec cas limites"""
    print("\n🔥 TEST DE STRESS - CAS LIMITES")
    print("=" * 60)
    
    # Test avec des caractères spéciaux
    print("🔤 Test avec caractères spéciaux...")
    special_chars = [
        "Consommation avec émojis 🏠⚡💡",
        "Question avec Unicode: αβγδε",
        "Caractères spéciaux: éàçù€£¥",
        "Question avec HTML: <b>test</b>",
        "Question avec SQL: SELECT * FROM data",
        "Question avec JavaScript: alert('test')"
    ]
    
    start_time = time.time()
    for char_set in special_chars:
        for i in range(50):
            question = f"{char_set} - Variation {i}"
            prompt = format_plan_prompt(question)
    
    total_time = time.time() - start_time
    print(f"✅ 300 prompts avec caractères spéciaux: {total_time:.3f}s")
    
    # Test avec des plans complexes
    print("\n🔄 Test avec plans complexes...")
    
    complex_plans = []
    for i in range(100):
        plan_data = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        plan_data["metadata"]["plan_id"] = f"complex_{i}"
        plan_data["metadata"]["estimated_duration"] = random.randint(5, 60)
        
        # Ajouter des étapes aléatoires
        num_steps = random.randint(3, 10)
        plan_data["steps"] = []
        
        for j in range(num_steps):
            tools = ["query_energy_data", "calculate_statistics", "generate_forecast", 
                    "create_visualization", "estimate_costs", "detect_anomalies"]
            step = {
                "step_id": j + 1,
                "tool_name": random.choice(tools),
                "description": f"Étape complexe {j + 1}",
                "parameters": {"param": f"value_{j}"},
                "depends_on": [j] if j > 0 else None
            }
            plan_data["steps"].append(step)
        
        complex_plans.append(plan_data)
    
    start_time = time.time()
    valid_complex = 0
    for plan_data in complex_plans:
        try:
            plan = LLMPlan(**plan_data)
            execution_order = plan.get_execution_order()
            valid_complex += 1
        except Exception as e:
            pass
    
    total_time = time.time() - start_time
    print(f"✅ {valid_complex}/100 plans complexes validés: {total_time:.3f}s")

def run_memory_stress_test():
    """Test de stress mémoire"""
    print("\n💾 TEST DE STRESS MÉMOIRE")
    print("=" * 60)
    
    # Créer beaucoup d'objets en mémoire
    print("📦 Test de création d'objets...")
    
    plans = []
    start_time = time.time()
    
    for i in range(5000):
        plan_data = copy.deepcopy(EXAMPLE_COMPLEX_PLAN)
        plan_data["metadata"]["plan_id"] = f"memory_{i}"
        plan = LLMPlan(**plan_data)
        plans.append(plan)
        
        if (i + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"   ✅ {i + 1} plans créés en {elapsed:.3f}s")
    
    creation_time = time.time() - start_time
    print(f"✅ Création de {len(plans)} plans: {creation_time:.3f}s")
    
    # Test d'accès aux objets
    print("\n🔍 Test d'accès aux objets...")
    start_time = time.time()
    
    for i in range(0, len(plans), 100):
        plan = plans[i]
        execution_order = plan.get_execution_order()
        metadata = plan.metadata
        steps = plan.steps
    
    access_time = time.time() - start_time
    print(f"✅ Accès à {len(plans)} plans: {access_time:.3f}s")
    
    # Nettoyer la mémoire
    del plans
    import gc
    gc.collect()
    print("🗑️ Mémoire nettoyée")

if __name__ == '__main__':
    print("🔥 DÉMARRAGE DES TESTS DE CHARGE RÉELLE")
    print("=" * 70)
    
    # Tests de charge avec questions réelles
    run_load_test_with_real_questions()
    
    # Tests de stress avec variations
    run_stress_test_with_variations()
    
    # Tests de stress avec cas limites
    run_edge_case_stress_test()
    
    # Tests de stress mémoire
    run_memory_stress_test()
    
    print("\n✅ TOUS LES TESTS DE CHARGE RÉELLE TERMINÉS")
    print("=" * 70)





