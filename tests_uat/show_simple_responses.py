#!/usr/bin/env python3
"""
Script simple pour afficher les réponses du test UAT
"""

import json
import sys

def show_simple_responses(json_file_path):
    """Affiche les réponses de manière simple"""
    
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
    print("📋 RÉPONSES SIMPLES DU TEST UAT - 46 QUESTIONS")
    print("=" * 80)
    
    results = data.get('results', [])
    
    for i, result in enumerate(results, 1):
        question = result.get('question', '')
        success = result.get('success', False)
        duration = result.get('duration', 0)
        
        print(f"\n🔍 Question {i:2d} : {question}")
        print(f"   ⏱️  Temps : {duration:.2f}s")
        print(f"   ✅ Statut : {'SUCCÈS' if success else 'ÉCHEC'}")
        
        if success:
            result_data = result.get('result', {})
            results_list = result_data.get('results', [])
            
            for step_result in results_list:
                tool_result = step_result.get('result', {})
                tool_name = tool_result.get('tool', '')
                
                if tool_name == 'aggregate':
                    # Afficher les paramètres et résultats
                    original_params = tool_result.get('original_parameters', {})
                    corrected_params = tool_result.get('parameters', {})
                    
                    print(f"   📝 Plan original : {original_params}")
                    print(f"   🔧 Plan corrigé : {corrected_params}")
                    
                    # Afficher les données
                    agg_result = tool_result.get('result', {})
                    agg_data = agg_result.get('data', [])
                    
                    if agg_data:
                        for data_point in agg_data:
                            value = data_point.get('value', 0)
                            count = data_point.get('count', 0)
                            start_date = data_point.get('start_date', '')
                            end_date = data_point.get('end_date', '')
                            
                            print(f"   📊 Résultat : {value:.2f} kWh")
                            print(f"   📅 Période : {start_date} → {end_date}")
                            print(f"   📈 Enregistrements : {count}")
                            
                            # Afficher les corrections métier
                            business_correction = corrected_params.get('business_correction', '')
                            post_processing = corrected_params.get('post_processing', '')
                            
                            if business_correction:
                                print(f"   🔧 Correction : {business_correction}")
                            if post_processing:
                                print(f"   ⚙️  Post-traitement : {post_processing}")
                
                elif tool_name == 'forecast':
                    forecast_result = tool_result.get('result', {})
                    if forecast_result.get('status') == 'error':
                        error_msg = forecast_result.get('message', '')
                        print(f"   ⚠️  Erreur prévision : {error_msg}")
                    else:
                        print(f"   ✅ Prévision générée")
                
                elif tool_name == 'plot':
                    print(f"   📈 Graphique généré")
        
        else:
            error = result.get('error', 'Erreur inconnue')
            print(f"   ❌ Erreur : {error}")
        
        print("-" * 60)

if __name__ == "__main__":
    import glob
    import os
    
    result_files = glob.glob("tests_uat/results_46_questions_*.json")
    
    if not result_files:
        print("❌ Aucun fichier de résultats trouvé dans tests_uat/")
        sys.exit(1)
    
    latest_file = max(result_files, key=os.path.getctime)
    print(f"📁 Utilisation du fichier : {latest_file}")
    
    show_simple_responses(latest_file)




