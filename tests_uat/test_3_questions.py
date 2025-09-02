#!/usr/bin/env python3
"""
Test UAT Rapide - 3 Questions Représentatives
Validation de la connectivité Bloc 2 + Bloc 3
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# Ajouter les chemins pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(os.path.join(parent_dir, 'llm_planner'))
sys.path.append(os.path.join(parent_dir, 'mcp_server'))

def test_bloc2_connectivity():
    """Test de connectivité du Bloc 2 (LLM Planner)"""
    try:
        from llm_planner.core.gemini_client import GeminiClient
        
        client = GeminiClient()
        
        # Test simple
        test_question = "Quelle est ma consommation d'électricité hier ?"
        response = client.generate_plan(test_question)
        
        return {
            "success": True,
            "response": response,
            "message": "Bloc 2 (LLM Planner) connecté et fonctionnel"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erreur de connexion Bloc 2"
        }

def test_bloc3_connectivity():
    """Test de connectivité du Bloc 3 (MCP Server)"""
    try:
        from mcp_server.core.mcp_server import MCPServer
        
        server = MCPServer()
        
        # Test simple
        test_plan = {
            "action": "get_consumption",
            "period": "yesterday",
            "parameters": {}
        }
        
        response = server.execute_plan(test_plan)
        
        return {
            "success": True,
            "response": response,
            "message": "Bloc 3 (MCP Server) connecté et fonctionnel"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erreur de connexion Bloc 3"
        }

def test_integration():
    """Test d'intégration Bloc 2 + Bloc 3"""
    try:
        from llm_planner.core.gemini_client import GeminiClient
        from mcp_server.core.mcp_server import MCPServer
        
        client = GeminiClient()
        server = MCPServer()
        
        # Question test
        question = "Quelle est ma consommation d'électricité hier ?"
        
        # Générer le plan
        plan = client.generate_plan(question)
        
        # Exécuter le plan
        result = server.execute_plan(plan)
        
        return {
            "success": True,
            "question": question,
            "plan": plan,
            "result": result,
            "message": "Intégration Bloc 2 + Bloc 3 réussie"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erreur d'intégration"
        }

def test_performance():
    """Test de performance (temps de réponse < 5s)"""
    questions = [
        "Quelle est ma consommation d'électricité hier ?",
        "Combien ai-je consommé ce mois-ci ?",
        "Quelle est ma consommation moyenne par jour ?"
    ]
    
    results = []
    
    for i, question in enumerate(questions, 1):
        start_time = time.time()
        
        try:
            from llm_planner.core.gemini_client import GeminiClient
            from mcp_server.core.mcp_server import MCPServer
            
            client = GeminiClient()
            server = MCPServer()
            
            print(f"\n🔍 QUESTION {i}: {question}")
            print("-" * 50)
            
            # Générer le plan
            plan = client.generate_plan(question)
            print(f"📋 PLAN GÉNÉRÉ:")
            print(f"   {plan}")
            
            # Exécuter le plan
            result = server.execute_plan(plan)
            print(f"📊 RÉSULTAT:")
            print(f"   {result}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            results.append({
                "question": i,
                "text": question,
                "success": True,
                "duration": duration,
                "within_limit": duration < 5.0,
                "plan": plan,
                "result": result
            })
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n❌ ERREUR QUESTION {i}: {str(e)}")
            
            results.append({
                "question": i,
                "text": question,
                "success": False,
                "error": str(e),
                "duration": duration
            })
    
    return results

def main():
    """Test principal"""
    print("🧪 TEST UAT RAPIDE - 3 QUESTIONS")
    print("=" * 50)
    print(f"⏰ Début du test : {datetime.now()}")
    print()
    
    # Test 1: Bloc 2
    print("🔍 Test Bloc 2 (LLM Planner)...")
    bloc2_result = test_bloc2_connectivity()
    if bloc2_result["success"]:
        print("✅ Bloc 2 connecté")
    else:
        print(f"❌ Bloc 2 erreur : {bloc2_result['error']}")
    print()
    
    # Test 2: Bloc 3
    print("🔍 Test Bloc 3 (MCP Server)...")
    bloc3_result = test_bloc3_connectivity()
    if bloc3_result["success"]:
        print("✅ Bloc 3 connecté")
    else:
        print(f"❌ Bloc 3 erreur : {bloc3_result['error']}")
    print()
    
    # Test 3: Intégration
    print("🔍 Test Intégration Bloc 2 + Bloc 3...")
    integration_result = test_integration()
    if integration_result["success"]:
        print("✅ Intégration réussie")
    else:
        print(f"❌ Intégration erreur : {integration_result['error']}")
    print()
    
    # Test 4: Performance
    print("🔍 Test Performance (3 questions)...")
    performance_results = test_performance()
    
    success_count = sum(1 for r in performance_results if r["success"])
    avg_duration = sum(r["duration"] for r in performance_results) / len(performance_results)
    within_limit_count = sum(1 for r in performance_results if r.get("within_limit", False))
    
    print(f"📊 Résultats performance :")
    print(f"   - Questions réussies : {success_count}/3")
    print(f"   - Temps moyen : {avg_duration:.2f}s")
    print(f"   - Dans la limite (<5s) : {within_limit_count}/3")
    print()
    
    # Résumé final
    print("📋 RÉSUMÉ DU TEST")
    print("=" * 50)
    print(f"Bloc 2 (LLM Planner) : {'✅' if bloc2_result['success'] else '❌'}")
    print(f"Bloc 3 (MCP Server) : {'✅' if bloc3_result['success'] else '❌'}")
    print(f"Intégration : {'✅' if integration_result['success'] else '❌'}")
    print(f"Performance : {success_count}/3 questions réussies")
    print(f"Temps moyen : {avg_duration:.2f}s")
    
    # Statut global
    all_success = (
        bloc2_result["success"] and 
        bloc3_result["success"] and 
        integration_result["success"] and 
        success_count == 3
    )
    
    print(f"\n🎯 STATUT GLOBAL : {'✅ SUCCÈS' if all_success else '❌ ÉCHEC'}")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
