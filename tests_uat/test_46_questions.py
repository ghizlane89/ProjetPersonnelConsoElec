#!/usr/bin/env python3
"""
Test UAT Complet - 46 Questions
Validation complète de toutes les fonctionnalités
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, Any, List

# Ajouter les chemins pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(os.path.join(parent_dir, 'llm_planner'))
sys.path.append(os.path.join(parent_dir, 'mcp_server'))

# Les 46 questions du cahier des charges
QUESTIONS_46 = [
    # Questions de base (1-10)
    "Quelle est ma consommation d'électricité hier ?",
    "Combien ai-je consommé ce mois-ci ?",
    "Quelle est ma consommation moyenne par jour ?",
    "Quelle sera ma consommation demain ?",
    "Quelle sera ma consommation la semaine prochaine ?",
    "Quelle est ma consommation par heure ?",
    "Quelle est ma consommation par semaine ?",
    "Quelle sera ma consommation le mois prochain ?",
    "Quelle est ma consommation par minute ?",
    "Quelle est ma consommation par année ?",
    
    # Questions de comparaison (11-20)
    "Ma consommation a-t-elle augmenté ce mois ?",
    "Ma consommation est-elle plus élevée que le mois dernier ?",
    "Ma consommation de jour est-elle plus élevée que la nuit ?",
    "Ma consommation en heures pleines est-elle plus élevée qu'en heures creuses ?",
    "Ma consommation du weekend est-elle différente de la semaine ?",
    "Ma consommation en été est-elle plus élevée qu'en hiver ?",
    "Ma consommation ce matin est-elle plus élevée qu'hier matin ?",
    "Ma consommation ce soir est-elle plus élevée qu'hier soir ?",
    "Ma consommation à midi est-elle plus élevée qu'à 18h ?",
    "Ma consommation cette semaine est-elle plus élevée que la semaine dernière ?",
    
    # Questions de coût (21-30)
    "Combien me coûte ma consommation d'électricité ?",
    "Quel est le coût de ma consommation hier ?",
    "Quel est le coût de ma consommation ce mois ?",
    "Quel sera le coût de ma consommation demain ?",
    "Quel est le coût moyen par jour ?",
    "Quel est le coût moyen par heure ?",
    "Quel est le coût moyen par semaine ?",
    "Quel sera le coût de ma consommation le mois prochain ?",
    "Quel est le coût de ma consommation en heures pleines ?",
    "Quel est le coût de ma consommation en heures creuses ?",
    
    # Questions d'analyse (31-40)
    "Quand est-ce que je consomme le plus ?",
    "Quand est-ce que je consomme le moins ?",
    "Quelles sont mes heures de pointe ?",
    "Quelles sont mes heures creuses ?",
    "Y a-t-il des anomalies dans ma consommation ?",
    "Quelles sont les causes de mes pics de consommation ?",
    "Quelles sont les causes de mes baisses de consommation ?",
    "Quelle est la tendance de ma consommation ?",
    "Ma consommation est-elle stable ?",
    "Ma consommation est-elle saisonnière ?",
    
    # Questions spéciales (41-43)
    "Si le coût de l'électricité est de 0,20 € le kilowattheure, de combien dois-je réduire ma consommation pour économiser 5 € le mois suivant ?",
    "Est-ce que ma consommation de nuit a augmenté récemment ?",
    "Anomalies dans les relevés d'intensité ?",
    
    # Questions de validation (44-46)
    "",  # Question vide
    "Quelle est la météo ?",  # Hors sujet
    "???"  # Question invalide
]

def test_single_question(question: str, question_number: int) -> Dict[str, Any]:
    """Test d'une question individuelle"""
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
            "question_number": question_number,
            "question": question,
            "success": True,
            "plan": plan,
            "result": result,
            "duration": duration,
            "within_limit": duration < 5.0,
            "error": None
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "question_number": question_number,
            "question": question,
            "success": False,
            "plan": None,
            "result": None,
            "duration": duration,
            "within_limit": False,
            "error": str(e)
        }

def test_all_questions():
    """Test de toutes les 46 questions"""
    print("🧪 TEST UAT COMPLET - 46 QUESTIONS")
    print("=" * 60)
    print(f"⏰ Début du test : {datetime.now()}")
    print()
    
    results = []
    total_start_time = time.time()
    
    for i, question in enumerate(QUESTIONS_46, 1):
        print(f"🔍 Question {i}/46 : {question[:50]}{'...' if len(question) > 50 else ''}")
        
        result = test_single_question(question, i)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Succès ({result['duration']:.2f}s)")
        else:
            print(f"   ❌ Échec : {result['error']}")
        
        # Pause entre les questions pour éviter la surcharge
        if i % 10 == 0:
            print(f"   ⏸️ Pause après {i} questions...")
            time.sleep(1)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    return results, total_duration

