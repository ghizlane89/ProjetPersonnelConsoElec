#!/usr/bin/env python3
"""
Script pour générer un rapport markdown avec les questions et réponses du test UAT
"""

import json
import sys
from datetime import datetime

def generate_markdown_report(json_file_path, output_file_path):
    """Génère un rapport markdown avec les questions et réponses"""
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"❌ Erreur de décodage JSON : {json_file_path}")
        return
    
    # Préparer le contenu markdown
    markdown_content = []
    
    # En-tête
    markdown_content.append("# 📋 RAPPORT UAT - 46 QUESTIONS ET RÉPONSES")
    markdown_content.append("")
    markdown_content.append(f"**Date de génération :** {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    markdown_content.append(f"**Fichier source :** {json_file_path}")
    markdown_content.append("")
    
    # Statistiques générales
    analysis = data.get('analysis', {})
    markdown_content.append("## 📊 STATISTIQUES GÉNÉRALES")
    markdown_content.append("")
    markdown_content.append(f"- **Questions totales :** {analysis.get('total_questions', 0)}")
    markdown_content.append(f"- **Questions réussies :** {analysis.get('successful_questions', 0)}")
    markdown_content.append(f"- **Questions échouées :** {analysis.get('failed_questions', 0)}")
    markdown_content.append(f"- **Taux de succès :** {analysis.get('success_rate', 0):.1f}%")
    markdown_content.append(f"- **Temps moyen :** {analysis.get('avg_duration', 0):.2f}s")
    markdown_content.append(f"- **Dans la limite (<5s) :** {analysis.get('within_limit_count', 0)}/{analysis.get('total_questions', 0)}")
    markdown_content.append("")
    
    # Questions et réponses
    markdown_content.append("## 🔍 QUESTIONS ET RÉPONSES")
    markdown_content.append("")
    
    results = data.get('results', [])
    
    for i, result in enumerate(results, 1):
        question = result.get('question', '')
        success = result.get('success', False)
        duration = result.get('duration', 0)
        within_limit = result.get('within_limit', False)
        
        # Statut
        status_icon = "✅" if success else "❌"
        limit_icon = "⚡" if within_limit else "🐌"
        
        markdown_content.append(f"### {status_icon} Question {i:2d} : {question}")
        markdown_content.append("")
        markdown_content.append(f"**⏱️ Temps :** {duration:.2f}s {limit_icon}")
        markdown_content.append(f"**✅ Statut :** {'SUCCÈS' if success else 'ÉCHEC'}")
        markdown_content.append("")
        
        if success:
            # Afficher le plan généré
            plan = result.get('plan', {})
            markdown_content.append("#### 📋 Plan généré")
            markdown_content.append("")
            markdown_content.append(f"- **Type :** {plan.get('metadata', {}).get('question_type', 'N/A')}")
            markdown_content.append(f"- **Complexité :** {plan.get('metadata', {}).get('complexity', 'N/A')}")
            markdown_content.append("")
            
            steps = plan.get('steps', [])
            for step in steps:
                markdown_content.append(f"- **Étape {step.get('step_id', 'N/A')} :** {step.get('description', 'N/A')}")
                params = step.get('parameters', {})
                if params:
                    markdown_content.append(f"  - Paramètres : `{params}`")
            markdown_content.append("")
            
            # Afficher les résultats
            result_data = result.get('result', {})
            results_list = result_data.get('results', [])
            
            markdown_content.append("#### 📊 Résultats")
            markdown_content.append("")
            
            for step_result in results_list:
                tool_result = step_result.get('result', {})
                tool_name = tool_result.get('tool', '')
                
                markdown_content.append(f"**🔧 Outil :** {tool_name}")
                markdown_content.append("")
                
                if tool_name == 'aggregate':
                    # Afficher les paramètres originaux et corrigés
                    original_params = tool_result.get('original_parameters', {})
                    corrected_params = tool_result.get('parameters', {})
                    
                    markdown_content.append(f"- **Plan original :** `{original_params}`")
                    markdown_content.append(f"- **Plan corrigé :** `{corrected_params}`")
                    markdown_content.append("")
                    
                    # Afficher les données d'agrégation
                    agg_result = tool_result.get('result', {})
                    agg_data = agg_result.get('data', [])
                    
                    if agg_data:
                        for data_point in agg_data:
                            value = data_point.get('value', 0)
                            count = data_point.get('count', 0)
                            start_date = data_point.get('start_date', '')
                            end_date = data_point.get('end_date', '')
                            
                            markdown_content.append(f"- **Résultat :** {value:.2f} kWh")
                            markdown_content.append(f"- **Période :** {start_date} → {end_date}")
                            markdown_content.append(f"- **Enregistrements :** {count}")
                            
                            # Afficher les corrections métier
                            business_correction = corrected_params.get('business_correction', '')
                            post_processing = corrected_params.get('post_processing', '')
                            
                            if business_correction:
                                markdown_content.append(f"- **🔧 Correction métier :** {business_correction}")
                            if post_processing:
                                markdown_content.append(f"- **⚙️ Post-traitement :** {post_processing}")
                            
                            markdown_content.append("")
                
                elif tool_name == 'forecast':
                    # Afficher les erreurs de prévision
                    forecast_result = tool_result.get('result', {})
                    if forecast_result.get('status') == 'error':
                        error_msg = forecast_result.get('message', '')
                        markdown_content.append(f"- **⚠️ Erreur prévision :** {error_msg}")
                        markdown_content.append("")
                    else:
                        markdown_content.append("- **✅ Prévision générée**")
                        markdown_content.append("")
                
                elif tool_name == 'plot':
                    # Indiquer qu'un graphique a été généré
                    markdown_content.append("- **📈 Graphique généré**")
                    markdown_content.append("")
        
        else:
            # Afficher l'erreur
            error = result.get('error', 'Erreur inconnue')
            markdown_content.append(f"**❌ Erreur :** {error}")
            markdown_content.append("")
        
        markdown_content.append("---")
        markdown_content.append("")
    
    # Résumé final
    markdown_content.append("## 🎯 RÉSUMÉ FINAL")
    markdown_content.append("")
    
    success_rate = analysis.get('success_rate', 0)
    within_limit_rate = (analysis.get('within_limit_count', 0) / analysis.get('total_questions', 1)) * 100
    
    markdown_content.append(f"- **✅ Succès :** {success_rate:.1f}%")
    markdown_content.append(f"- **⚡ Performance :** {within_limit_rate:.1f}%")
    markdown_content.append(f"- **🎯 STATUT GLOBAL :** {'SUCCÈS' if success_rate >= 80 and within_limit_rate >= 80 else 'ÉCHEC'}")
    markdown_content.append("")
    
    # Écrire le fichier markdown
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))
        print(f"✅ Rapport markdown généré : {output_file_path}")
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture du fichier : {e}")

if __name__ == "__main__":
    import glob
    import os
    
    result_files = glob.glob("tests_uat/results_46_questions_*.json")
    
    if not result_files:
        print("❌ Aucun fichier de résultats trouvé dans tests_uat/")
        sys.exit(1)
    
    # Prendre le plus récent
    latest_file = max(result_files, key=os.path.getctime)
    print(f"📁 Utilisation du fichier : {latest_file}")
    
    # Générer le nom du fichier de sortie
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"tests_uat/rapport_uat_46_questions_{timestamp}.md"
    
    generate_markdown_report(latest_file, output_file)




