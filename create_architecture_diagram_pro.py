#!/usr/bin/env python3
"""
🎨 Générateur d'Architecture Energy-Agent - Version Pro
Création d'une image professionnelle pour PowerPoint (sans emojis)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
import os

def create_energy_agent_architecture_pro():
    """Création de l'architecture Energy-Agent avec un design professionnel (sans emojis)"""
    
    # Configuration de la figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Couleurs professionnelles
    colors = {
        'primary': '#1f77b4',      # Bleu principal
        'secondary': '#2ca02c',    # Vert secondaire
        'accent': '#ff7f0e',        # Orange accent
        'light': '#f0f8ff',         # Bleu clair
        'dark': '#2c3e50',          # Gris foncé
        'success': '#27ae60',       # Vert succès
        'warning': '#f39c12',       # Orange warning
        'info': '#3498db'           # Bleu info
    }
    
    # Titre principal
    ax.text(5, 11.5, 'ENERGY AGENT ARCHITECTURE', 
            fontsize=24, fontweight='bold', ha='center', 
            color=colors['dark'])
    
    # Sous-titre
    ax.text(5, 11, 'Intelligent Energy Consumption Analysis Platform', 
            fontsize=14, ha='center', color=colors['primary'], style='italic')
    
    # 1. INTERFACE UTILISATEUR (Streamlit)
    ui_box = FancyBboxPatch((0.5, 9.5), 9, 1, 
                           boxstyle="round,pad=0.1", 
                           facecolor=colors['light'], 
                           edgecolor=colors['primary'], 
                           linewidth=2)
    ax.add_patch(ui_box)
    
    ax.text(5, 10, 'INTERFACE UTILISATEUR (Streamlit)', 
            fontsize=16, fontweight='bold', ha='center', color=colors['primary'])
    
    # Onglets de l'interface
    tabs = ['Chat', 'Dashboard', 'Previsions', 'Sidebar']
    tab_width = 2
    for i, tab in enumerate(tabs):
        x_pos = 1 + i * 2
        tab_box = FancyBboxPatch((x_pos, 9.7), 1.5, 0.4, 
                                boxstyle="round,pad=0.05", 
                                facecolor=colors['info'], 
                                edgecolor=colors['primary'], 
                                linewidth=1)
        ax.add_patch(tab_box)
        ax.text(x_pos + 0.75, 9.9, tab, fontsize=10, ha='center', 
                color='white', fontweight='bold')
    
    # 2. ORCHESTRATEUR LANGGRAPH
    orchestrator_box = FancyBboxPatch((2, 8), 6, 1, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=colors['success'], 
                                     edgecolor=colors['dark'], 
                                     linewidth=2)
    ax.add_patch(orchestrator_box)
    
    ax.text(5, 8.5, 'ORCHESTRATEUR LANGGRAPH', 
            fontsize=16, fontweight='bold', ha='center', color='white')
    ax.text(5, 8.2, 'EnergyLangGraphWorkflow', 
            fontsize=12, ha='center', color='white', style='italic')
    
    # 3. AGENTS SPÉCIALISÉS
    agents_box = FancyBboxPatch((0.5, 5.5), 9, 2, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['warning'], 
                              edgecolor=colors['dark'], 
                              linewidth=2)
    ax.add_patch(agents_box)
    
    ax.text(5, 7.2, 'AGENTS SPECIALISES (8 Agents)', 
            fontsize=16, fontweight='bold', ha='center', color='white')
    
    # Agents individuels
    agents = [
        ('Agent 1\nValidator', 1, 6.5),
        ('Agent 2\nIntent Analyzer', 2.5, 6.5),
        ('Agent 3\nSemantic Validator', 4, 6.5),
        ('Agent 4\nLLM Agent', 5.5, 6.5),
        ('Agent 5\nStrategy Builder', 7, 6.5),
        ('Agent 6\nMCP Agent', 1, 6),
        ('Agent 7\nResponse Builder', 2.5, 6),
        ('Agent 8\nError Handler', 4, 6)
    ]
    
    for agent_name, x, y in agents:
        agent_box = FancyBboxPatch((x, y), 1.2, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor='white', 
                                  edgecolor=colors['dark'], 
                                  linewidth=1)
        ax.add_patch(agent_box)
        ax.text(x + 0.6, y + 0.3, agent_name, fontsize=9, ha='center', 
                color=colors['dark'], fontweight='bold')
    
    # 4. SERVEUR MCP (OUTILS)
    mcp_box = FancyBboxPatch((0.5, 3.5), 9, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=colors['accent'], 
                            edgecolor=colors['dark'], 
                            linewidth=2)
    ax.add_patch(mcp_box)
    
    ax.text(5, 4.5, 'SERVEUR MCP (OUTILS MODULAIRES)', 
            fontsize=16, fontweight='bold', ha='center', color='white')
    
    # Outils MCP
    tools = [
        ('EnergyMCPTools\nRequetes Energetiques', 1.5, 3.8),
        ('DashboardTools\nVisualisations', 3.5, 3.8),
        ('ProphetForecastTool\nPrevisions', 5.5, 3.8),
        ('DatabaseManager\nGestion BDD', 7.5, 3.8)
    ]
    
    for tool_name, x, y in tools:
        tool_box = FancyBboxPatch((x, y), 1.8, 0.8, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='white', 
                                 edgecolor=colors['dark'], 
                                 linewidth=1)
        ax.add_patch(tool_box)
        ax.text(x + 0.9, y + 0.4, tool_name, fontsize=9, ha='center', 
                color=colors['dark'], fontweight='bold')
    
    # 5. BASE DE DONNÉES
    db_box = FancyBboxPatch((2, 1.5), 6, 1, 
                           boxstyle="round,pad=0.1", 
                           facecolor=colors['dark'], 
                           edgecolor=colors['primary'], 
                           linewidth=2)
    ax.add_patch(db_box)
    
    ax.text(5, 2.2, 'BASE DE DONNEES (DuckDB)', 
            fontsize=16, fontweight='bold', ha='center', color='white')
    ax.text(5, 1.8, '8,772 lignes • 2 ans de donnees • Mesures 2h', 
            fontsize=12, ha='center', color='white')
    
    # Flèches de connexion
    arrows = [
        ((5, 9.5), (5, 9)),      # UI vers Orchestrateur
        ((5, 8), (5, 7.5)),      # Orchestrateur vers Agents
        ((5, 5.5), (5, 5)),      # Agents vers MCP
        ((5, 3.5), (5, 2.5))     # MCP vers Base de données
    ]
    
    for start, end in arrows:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=20, fc=colors['primary'],
                              ec=colors['primary'], linewidth=2)
        ax.add_patch(arrow)
    
    # Métriques de performance
    metrics_box = FancyBboxPatch((0.2, 0.2), 2.5, 1, 
                                boxstyle="round,pad=0.05", 
                                facecolor=colors['light'], 
                                edgecolor=colors['success'], 
                                linewidth=1)
    ax.add_patch(metrics_box)
    
    ax.text(1.45, 0.8, 'PERFORMANCE', fontsize=12, fontweight='bold', 
            ha='center', color=colors['success'])
    ax.text(1.45, 0.6, '• Reponse < 3s', fontsize=10, ha='center', color=colors['dark'])
    ax.text(1.45, 0.4, '• Precision 95%', fontsize=10, ha='center', color=colors['dark'])
    ax.text(1.45, 0.2, '• 8 Agents Specialises', fontsize=10, ha='center', color=colors['dark'])
    
    # Légende des couleurs
    legend_box = FancyBboxPatch((7.3, 0.2), 2.4, 1, 
                               boxstyle="round,pad=0.05", 
                               facecolor=colors['light'], 
                               edgecolor=colors['info'], 
                               linewidth=1)
    ax.add_patch(legend_box)
    
    ax.text(8.5, 0.8, 'LEGENDE', fontsize=12, fontweight='bold', 
            ha='center', color=colors['info'])
    ax.text(8.5, 0.6, 'Interface', fontsize=10, ha='center', color=colors['dark'])
    ax.text(8.5, 0.4, 'Orchestration', fontsize=10, ha='center', color=colors['dark'])
    ax.text(8.5, 0.2, 'Intelligence', fontsize=10, ha='center', color=colors['dark'])
    
    # Ajout d'éléments décoratifs
    # Points pour l'énergie
    for i in range(8):
        x = np.random.uniform(0.5, 9.5)
        y = np.random.uniform(0.5, 11)
        ax.plot(x, y, 'o', markersize=8, color=colors['primary'], alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_flow_diagram_pro():
    """Création du diagramme de flux de traitement (sans emojis)"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    colors = {
        'primary': '#1f77b4',
        'secondary': '#2ca02c',
        'accent': '#ff7f0e',
        'light': '#f0f8ff',
        'dark': '#2c3e50',
        'success': '#27ae60',
        'warning': '#f39c12',
        'info': '#3498db'
    }
    
    # Titre
    ax.text(5, 9.5, 'PIPELINE DE TRAITEMENT - FLUX COMPLET', 
            fontsize=20, fontweight='bold', ha='center', color=colors['dark'])
    
    # Étapes du flux
    steps = [
        ('Question\nUtilisateur', 1, 8, colors['info']),
        ('Validation', 2.5, 8, colors['success']),
        ('Analyse\nIntention', 4, 8, colors['warning']),
        ('Validation\nSemantique', 5.5, 8, colors['accent']),
        ('Generation\nPlan', 7, 8, colors['primary']),
        ('Construction\nStrategie', 8.5, 8, colors['secondary'])
    ]
    
    for step_name, x, y, color in steps:
        step_box = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, 
                                 edgecolor=colors['dark'], 
                                 linewidth=1)
        ax.add_patch(step_box)
        ax.text(x, y, step_name, fontsize=10, ha='center', 
                color='white', fontweight='bold')
    
    # Étapes du bas
    steps_bottom = [
        ('Execution\nOutils MCP', 2.5, 6, colors['dark']),
        ('Formatage\nReponse', 5.5, 6, colors['info']),
        ('Reponse\nFinale', 8.5, 6, colors['success'])
    ]
    
    for step_name, x, y, color in steps_bottom:
        step_box = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, 
                                 edgecolor=colors['dark'], 
                                 linewidth=1)
        ax.add_patch(step_box)
        ax.text(x, y, step_name, fontsize=10, ha='center', 
                color='white', fontweight='bold')
    
    # Flèches de connexion
    arrows = [
        ((1.4, 8), (2.1, 8)),      # Question vers Validation
        ((2.9, 8), (3.6, 8)),      # Validation vers Analyse
        ((4.4, 8), (5.1, 8)),      # Analyse vers Validation Sémantique
        ((5.9, 8), (6.6, 8)),      # Validation vers Génération
        ((7.4, 8), (8.1, 8)),      # Génération vers Construction
        ((8.5, 7.7), (2.5, 6.3)),  # Construction vers Exécution
        ((2.9, 6), (5.1, 6)),      # Exécution vers Formatage
        ((5.9, 6), (8.1, 6))       # Formatage vers Réponse
    ]
    
    for start, end in arrows:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=15, fc=colors['primary'],
                              ec=colors['primary'], linewidth=2)
        ax.add_patch(arrow)
    
    # Exemple de flux
    example_box = FancyBboxPatch((0.5, 3), 9, 2.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['light'], 
                                edgecolor=colors['primary'], 
                                linewidth=2)
    ax.add_patch(example_box)
    
    ax.text(5, 4.8, 'EXEMPLE DE FLUX : "Ma consommation hier ?"', 
            fontsize=14, fontweight='bold', ha='center', color=colors['primary'])
    
    example_steps = [
        '1. Question valide',
        '2. Type: consumption, Period: yesterday',
        '3. Code: YESTERDAY, Confiance: 95%',
        '4. Plan: Recuperer donnees hier avec EnergyMCPTools',
        '5. Strategie: query_energy_data("yesterday", "sum")',
        '6. Requete DuckDB -> Resultat: 12.5 kWh',
        '7. Formatage: "Votre consommation hier etait de 12.5 kWh"',
        '8. Reponse affichee a l\'utilisateur'
    ]
    
    for i, step in enumerate(example_steps):
        y_pos = 4.2 - i * 0.25
        ax.text(0.8, y_pos, step, fontsize=10, ha='left', color=colors['dark'])
    
    plt.tight_layout()
    return fig

def main():
    """Fonction principale pour générer les diagrammes professionnels"""
    
    print("🎨 Génération des diagrammes d'architecture Energy-Agent (Version Pro)...")
    
    # Création du répertoire de sortie
    output_dir = "architecture_diagrams_pro"
    os.makedirs(output_dir, exist_ok=True)
    
    # Diagramme d'architecture principal
    print("📊 Création du diagramme d'architecture principal (Pro)...")
    fig1 = create_energy_agent_architecture_pro()
    fig1.savefig(f"{output_dir}/energy_agent_architecture_pro.png", 
                 dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig1)
    
    # Diagramme de flux
    print("🔄 Création du diagramme de flux (Pro)...")
    fig2 = create_flow_diagram_pro()
    fig2.savefig(f"{output_dir}/energy_agent_flow_pro.png", 
                 dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig2)
    
    print(f"✅ Diagrammes générés dans le dossier '{output_dir}/'")
    print("📁 Fichiers créés :")
    print("   • energy_agent_architecture_pro.png (Architecture principale - Pro)")
    print("   • energy_agent_flow_pro.png (Flux de traitement - Pro)")
    print("🎯 Prêts pour PowerPoint !")

if __name__ == "__main__":
    main()
