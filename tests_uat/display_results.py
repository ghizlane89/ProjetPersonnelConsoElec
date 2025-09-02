#!/usr/bin/env python3
"""
Script pour afficher les résultats du test UAT des 46 questions
"""

import json
import sys
from datetime import datetime

def display_uat_results(json_file_path):
    """Affiche les résultats UAT de manière lisible"""
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"❌ Erreur de décodage JSON : {json_file_path}")
        return
    
    print("=" * 80)
    print("📋 RÉSULTATS DU TEST UAT - 46 QUESTIONS")
    print("=" * 80)
    
    # Statistiques générales
    analysis = data.get('analysis', {})
    print(f"\n📊 STATISTIQUES GÉNÉRALES :")
    print(f"   - Questions totales : {analysis.get('total_questions', 0)}")
    print(f"   - Questions réussies : {analysis.get('successful_questions', 0)}")
    print(f"   - Questions échouées : {analysis.get('failed_questions', 0)}")
    print(f"   - Taux de succès : {analysis.get('success_rate', 0):.1f}%")
    print(f"   - Temps moyen : {analysis.get('avg_duration', 0):.2f}s")
    print(f"   - Dans la limite (<5s) : {analysis.get('within_limit_count', 0)}/{analysis.get('total_questions', 0)}")
    
    print("\n" + "=" * 80)
    print("🔍 QUESTIONS ET RÉPONSES")
    print("=" * 80)
    
    results = data.get('results', [])
    
    for i, result in enumerate(results, 1):
        question = result.get('question', '')
        success = result.get('success', False)
        duration = result.get('duration', 0)
        within_limit = result.get('within_limit', False)
        
        # Statut
        status_icon = "✅" if success else "❌"
        limit_icon = "⚡" if within_limit else "🐌"
        
        print(f"\n{status_icon} Question {i:2d} : {question}")
        print(f"   ⏱️  Temps : {duration:.2f}s {limit_icon}")
        
        if success:
            # Extraire les informations importantes du résultat
            result_data = result.get('result', {})
            results_list = result_data.get('results', [])
            
            for step_result in results_list:
                tool_result = step_result.get('result', {})
                tool_name = tool_result.get('tool', '')
                
                if tool_name == 'aggregate':
                    # Afficher les données d'agrégation
                    agg_result = tool_result.get('result', {})
                    agg_data = agg_result.get('data', [])
                    
                    if agg_data:
                        for data_point in agg_data:
                            value = data_point.get('value', 0)
                            count = data_point.get('count', 0)
                            start_date = data_point.get('start_date', '')
                            end_date = data_point.get('end_date', '')
                            
                            # Vérifier s'il y a eu une correction métier
                            business_correction = tool_result.get('parameters', {}).get('business_correction', '')
                            post_processing = tool_result.get('parameters', {}).get('post_processing', '')
                            
                            print(f"   📊 Résultat : {value:.2f} kWh")
                            print(f"   📅 Période : {start_date} → {end_date}")
                            print(f"   📈 Enregistrements : {count}")
                            
                            if business_correction:
                                print(f"   🔧 Correction métier : {business_correction}")
                            if post_processing:
                                print(f"   ⚙️  Post-traitement : {post_processing}")
                
                elif tool_name == 'forecast':
                    # Afficher les erreurs de prévision
                    forecast_result = tool_result.get('result', {})
                    if forecast_result.get('status') == 'error':
                        error_msg = forecast_result.get('message', '')
                        print(f"   ⚠️  Erreur prévision : {error_msg}")
                
                elif tool_name == 'plot':
                    # Indiquer qu'un graphique a été généré
                    print(f"   📈 Graphique généré")
        
        else:
            # Afficher l'erreur
            error = result.get('error', 'Erreur inconnue')
            print(f"   ❌ Erreur : {error}")
    
    print("\n" + "=" * 80)
    print("🎯 RÉSUMÉ FINAL")
    print("=" * 80)
    
    success_rate = analysis.get('success_rate', 0)
    within_limit_rate = (analysis.get('within_limit_count', 0) / analysis.get('total_questions', 1)) * 100
    
    print(f"✅ Succès : {success_rate:.1f}%")
    print(f"⚡ Performance : {within_limit_rate:.1f}%")
    print(f"🎯 STATUT GLOBAL : {'SUCCÈS' if success_rate >= 80 and within_limit_rate >= 80 else 'ÉCHEC'}")

if __name__ == "__main__":
    # Chercher le fichier de résultats le plus récent
    import glob
    import os
    
    result_files = glob.glob("tests_uat/results_46_questions_*.json")
    
    if not result_files:
        print("❌ Aucun fichier de résultats trouvé dans tests_uat/")
        sys.exit(1)
    
    # Prendre le plus récent
    latest_file = max(result_files, key=os.path.getctime)
    print(f"📁 Utilisation du fichier : {latest_file}")
    
    display_uat_results(latest_file)