def analyze_results(results: List[Dict[str, Any]], total_duration: float):
    """Analyse des résultats"""
    print("\n📊 ANALYSE DES RÉSULTATS")
    print("=" * 60)
    
    # Statistiques générales
    total_questions = len(results)
    successful_questions = sum(1 for r in results if r["success"])
    failed_questions = total_questions - successful_questions
    
    # Statistiques de performance
    successful_durations = [r["duration"] for r in results if r["success"]]
    avg_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0
    max_duration = max(successful_durations) if successful_durations else 0
    min_duration = min(successful_durations) if successful_durations else 0
    
    within_limit_count = sum(1 for r in results if r.get("within_limit", False))
    
    # Affichage des statistiques
    print(f"📋 Statistiques générales :")
    print(f"   - Questions totales : {total_questions}")
    print(f"   - Questions réussies : {successful_questions}")
    print(f"   - Questions échouées : {failed_questions}")
    print(f"   - Taux de succès : {(successful_questions/total_questions)*100:.1f}%")
    print()
    
    print(f"⏱️ Statistiques de performance :")
    print(f"   - Temps total : {total_duration:.2f}s")
    print(f"   - Temps moyen : {avg_duration:.2f}s")
    print(f"   - Temps min : {min_duration:.2f}s")
    print(f"   - Temps max : {max_duration:.2f}s")
    print(f"   - Dans la limite (<5s) : {within_limit_count}/{successful_questions}")
    print()
    
    # Questions échouées
    if failed_questions > 0:
        print(f"❌ Questions échouées :")
        for result in results:
            if not result["success"]:
                print(f"   - Question {result['question_number']} : {result['error']}")
        print()
    
    # Questions lentes
    slow_questions = [r for r in results if r["success"] and r["duration"] >= 5.0]
    if slow_questions:
        print(f"🐌 Questions lentes (>5s) :")
        for result in slow_questions:
            print(f"   - Question {result['question_number']} : {result['duration']:.2f}s")
        print()
    
    return {
        "total_questions": total_questions,
        "successful_questions": successful_questions,
        "failed_questions": failed_questions,
        "success_rate": (successful_questions/total_questions)*100,
        "avg_duration": avg_duration,
        "within_limit_count": within_limit_count,
        "total_duration": total_duration
    }

def save_results(results: List[Dict[str, Any]], analysis: Dict[str, Any]):
    """Sauvegarde des résultats"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sauvegarder les résultats détaillés
    results_file = f"tests_uat/results_46_questions_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Résultats sauvegardés : {results_file}")

def main():
    """Test principal"""
    # Test de toutes les questions
    results, total_duration = test_all_questions()
    
    # Analyse des résultats
    analysis = analyze_results(results, total_duration)
    
    # Sauvegarde
    save_results(results, analysis)
    
    # Résumé final
    print("📋 RÉSUMÉ FINAL")
    print("=" * 60)
    print(f"Questions réussies : {analysis['successful_questions']}/{analysis['total_questions']}")
    print(f"Taux de succès : {analysis['success_rate']:.1f}%")
    print(f"Temps moyen : {analysis['avg_duration']:.2f}s")
    print(f"Performance : {analysis['within_limit_count']}/{analysis['successful_questions']} dans la limite")
    print(f"Temps total : {analysis['total_duration']:.2f}s")
    
    # Statut global
    success_threshold = 0.8  # 80% de succès minimum
    performance_threshold = 0.8  # 80% dans la limite de temps
    
    success_ok = analysis['success_rate'] >= success_threshold
    performance_ok = (analysis['within_limit_count'] / analysis['successful_questions']) >= performance_threshold if analysis['successful_questions'] > 0 else False
    
    global_success = success_ok and performance_ok
    
    print(f"\n🎯 STATUT GLOBAL : {'✅ SUCCÈS' if global_success else '❌ ÉCHEC'}")
    print(f"   - Succès ({success_threshold*100}%) : {'✅' if success_ok else '❌'}")
    print(f"   - Performance ({performance_threshold*100}%) : {'✅' if performance_ok else '❌'}")
    
    return global_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
