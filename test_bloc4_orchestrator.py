#!/usr/bin/env python3
"""
Test Rapide du Bloc 4 - Orchestrateur LangGraph
===============================================

Test simple pour vérifier que l'orchestrateur fonctionne.
"""

import sys
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bloc4():
    """Test du Bloc 4"""
    print("🧪 TEST BLOC 4 - ORCHESTRATEUR LANGGRAPH")
    print("=" * 50)
    
    try:
        # Import de l'orchestrateur
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        
        print("🔧 Initialisation de l'orchestrateur...")
        orchestrator = LangGraphOrchestrator()
        
        # Vérifier le statut
        status = orchestrator.get_status()
        print(f"📊 Statut: {status}")
        
        # Test avec une question simple
        test_question = "Quelle est ma consommation d'électricité hier ?"
        print(f"\n🔍 Test avec la question: {test_question}")
        
        response = orchestrator.process_question(test_question)
        
        print(f"\n📋 RÉPONSE:")
        print(f"   Question: {response.get('question')}")
        print(f"   Réponse: {response.get('answer')}")
        print(f"   Statut: {response.get('status')}")
        print(f"   Temps: {response.get('total_execution_time', 0):.2f}s")
        
        if response.get('corrections_applied'):
            print(f"   Corrections: {response.get('corrections_applied')}")
        
        print("\n✅ TEST RÉUSSI - Bloc 4 fonctionne !")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = test_bloc4()
    sys.exit(0 if success else 1)




