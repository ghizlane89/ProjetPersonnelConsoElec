#!/usr/bin/env python3
"""
Test UAT Performance
Validation des seuils de performance (< 5 secondes)
"""

import sys
import os
import time
import json
import statistics
from datetime import datetime
from typing import Dict, Any, List

# Ajouter les chemins pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(os.path.join(parent_dir, 'llm_planner'))
sys.path.append(os.path.join(parent_dir, 'mcp_server'))

# Questions de test pour la performance
PERFORMANCE_QUESTIONS = [
    "Quelle est ma consommation d'électricité hier ?",
    "Combien ai-je consommé ce mois-ci ?",
    "Quelle est ma consommation moyenne par jour ?",
    "Quelle sera ma consommation demain ?",
    "Quelle sera ma consommation la semaine prochaine ?",
    "Quelle est ma consommation par heure ?",
    "Quelle est ma consommation par semaine ?",
    "Quelle sera ma consommation le mois prochain ?",
    "Quelle est ma consommation par minute ?",
    "Quelle est ma consommation par année ?"
]

def test_single_performance(question: str, iteration: int) -> Dict[str, Any]:
    """Test de performance d'une question"""
    start_time = time.time()
    
    try:
        from llm_planner.core.gemini_client import GeminiClient
        from mcp_server.core.mcp_server import MCPServer
        
        client = GeminiClient()
        server = MCPServer()
        
        # Générer le plan
        plan = client.generate_plan(question)
        
        # Exécuter le plan
        result = server.execute_plan(plan)
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "iteration": iteration,
            "question": question,
            "success": True,
            "duration": duration,
            "within_limit": duration < 5.0,
            "error": None
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "iteration": iteration,
            "question": question,
            "success": False,
            "duration": duration,
            "within_limit": False,
            "error": str(e)
        }

def test_performance_benchmark(iterations: int = 3):
    """Test de performance avec plusieurs itérations"""
    print("🧪 TEST UAT PERFORMANCE")
    print("=" * 50)
    print(f"⏰ Début du test : {datetime.now()}")
    print(f"📊 Itérations par question : {iterations}")
    print(f"📋 Questions de test : {len(PERFORMANCE_QUESTIONS)}")
    print()
    
    all_results = []
    total_start_time = time.time()
    
    for question_idx, question in enumerate(PERFORMANCE_QUESTIONS, 1):
        print(f"🔍 Question {question_idx}/{len(PERFORMANCE_QUESTIONS)} : {question}")
        
        question_results = []
        
        for iteration in range(1, iterations + 1):
            result = test_single_performance(question, iteration)
            question_results.append(result)
            all_results.append(result)
            
            if result["success"]:
                print(f"   Itération {iteration} : {result['duration']:.2f}s {'✅' if result['within_limit'] else '⚠️'}")
            else:
                print(f"   Itération {iteration} : ÉCHEC - {result['error']}")
        
        # Statistiques par question
        successful_results = [r for r in question_results if r["success"]]
        if successful_results:
            avg_duration = statistics.mean([r["duration"] for r in successful_results])
            min_duration = min([r["duration"] for r in successful_results])
            max_duration = max([r["duration"] for r in successful_results])
            within_limit_count = sum(1 for r in successful_results if r["within_limit"])
            
            print(f"   📊 Moyenne : {avg_duration:.2f}s | Min : {min_duration:.2f}s | Max : {max_duration:.2f}s")
            print(f"   📊 Dans la limite : {within_limit_count}/{len(successful_results)}")
        
        print()
        
        # Pause entre les questions
        if question_idx < len(PERFORMANCE_QUESTIONS):
            time.sleep(0.5)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    return all_results, total_duration

