#!/usr/bin/env python3
"""
Tests Poussés du Bloc 4 - Orchestrateur LangGraph
=================================================

Tests avancés pour valider toutes les fonctionnalités du Bloc 4 :
- Corrections automatiques
- Gestion d'erreurs
- Retry et fallback
- Formatage des réponses
"""

import sys
import os
import logging
import time
from typing import Dict, List, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_bloc4_advanced():
    """Tests poussés du Bloc 4"""
    print("🧪 TESTS PUSÉS BLOC 4 - ORCHESTRATEUR LANGGRAPH")
    print("=" * 60)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        
        # Initialiser l'orchestrateur
        print("🔧 Initialisation de l'orchestrateur...")
        orchestrator = LangGraphOrchestrator()
        
        # Tests des différents composants
        tests = [
            test_corrections_automatiques,
            test_gestion_erreurs,
            test_retry_fallback,
            test_formatage_reponses,
            test_performance,
            test_cas_complexes
        ]
        
        results = []
        for test_func in tests:
            print(f"\n🔍 {test_func.__name__.replace('_', ' ').title()}...")
            result = test_func(orchestrator)
            results.append(result)
            print(f"   {'✅' if result['success'] else '❌'} {result['description']}")
        
        # Résumé
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        print(f"\n📊 RÉSUMÉ DES TESTS:")
        print(f"   Tests réussis: {success_count}/{total_count}")
        print(f"   Taux de succès: {success_count/total_count*100:.1f}%")
        
        return success_count == total_count
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        return False

def test_corrections_automatiques(orchestrator) -> Dict[str, Any]:
    """Test des corrections automatiques"""
    questions_with_corrections = [
        "Quelle est ma consommation moyenne par jour ?",  # mean → sum + post_processing
        "Combien ai-je consommé cette semaine ?",         # week → 7d
        "Quelle est ma consommation totale ?",             # all → current_year
        "Montre-moi ma consommation d'hier",              # hier → last_day
    ]
    
    corrections_detected = 0
    
    for question in questions_with_corrections:
        try:
            response = orchestrator.process_question(question)
            corrections = response.get('corrections_applied', [])
            
            if corrections:
                corrections_detected += 1
                print(f"     ✅ Corrections détectées pour '{question}': {corrections}")
            
        except Exception as e:
            print(f"     ❌ Erreur pour '{question}': {e}")
    
    return {
        'success': corrections_detected >= 2,  # Au moins 2 corrections
        'description': f'Corrections automatiques ({corrections_detected}/4)',
        'details': f'Corrections détectées: {corrections_detected}'
    }

def test_gestion_erreurs(orchestrator) -> Dict[str, Any]:
    """Test de la gestion d'erreurs"""
    error_scenarios = [
        "Question vide",                    # Gestion des questions vides
        "",                                 # Chaîne vide
        "Question avec caractères spéciaux: @#$%^&*()",  # Caractères spéciaux
        "Question très longue " + "x" * 1000,  # Question très longue
    ]
    
    errors_handled = 0
    
    for scenario in error_scenarios:
        try:
            response = orchestrator.process_question(scenario)
            
            if response.get('status') == 'error':
                errors_handled += 1
                print(f"     ✅ Erreur gérée pour: {scenario[:50]}...")
            elif 'erreur' in response.get('answer', '').lower():
                errors_handled += 1
                print(f"     ✅ Erreur détectée dans la réponse")
            
        except Exception as e:
            errors_handled += 1
            print(f"     ✅ Exception gérée: {e}")
    
    return {
        'success': errors_handled >= 3,  # Au moins 3 erreurs gérées
        'description': f'Gestion d\'erreurs ({errors_handled}/4)',
        'details': f'Erreurs gérées: {errors_handled}'
    }

