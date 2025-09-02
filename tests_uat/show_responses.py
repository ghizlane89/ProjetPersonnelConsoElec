#!/usr/bin/env python3
"""
Script pour afficher les réponses détaillées du test UAT
"""

import json
import sys
from datetime import datetime

def show_detailed_responses(json_file_path):
    """Affiche les réponses détaillées du test UAT"""
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"❌ Erreur de décodage JSON : {json_file_path}")
        return
    
    print("=" * 100)
    print("📋 RÉPONSES DÉTAILLÉES DU TEST UAT - 46 QUESTIONS")
    print("=" * 100)
    
    results = data.get('results', [])
    
    for i, result in enumerate(results, 1):
        question = result.get('question', '')
        success = result.get('success', False)
        duration = result.get('duration', 0)
        
        print(f"\n{'='*80}")
        print(f"🔍 QUESTION {i:2d} : {question}")
        print(f"{'='*80}")
        print(f"⏱️  Temps : {duration:.2f}s")
        print(f"✅ Statut : {'SUCCÈS' if success else 'ÉCHEC'}")
        
        if success:
            # Afficher le plan généré
            plan = result.get('plan', {})
            print(f"\n📋 PLAN GÉNÉRÉ :")
            print(f"   Type : {plan.get('metadata', {}).get('question_type', 'N/A')}")
            print(f"   Complexité : {plan.get('metadata', {}).get('complexity', 'N/A')}")
            
            steps = plan.get('steps', [])
            for step in steps:
                print(f"   📝 Étape {step.get('step_id', 'N/A')} : {step.get('description', 'N/A')}")
                params = step.get('parameters', {})
                if params:
                    print(f"      Paramètres : {params}")
            
            # Afficher les résultats détaillés
            result_data = result.get('result', {})
            results_list = result_data.get('results', [])
            
            print(f"\n📊 RÉSULTATS DÉTAILLÉS :")
            for step_result in results_list:
                tool_result = step_result.get('result', {})
                tool_name = tool_result.get('tool', '')
                
                print(f"\n   🔧 Outil : {tool_name}")
                
                if tool_name == 'aggregate':
                    # Afficher les paramètres originaux et corrigés
                    original_params = tool_result.get('original_parameters', {})
                    corrected_params = tool_result.get('parameters', {})
                    
                    print(f"      📝 Paramètres originaux : {original_params}")
                    print(f"      🔧 Paramètres corrigés : {corrected_params}")
                    
                    # Afficher les données d'agrégation
                    agg_result = tool_result.get('result', {})
                    agg_data = agg_result.get('data', [])
                    
                    if agg_data:
                        for data_point in agg_data:
                            value = data_point.get('value', 0)
                            count = data_point.get('count', 0)
                            start_date = data_point.get('start_date', '')
                            end_date = data_point.get('end_date', '')
                            
                            print(f"      📊 Valeur : {value:.2f} kWh")
                            print(f"      📅 Période : {start_date} → {end_date}")
                            print(f"      📈 Enregistrements : {count}")
                            
                            # Afficher les corrections métier
                            business_correction = corrected_params.get('business_correction', '')
                            post_processing = corrected_params.get('post_processing', '')
                            original_aggregation = corrected_params.get('original_aggregation', '')
                            
                            if business_correction:
                                print(f"      🔧 Correction métier : {business_correction}")
                            if post_processing:
                                print(f"      ⚙️  Post-traitement : {post_processing}")
                            if original_aggregation:
                                print(f"      🔄 Agrégation originale : {original_aggregation}")
                            
                            # Afficher le traitement métier
                            business_processing = agg_result.get('business_processing', '')
                            if business_processing:
                                print(f"      💼 Traitement métier : {business_processing}")
                
                elif tool_name == 'forecast':
                    # Afficher les erreurs de prévision
                    forecast_result = tool_result.get('result', {})
                    if forecast_result.get('status') == 'error':
                        error_msg = forecast_result.get('message', '')
                        print(f"      ⚠️  Erreur : {error_msg}")
                    else:
                        print(f"      ✅ Prévision générée")
                
                elif tool_name == 'plot':
                    # Indiquer qu'un graphique a été généré
                    plot_result = tool_result.get('result', {})
                    chart_json = plot_result.get('chart_json', '')
                    if chart_json:
                        print(f"      📈 Graphique généré (JSON disponible)")
                    else:
                        print(f"      📈 Graphique généré")
        
        else:
            # Afficher l'erreur
            error = result.get('error', 'Erreur inconnue')
            print(f"\n❌ ERREUR : {error}")
        
        print(f"\n{'='*80}")

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
    
    show_detailed_responses(latest_file)