def analyze_performance_results(results: List[Dict[str, Any]], total_duration: float):
    """Analyse des résultats de performance"""
    print("📊 ANALYSE DES RÉSULTATS DE PERFORMANCE")
    print("=" * 50)
    
    # Statistiques générales
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - successful_tests
    
    # Statistiques de performance
    successful_durations = [r["duration"] for r in results if r["success"]]
    
    if successful_durations:
        avg_duration = statistics.mean(successful_durations)
        median_duration = statistics.median(successful_durations)
        min_duration = min(successful_durations)
        max_duration = max(successful_durations)
        std_duration = statistics.stdev(successful_durations) if len(successful_durations) > 1 else 0
        
        within_limit_count = sum(1 for r in results if r.get("within_limit", False))
        within_limit_rate = (within_limit_count / successful_tests) * 100 if successful_tests > 0 else 0
        
        # Seuils de performance
        p95_duration = statistics.quantiles(successful_durations, n=20)[18] if len(successful_durations) >= 5 else max_duration
        p99_duration = statistics.quantiles(successful_durations, n=100)[98] if len(successful_durations) >= 5 else max_duration
        
        print(f"📋 Statistiques générales :")
        print(f"   - Tests totaux : {total_tests}")
        print(f"   - Tests réussis : {successful_tests}")
        print(f"   - Tests échoués : {failed_tests}")
        print(f"   - Taux de succès : {(successful_tests/total_tests)*100:.1f}%")
        print()
        
        print(f"⏱️ Statistiques de performance :")
        print(f"   - Temps moyen : {avg_duration:.2f}s")
        print(f"   - Temps médian : {median_duration:.2f}s")
        print(f"   - Temps min : {min_duration:.2f}s")
        print(f"   - Temps max : {max_duration:.2f}s")
        print(f"   - Écart-type : {std_duration:.2f}s")
        print(f"   - P95 : {p95_duration:.2f}s")
        print(f"   - P99 : {p99_duration:.2f}s")
        print()
        
        print(f"🎯 Seuils de performance :")
        print(f"   - Limite < 5s : {within_limit_count}/{successful_tests} ({within_limit_rate:.1f}%)")
        print(f"   - Temps total : {total_duration:.2f}s")
        print()
        
        # Analyse par question
        print(f"📊 Analyse par question :")
        for question in PERFORMANCE_QUESTIONS:
            question_results = [r for r in results if r["question"] == question and r["success"]]
            if question_results:
                question_avg = statistics.mean([r["duration"] for r in question_results])
                question_within_limit = sum(1 for r in question_results if r["within_limit"])
                print(f"   - {question[:40]}{'...' if len(question) > 40 else ''}")
                print(f"     Moyenne : {question_avg:.2f}s | Dans limite : {question_within_limit}/{len(question_results)}")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests/total_tests)*100,
            "avg_duration": avg_duration,
            "median_duration": median_duration,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "std_duration": std_duration,
            "p95_duration": p95_duration,
            "p99_duration": p99_duration,
            "within_limit_count": within_limit_count,
            "within_limit_rate": within_limit_rate,
            "total_duration": total_duration
        }
    else:
        print("❌ Aucun test réussi pour l'analyse de performance")
        return None

def save_performance_results(results: List[Dict[str, Any]], analysis: Dict[str, Any]):
    """Sauvegarde des résultats de performance"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sauvegarder les résultats détaillés
    results_file = f"tests_uat/performance_results_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Résultats sauvegardés : {results_file}")

def main():
    """Test principal de performance"""
    # Test de performance
    results, total_duration = test_performance_benchmark(iterations=3)
    
    # Analyse des résultats
    analysis = analyze_performance_results(results, total_duration)
    
    if analysis:
        # Sauvegarde
        save_performance_results(results, analysis)
        
        # Résumé final
        print("📋 RÉSUMÉ FINAL DE PERFORMANCE")
        print("=" * 50)
        print(f"Tests réussis : {analysis['successful_tests']}/{analysis['total_tests']}")
        print(f"Taux de succès : {analysis['success_rate']:.1f}%")
        print(f"Temps moyen : {analysis['avg_duration']:.2f}s")
        print(f"Performance : {analysis['within_limit_rate']:.1f}% dans la limite")
        print(f"Temps total : {analysis['total_duration']:.2f}s")
        
        # Seuils de validation
        success_threshold = 0.9  # 90% de succès minimum
        performance_threshold = 0.8  # 80% dans la limite de temps
        avg_duration_threshold = 3.0  # Temps moyen < 3s
        
        success_ok = analysis['success_rate'] >= success_threshold
        performance_ok = analysis['within_limit_rate'] >= performance_threshold
        duration_ok = analysis['avg_duration'] <= avg_duration_threshold
        
        print(f"\n🎯 SEUILS DE VALIDATION :")
        print(f"   - Succès ({success_threshold*100}%) : {'✅' if success_ok else '❌'}")
        print(f"   - Performance ({performance_threshold*100}%) : {'✅' if performance_ok else '❌'}")
        print(f"   - Temps moyen (<{avg_duration_threshold}s) : {'✅' if duration_ok else '❌'}")
        
        global_success = success_ok and performance_ok and duration_ok
        
        print(f"\n🎯 STATUT GLOBAL : {'✅ SUCCÈS' if global_success else '❌ ÉCHEC'}")
        
        return global_success
    else:
        print("❌ ÉCHEC : Aucun test réussi")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