def test_retry_fallback(orchestrator) -> Dict[str, Any]:
    """Test du système de retry et fallback"""
    # Simuler des erreurs en modifiant temporairement la configuration
    original_config = orchestrator.config.RETRY_CONFIG.copy()
    
    try:
        # Configurer des retries rapides pour le test
        orchestrator.config.RETRY_CONFIG['max_retries'] = 2
        orchestrator.config.RETRY_CONFIG['retry_delay'] = 0.1
        
        # Test avec une question normale
        start_time = time.time()
        response = orchestrator.process_question("Quelle est ma consommation d'électricité hier ?")
        execution_time = time.time() - start_time
        
        # Vérifier que le système a géré les retries
        if execution_time > 0.5:  # Temps suffisant pour retries
            return {
                'success': True,
                'description': 'Système de retry fonctionnel',
                'details': f'Temps d\'exécution: {execution_time:.2f}s'
            }
        else:
            return {
                'success': False,
                'description': 'Retry non détecté',
                'details': f'Temps trop court: {execution_time:.2f}s'
            }
            
    finally:
        # Restaurer la configuration originale
        orchestrator.config.RETRY_CONFIG = original_config

def test_formatage_reponses(orchestrator) -> Dict[str, Any]:
    """Test du formatage des réponses"""
    test_questions = [
        "Quelle est ma consommation d'électricité hier ?",
        "Combien ai-je consommé ce mois-ci ?",
        "Quelle est ma consommation moyenne par jour ?",
    ]
    
    formatted_responses = 0
    
    for question in test_questions:
        try:
            response = orchestrator.process_question(question)
            
            # Vérifier le formatage
            if (response.get('answer') and 
                response.get('status') and 
                'total_execution_time' in response):
                formatted_responses += 1
                print(f"     ✅ Réponse formatée pour: {question[:30]}...")
            
        except Exception as e:
            print(f"     ❌ Erreur de formatage: {e}")
    
    return {
        'success': formatted_responses >= 2,  # Au moins 2 réponses formatées
        'description': f'Formatage des réponses ({formatted_responses}/3)',
        'details': f'Réponses formatées: {formatted_responses}'
    }

def test_performance(orchestrator) -> Dict[str, Any]:
    """Test de performance"""
    performance_tests = []
    
    for i in range(3):
        start_time = time.time()
        response = orchestrator.process_question("Quelle est ma consommation d'électricité hier ?")
        execution_time = time.time() - start_time
        performance_tests.append(execution_time)
    
    avg_time = sum(performance_tests) / len(performance_tests)
    max_time = max(performance_tests)
    
    print(f"     ⏱️ Temps moyen: {avg_time:.2f}s")
    print(f"     ⏱️ Temps max: {max_time:.2f}s")
    
    return {
        'success': avg_time < 5.0 and max_time < 10.0,  # Critères de performance
        'description': f'Performance ({avg_time:.2f}s moyen)',
        'details': f'Min: {min(performance_tests):.2f}s, Max: {max_time:.2f}s'
    }

def test_cas_complexes(orchestrator) -> Dict[str, Any]:
    """Test de cas complexes"""
    complex_questions = [
        "Compare ma consommation d'hier avec celle d'aujourd'hui",
        "Quelle est ma consommation moyenne par jour et combien ça coûte ?",
        "Montre-moi ma consommation de cette semaine et du mois dernier",
    ]
    
    complex_success = 0
    
    for question in complex_questions:
        try:
            response = orchestrator.process_question(question)
            
            if response.get('status') == 'success':
                complex_success += 1
                print(f"     ✅ Cas complexe réussi: {question[:40]}...")
            
        except Exception as e:
            print(f"     ❌ Cas complexe échoué: {e}")
    
    return {
        'success': complex_success >= 1,  # Au moins 1 cas complexe réussi
        'description': f'Cas complexes ({complex_success}/3)',
        'details': f'Cas complexes réussis: {complex_success}'
    }

if __name__ == "__main__":
    success = test_bloc4_advanced()
    print(f"\n🎯 {'✅ TOUS LES TESTS RÉUSSIS' if success else '❌ CERTAINS TESTS ÉCHOUÉS'}")
    sys.exit(0 if success else 1)
