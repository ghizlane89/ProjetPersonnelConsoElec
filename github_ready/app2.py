#!/usr/bin/env python3
"""
⚡ Energy Agent - Application Streamlit (Interface Complète + Architecture LangGraph)
Interface utilisateur complète pour l'analyse de consommation électrique
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
try:
    import duckdb
except ImportError:
    st.error("❌ Erreur : Module 'duckdb' non trouvé. Veuillez activer l'environnement conda 'energy-agent' avec : conda activate energy-agent")
    st.stop()
from datetime import datetime, timedelta
import sys
import os

# Ajouter les chemins pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports des modules existants (architecture LangGraph)
from orchestration.energy_langgraph_workflow import get_energy_workflow
from mcp_server.core.dashboard_tools import DashboardTools
from core.dashboard.forecast_page import show_forecast_page

# Configuration de la page
st.set_page_config(
    page_title="⚡ Energy Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Électrique Pimpé (repris complet de app_old.py)
st.markdown("""
<style>
    /* Thème électrique principal */
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #10b981 50%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        box-shadow: 0 8px 32px rgba(37, 99, 235, 0.3);
        margin-bottom: 2rem;
    }
    
    .electric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #2563eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .electric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4);
    }
    
    .electric-metric {
        background: linear-gradient(45deg, #2563eb, #10b981);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .electric-pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .analysis-section {
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-weight: bold;
        color: #2563eb;
        margin-bottom: 0.5rem;
        font-size: 1.1em;
    }
    
    .section-content {
        color: #666;
        line-height: 1.6;
    }
    
    .chat-message {
        background: linear-gradient(90deg, #2563eb 0%, #10b981 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background: linear-gradient(90deg, #10b981 0%, #2563eb 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: right;
    }
    
    .suggestion-button {
        background: linear-gradient(45deg, #2563eb, #10b981);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9em;
    }
    
    .suggestion-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    .sidebar-section {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #1E90FF;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(30, 144, 255, 0.2);
    }
    
    .sidebar-title {
        color: #1E90FF;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 0.5rem;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .status-ok {
        background: #39FF14;
        color: #333333;
    }
    
    .status-error {
        background: #FF4444;
        color: white;
    }
    
    .info-text {
        color: #333333;
        font-size: 0.9em;
        line-height: 1.4;
    }
    
    .smart-question {
        background: linear-gradient(45deg, #2563eb, #10b981);
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        cursor: pointer;
        font-size: 0.9em;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .smart-question:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    .control-btn {
        background: #f8f9fa;
        border: 1px solid #2563eb;
        color: #2563eb;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        margin: 0.2rem;
        cursor: pointer;
        font-size: 0.8em;
        transition: all 0.3s ease;
    }
    
    .control-btn:hover {
        background: #2563eb;
        color: white;
    }
    
    /* Style personnalisé pour le bouton d'entraînement */
    .stButton > button {
        background: linear-gradient(45deg, #2563eb, #10b981) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #1d4ed8, #059669) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    .alert-warning {
        background: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.25rem 0;
        font-size: 0.85em;
        border-left: 4px solid #ffc107;
    }
    
    .alert-info {
        background: #d1ecf1;
        color: #0c5460;
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.25rem 0;
        font-size: 0.85em;
        border-left: 4px solid #17a2b8;
    }
    
    .alert-success {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.25rem 0;
        font-size: 0.85em;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

class EnergyAgentApp:
    """Application principale Energy Agent avec interface complète + architecture LangGraph"""
    
    def __init__(self):
        """Initialisation de l'application"""
        # Initialisation silencieuse des composants
        placeholder = st.empty()
        with placeholder.container():
            try:
                self.workflow = get_energy_workflow()
                self.dashboard_tools = DashboardTools()
                # Statut des composants
                self.system_status = self._check_system_status()
            except Exception as e:
                st.error(f"Erreur d'initialisation: {e}")
                self.workflow = None
                self.dashboard_tools = None
                self.system_status = {
                    'workflow': {'status': 'error', 'message': f'Erreur: {str(e)}'},
                    'gemini': {'status': 'unknown', 'message': 'Non testé'},
                    'mcp': {'status': 'unknown', 'message': 'Non testé'},
                    'database': {'status': 'unknown', 'message': 'Non testé'}
                }
        
        # Questions suggérées organisées par catégorie (reprises de app_old.py)
        self.suggested_questions = {
            "Consommation": [
                "Quelle est ma consommation d'électricité hier ?",
                "Combien ai-je consommé ce mois-ci ?",
                "Quelle est ma consommation moyenne par jour ?",
                "Quelle est ma consommation par heure ?"
            ],
            "Comparaisons": [
                "Ma consommation a-t-elle augmenté ce mois ?",
                "Ma consommation est-elle plus élevée que le mois dernier ?",
                "Ma consommation de jour est-elle plus élevée que la nuit ?",
                "Ma consommation du weekend est-elle différente de la semaine ?"
            ],
            "Tendances": [
                "Quelle est ma consommation par semaine ?",
                "Quelle est ma consommation par année ?",
                "Ma consommation en été est-elle plus élevée qu'en hiver ?",
                "Quelle est ma consommation moyenne par jour ?"
            ]
        }
    
    def _check_system_status(self):
        """Vérifie l'état des composants système"""
        status = {}
        
        # Test Workflow
        if hasattr(self, 'workflow') and self.workflow is not None:
            status['workflow'] = {'status': 'success', 'message': '✅ Workflow LangGraph initialisé'}
        else:
            status['workflow'] = {'status': 'error', 'message': '❌ Workflow non initialisé'}
        
        # Test Gemini
        try:
            from llm_planner.core.gemini_client import get_gemini_client
            gemini_client = get_gemini_client()
            if gemini_client.api_key:
                status['gemini'] = {'status': 'success', 'message': '✅ API Gemini configurée'}
            else:
                status['gemini'] = {'status': 'warning', 'message': '⚠️ API Gemini non configurée'}
        except Exception as e:
            status['gemini'] = {'status': 'error', 'message': f'❌ Erreur Gemini: {str(e)}'}
        
        # Test MCP
        try:
            from mcp_server.core.energy_mcp_tools import get_energy_capabilities
            capabilities = get_energy_capabilities()
            status['mcp'] = {'status': 'success', 'message': '✅ Capacités MCP chargées'}
        except Exception as e:
            status['mcp'] = {'status': 'error', 'message': f'❌ Erreur MCP: {str(e)}'}
        
        # Test Database
        try:
            db_path = "data_genere/processed/energy_fictional_2h.duckdb"
            if os.path.exists(db_path):
                status['database'] = {'status': 'success', 'message': '✅ Base DuckDB disponible'}
            else:
                status['database'] = {'status': 'error', 'message': f'❌ Base non trouvée: {db_path}'}
        except Exception as e:
            status['database'] = {'status': 'error', 'message': f'❌ Erreur DB: {str(e)}'}
        
        return status
    
    def _show_gap_management(self):
        """Affiche la section de gestion des gaps dans la sidebar"""
        try:
            from data_genere_gap.gap_manager import GapManager
            
            # Vérifier le statut des gaps
            manager = GapManager()
            status = manager.get_gap_status()
            
            # Affichage du statut
            if status.get('gap_detected', False):
                st.sidebar.markdown(f"""
                <div style="background: #fff3cd; color: #856404; padding: 0.5rem; border-radius: 6px; margin: 0.5rem 0; font-size: 0.85em; border-left: 4px solid #ffc107;">
                    {status['summary']}
                </div>
                """, unsafe_allow_html=True)
                
                # Bouton de génération
                if st.sidebar.button("🔄 Générer données manquantes", 
                                   key="generate_gap_data",
                                   help="Génère automatiquement les données manquantes"):
                    self._handle_gap_generation(manager)
            else:
                st.sidebar.markdown(f"""
                <div style="background: #d4edda; color: #155724; padding: 0.5rem; border-radius: 6px; margin: 0.5rem 0; font-size: 0.85em; border-left: 4px solid #28a745;">
                    {status['summary']}
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.sidebar.error(f"❌ Erreur gestion gaps: {str(e)}")
    
    def _handle_gap_generation(self, manager):
        """Gère la génération des données manquantes"""
        try:
            # Éléments de progression
            progress_bar = st.sidebar.progress(0)
            status_text = st.sidebar.empty()
            
            def progress_callback(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
            
            # Génération avec callback
            with st.spinner("🔄 Génération des données en cours..."):
                result = manager.check_and_fill_gaps(progress_callback)
            
            # Nettoyer les éléments de progression
            progress_bar.empty()
            status_text.empty()
            
            # Afficher le résultat
            if result['success']:
                if result.get('gap_detected', False):
                    records = result.get('records_generated', 0)
                    duration = result.get('duration', 0)
                    st.sidebar.success(f"✅ {records} enregistrements générés en {duration:.1f}s")
                    
                    # Relancer Streamlit pour rafraîchir les données
                    st.rerun()
                else:
                    st.sidebar.info("ℹ️ Aucune donnée à générer")
            else:
                error_msg = result.get('message', 'Erreur inconnue')
                st.sidebar.error(f"❌ {error_msg}")
                
        except Exception as e:
            st.sidebar.error(f"❌ Erreur génération: {str(e)}")
    
    def show_header(self):
        """Affiche l'en-tête principal"""
        st.markdown("""
        <div class="main-header">
            <h1>⚡ Energy Agent ⚡</h1>
            <p>Votre assistant intelligent pour l'analyse de consommation électrique</p>
        </div>
        """, unsafe_allow_html=True)
    
    def show_sidebar(self):
        """Affiche la sidebar réorganisée avec l'ordre demandé"""
        
        # 1. 🔄 Gestion des Données
        st.sidebar.markdown("### 🔄 Gestion des Données")
        self._show_gap_management()
        
        st.sidebar.markdown("---")  # Séparateur
        
        # 2. 📊 Résumé Exécutif
        try:
            conn = duckdb.connect('data_genere/processed/energy_fictional_2h.duckdb')
            df_summary = conn.execute("SELECT * FROM energy_data LIMIT 100").fetchdf()
            conn.close()
            
            if not df_summary.empty:
                total_power = df_summary['global_active_power_kw'].mean()
                current_cost = total_power * 24 * 30 * 0.20
                savings_potential = current_cost * 0.15
                trend = 5.2  # Tendance simulée
            else:
                current_cost = 0
                savings_potential = 0
                trend = 0
            
        except Exception as e:
            current_cost = 0
            savings_potential = 0
            trend = 0
        
        st.sidebar.markdown("### 📊 Résumé Exécutif")
        st.sidebar.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-title">💰 Coût et Économies</div>
            <div class="info-text">
                <strong>💰 Coût mensuel :</strong> {current_cost:.2f}€<br>
                <small>(Tarif : 0,20€/kWh)</small><br>
                <strong>💡 Économie possible :</strong> {savings_potential:.2f}€<br>
                <strong>📈 Tendance :</strong> {'↗️' if trend > 0 else '↘️'} {abs(trend):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown("---")  # Séparateur
        
        # 4. 🔧 État des Systèmes
        st.sidebar.markdown("### 🔧 État des Systèmes")
        
        system_components = {
            'workflow': '🎼 Orchestrateur LangGraph',
            'gemini': '🤖 LLM Gemini',
            'mcp': '🔧 Serveur MCP',
            'database': '💾 Base DuckDB'
        }
        
        for key, name in system_components.items():
            status = self.system_status.get(key, {'status': 'unknown', 'message': 'Non testé'})
            status_color = {
                'success': '#39FF14',
                'warning': '#ffc107', 
                'error': '#FF4444',
                'unknown': '#6c757d'
            }.get(status['status'], '#6c757d')
            
            st.sidebar.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <div style="width: 10px; height: 10px; border-radius: 50%; background-color: {status_color}; margin-right: 8px;"></div>
                <strong style="font-size: 0.9em;">{name}</strong>
            </div>
            <div style="margin-left: 18px; font-size: 0.8em; color: #666;">
                {status['message']}
            </div>
            """, unsafe_allow_html=True)
    
    def chat_tab(self):
        """Onglet 1 : Chat intelligent (repris de app_old.py + améliorations)"""
        st.markdown("## 💬 Chat Intelligent")
        
        # Vérification que le workflow est disponible
        if not hasattr(self, 'workflow') or self.workflow is None:
            st.error("❌ Workflow LangGraph non initialisé. Vérifiez l'état des systèmes dans la sidebar.")
            return
        
        # Zone de saisie
        user_question = st.text_input(
            "⚡ Posez votre question sur votre consommation électrique...",
            placeholder="Ex: Quelle est ma consommation hier ? | Combien ai-je consommé le mois dernier ? | Quelle est ma consommation moyenne par jour ?"
        )
        
        # Gestion des questions de la sidebar (supprimé)
        pass
        
        # Traitement de la question
        if user_question or 'user_question' in st.session_state:
            question = user_question or st.session_state.user_question
            
            # Affichage de la question utilisateur
            st.markdown(f"""
            <div class="user-message">
                <strong>Vous :</strong> {question}
            </div>
            """, unsafe_allow_html=True)
            
            # Traitement avec le workflow LangGraph (architecture agentique)
            with st.spinner("🤖 Energy Agent réfléchit..."):
                try:
                    response = self.workflow.process_question(question)
                    
                    # Extraire la réponse principale du dictionnaire
                    if isinstance(response, dict):
                        answer = response.get('answer', 'Aucune réponse disponible')
                        
                        # Affichage de la réponse principale
                        st.markdown(f"""
                        <div class="chat-message">
                            <strong>⚡ Energy Agent :</strong> {answer}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Si la réponse n'est pas un dictionnaire, l'afficher directement
                        st.markdown(f"""
                        <div class="chat-message">
                            <strong>⚡ Energy Agent :</strong> {response}
                        </div>
                        """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")
        
        # 🆕 SUGGESTIONS DÉPLACÉES EN DESSOUS DE LA CONVERSATION
        st.markdown("---")
        st.markdown("### 💡 Suggestions de Questions Intelligentes")
        st.markdown("*Cliquez sur une question pour l'essayer !*")
        
        # Catégorie 1: Consommation par période passée
        with st.expander("🗓️ **Consommation par période passée**", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Quelle a été ma consommation hier ?", key="sugg_hier"):
                    st.session_state.user_question = "Quelle a été ma consommation hier ?"
                    st.rerun()
                if st.button("Quelle était ma consommation la semaine dernière ?", key="sugg_semaine_derniere"):
                    st.session_state.user_question = "Quelle était ma consommation la semaine dernière ?"
                    st.rerun()
            with col2:
                if st.button("Combien ai-je consommé le mois dernier ?", key="sugg_mois_dernier"):
                    st.session_state.user_question = "Combien ai-je consommé le mois dernier ?"
                    st.rerun()
                if st.button("Ma consommation ces 30 derniers jours ?", key="sugg_30_jours"):
                    st.session_state.user_question = "Ma consommation ces 30 derniers jours ?"
                    st.rerun()
                if st.button("Quelle était ma consommation l'année dernière ?", key="sugg_annee_derniere"):
                    st.session_state.user_question = "Quelle était ma consommation l'année dernière ?"
                    st.rerun()
        
        # Catégorie 2: Consommation moyenne
        with st.expander("📈 **Consommation moyenne**", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Quelle est ma consommation moyenne par jour ?", key="sugg_moyenne_jour"):
                    st.session_state.user_question = "Quelle est ma consommation moyenne par jour ?"
                    st.rerun()
                if st.button("Quelle est ma consommation moyenne par heure ?", key="sugg_moyenne_heure"):
                    st.session_state.user_question = "Quelle est ma consommation moyenne par heure ?"
                    st.rerun()
                if st.button("Quelle est ma consommation moyenne par semaine ?", key="sugg_moyenne_semaine"):
                    st.session_state.user_question = "Quelle est ma consommation moyenne par semaine ?"
                    st.rerun()
            with col2:
                if st.button("Quelle est ma consommation moyenne par mois ?", key="sugg_moyenne_mois"):
                    st.session_state.user_question = "Quelle est ma consommation moyenne par mois ?"
                    st.rerun()
                if st.button("Quelle est ma consommation moyenne par an ?", key="sugg_moyenne_an"):
                    st.session_state.user_question = "Quelle est ma consommation moyenne par an ?"
                    st.rerun()
        
        # Catégorie 3: Consommation par moment/contexte
        with st.expander("🏠 **Consommation par moment/contexte**", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Combien ai-je consommé samedi ?", key="sugg_samedi"):
                    st.session_state.user_question = "Combien ai-je consommé samedi ?"
                    st.rerun()
            with col2:
                if st.button("Quel est mon total de consommation cette semaine ?", key="sugg_total_semaine"):
                    st.session_state.user_question = "Quel est mon total de consommation cette semaine ?"
                    st.rerun()
    
    def dashboard_tab(self):
        """Onglet 2 : Tableau de bord électrique - Structure restructurée en 4 parties"""
        st.markdown("## 📊 Tableau de Bord - Consommation Électrique")
        
        # Chargement des données
        try:
            conn = duckdb.connect('data_genere/processed/energy_fictional_2h.duckdb')
            df = conn.execute("SELECT * FROM energy_data").fetchdf()
            conn.close()
            
            if df.empty:
                st.warning("⚠️ Aucune donnée disponible")
                return
            
            # Conversion des colonnes
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['month'] = df['timestamp'].dt.month
            df['year'] = df['timestamp'].dt.year
            df['week'] = df['timestamp'].dt.isocalendar().week
            df['day_of_week'] = df['timestamp'].dt.day_name()
            
            # 🎯 PÉRIODE DE RÉFÉRENCE : 12 derniers mois (période glissante depuis hier)
            yesterday = pd.Timestamp.now().normalize() - pd.Timedelta(days=1)
            start_date = yesterday - pd.DateOffset(months=12)
            
            # Filtrer les données sur les 12 derniers mois
            df_12m = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= yesterday)]
            
            if df_12m.empty:
                st.warning("⚠️ Aucune donnée disponible sur les 12 derniers mois")
                return
            
            # 🔹 PARTIE 1 - KPIs ÉLECTRIQUE (12 derniers mois)
            st.markdown("### 🔹 KPIs Électrique (sur les 12 derniers mois)")
            
            # Calculs des KPIs
            total_consumption_12m = df_12m['energy_total_kwh'].sum()
            avg_monthly_consumption = total_consumption_12m / 12
            avg_weekly_consumption = total_consumption_12m / 52  # 52 semaines
            avg_daily_consumption = total_consumption_12m / 365  # 365 jours
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="electric-metric">
                    ⚡ Consommation Totale<br>
                    <strong>{total_consumption_12m:.1f} kWh</strong><br>
                    <small>12 derniers mois</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="electric-metric">
                    📅 Moyenne Mensuelle<br>
                    <strong>{avg_monthly_consumption:.1f} kWh</strong><br>
                    <small>12 derniers mois</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="electric-metric">
                    📊 Moyenne Hebdomadaire<br>
                    <strong>{avg_weekly_consumption:.1f} kWh</strong><br>
                    <small>12 derniers mois</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="electric-metric">
                    📈 Moyenne Journalière<br>
                    <strong>{avg_daily_consumption:.1f} kWh</strong><br>
                    <small>12 derniers mois</small>
                </div>
                """, unsafe_allow_html=True)
            
            # 🔹 PARTIE 2 - CONSOMMATION TOTALE MENSUELLE (12 derniers mois)
            st.markdown("### 🔹 Consommation Totale Mensuelle")
            
            # Données mensuelles sur les 12 derniers mois
            monthly_data_12m = df_12m.groupby(['year', 'month']).agg({
                'energy_total_kwh': 'sum'
            }).reset_index()
            
            monthly_data_12m['date'] = pd.to_datetime(monthly_data_12m[['year', 'month']].assign(day=1))
            monthly_data_12m = monthly_data_12m.sort_values('date')
            
            fig1 = px.bar(
                monthly_data_12m,
                x='date',
                y='energy_total_kwh',
                title="Consommation Électrique Mensuelle - 12 Derniers Mois",
                color_discrete_sequence=['#2563eb'],
                template="plotly_white"
            )
            fig1.update_layout(
                xaxis_title="Mois",
                yaxis_title="Consommation (kWh)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # 🔹 PARTIE 3 - RÉPARTITION PAR TYPE D'ÉQUIPEMENT (12 derniers mois)
            st.markdown("### 🔹 Répartition par Type d'Équipement")
            
            # Calculs sur les 12 derniers mois (CORRECTION DU CALCUL)
            kitchen_total_12m = df_12m['sub_metering_1_kwh'].sum()
            laundry_total_12m = df_12m['sub_metering_2_kwh'].sum()
            water_heater_total_12m = df_12m['sub_metering_3_kwh'].sum()
            
            # 🔧 CORRECTION : Utiliser energy_total_kwh au lieu de global_active_power_kw
            total_energy_12m = df_12m['energy_total_kwh'].sum()
            others_total_12m = total_energy_12m - (kitchen_total_12m + laundry_total_12m + water_heater_total_12m)
            
            # Disposition : Métriques à gauche, graphique à droite
            left_col, right_col = st.columns([1, 2])
            
            with left_col:
                # Métriques détaillées par sous-compteur (12 derniers mois) - ALIGNEMENT AMÉLIORÉ
                st.markdown(f"""
                <div class="electric-card" style="margin-bottom: 15px;">
                    <div class="analysis-section">
                        <div class="section-title">🍳 Cuisine</div>
                        <div class="section-content">
                            <small>
                            <strong>Moyenne :</strong> {df_12m['sub_metering_1_kwh'].mean() * 1000:.2f} W<br>
                            <strong>Maximum :</strong> {df_12m['sub_metering_1_kwh'].max() * 1000:.2f} W<br>
                            <strong>Total :</strong> {kitchen_total_12m:.2f} kWh
                            </small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="electric-card" style="margin-bottom: 15px;">
                    <div class="analysis-section">
                        <div class="section-title">👕 Buanderie</div>
                        <div class="section-content">
                            <small>
                            <strong>Moyenne :</strong> {df_12m['sub_metering_2_kwh'].mean() * 1000:.2f} W<br>
                            <strong>Maximum :</strong> {df_12m['sub_metering_2_kwh'].max() * 1000:.2f} W<br>
                            <strong>Total :</strong> {laundry_total_12m:.2f} kWh
                            </small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="electric-card" style="margin-bottom: 15px;">
                    <div class="analysis-section">
                        <div class="section-title">🛁 Ballon d'eau chaude</div>
                        <div class="section-content">
                            <small>
                            <strong>Moyenne :</strong> {df_12m['sub_metering_3_kwh'].mean() * 1000:.2f} W<br>
                            <strong>Maximum :</strong> {df_12m['sub_metering_3_kwh'].max() * 1000:.2f} W<br>
                            <strong>Total :</strong> {water_heater_total_12m:.2f} kWh
                            </small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with right_col:
                # Camembert répartition (12 derniers mois) - SANS "AUTRES"
                equipment_data_12m = {
                    'Cuisine': kitchen_total_12m,
                    'Buanderie': laundry_total_12m,
                    'Ballon d\'eau chaude': water_heater_total_12m
                }
                
                fig2 = px.pie(
                    values=list(equipment_data_12m.values()),
                    names=list(equipment_data_12m.keys()),
                    title="Répartition de la Consommation - 12 Derniers Mois",
                    color_discrete_sequence=['#2563eb', '#10b981', '#3b82f6']
                )
                fig2.update_layout(
                    height=500,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=14)
                    )
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # 🔹 PARTIE 4 - ANALYSE INTELLIGENTE
            st.markdown("### 🔹 Analyse Intelligente")
            
            # Calculs pour l'analyse intelligente (MISE À JOUR DES RÉFÉRENCES)
            total_consumption_12m = sum(equipment_data_12m.values())
            kitchen_pct = (equipment_data_12m['Cuisine'] / total_consumption_12m) * 100
            laundry_pct = (equipment_data_12m['Buanderie'] / total_consumption_12m) * 100
            water_heater_pct = (equipment_data_12m['Ballon d\'eau chaude'] / total_consumption_12m) * 100
            
            # Poste le plus gourmand
            max_consumer = max([
                ('Cuisine', kitchen_pct),
                ('Buanderie', laundry_pct),
                ('Ballon d\'eau chaude', water_heater_pct)
            ], key=lambda x: x[1])
            
            # Tendances (comparaison avec les 6 derniers mois vs 6 mois précédents)
            mid_point = yesterday - pd.DateOffset(months=6)
            df_first_6m = df_12m[df_12m['timestamp'] < mid_point]
            df_last_6m = df_12m[df_12m['timestamp'] >= mid_point]
            
            if not df_first_6m.empty and not df_last_6m.empty:
                consumption_first_6m = df_first_6m['energy_total_kwh'].sum()
                consumption_last_6m = df_last_6m['energy_total_kwh'].sum()
                trend_percentage = ((consumption_last_6m - consumption_first_6m) / consumption_first_6m) * 100
                trend_direction = "📈 Hausse" if trend_percentage > 0 else "📉 Baisse"
            else:
                trend_percentage = 0
                trend_direction = "➡️ Stable"
            
            # Moyennes nationales (simulation) - FOYER DE 3 PERSONNES
            national_avg_daily_3p = 10.5  # kWh/jour (moyenne française pour 3 personnes - plus réaliste)
            user_avg_daily = avg_daily_consumption
            comparison_percentage = ((user_avg_daily - national_avg_daily_3p) / national_avg_daily_3p) * 100
            
            # Pics de consommation
            max_power_12m = df_12m['global_active_power_kw'].max()
            avg_power_12m = df_12m['global_active_power_kw'].mean()
            peak_factor = max_power_12m / avg_power_12m if avg_power_12m > 0 else 1
            
            # Affichage de l'analyse intelligente
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="electric-card">
                    <h4>📊 Comparaison Nationale</h4>
                    <p><strong>Votre consommation :</strong> {user_avg_daily:.1f} kWh/jour</p>
                    <p><strong>Moyenne française (3 pers.) :</strong> {national_avg_daily_3p} kWh/jour</p>
                    <p><strong>Différence :</strong> {comparison_percentage:+.1f}%</p>
                    <p><em>{'Au-dessus' if comparison_percentage > 0 else 'En-dessous'} de la moyenne nationale</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="electric-card">
                    <h4>📈 Tendances</h4>
                    <p><strong>Évolution 6 derniers mois :</strong> {trend_direction}</p>
                    <p><strong>Variation :</strong> {trend_percentage:+.1f}%</p>
                    <p><strong>Poste le plus gourmand :</strong> {max_consumer[0]} ({max_consumer[1]:.1f}%)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="electric-card">
                    <h4>⚠️ Alertes</h4>
                    <p><strong>Pic de consommation :</strong> {max_power_12m:.2f} kW</p>
                    <p><strong>Facteur de pic :</strong> {peak_factor:.1f}x la moyenne</p>
                    <p><strong>Statut :</strong> {'🚨 Pic anormal détecté' if peak_factor > 3 else '✅ Normal'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="electric-card">
                    <h4>💡 Conseils d'Économie</h4>
                    <ul>
                        <li>🕐 <strong>Heures creuses :</strong> Déplacer la charge vers 23h-7h</li>
                        <li>🛁 <strong>Ballon d'eau chaude :</strong> Programmer les heures de chauffe</li>
                        <li>🔍 <strong>Surveillance :</strong> Vérifier les appareils en pic</li>
                        <li>💰 <strong>Potentiel :</strong> Économies de 10-15% possibles</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
    
    def forecast_tab(self):
        """Onglet 3 : Prévisions Prophet"""
        try:
            # Utiliser la page de prévisions existante
            show_forecast_page()
            
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des prévisions : {str(e)}")
            st.markdown("""
            <div class="electric-card">
                <h2>🚧 Prévisions en Développement</h2>
                <p>Les prévisions Prophet seront bientôt disponibles !</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Fonction principale"""
    # Initialisation de l'application
    app = EnergyAgentApp()
    
    # En-tête
    app.show_header()
    
    # Sidebar complète
    app.show_sidebar()
    
        # Navigation par onglets
    tab1, tab2, tab3 = st.tabs(["💬 Chat Intelligent", "📊 Tableau de Bord", "📈 Prévisions"])
    
    with tab1:
        app.chat_tab()
    
    with tab2:
        app.dashboard_tab()
    
    with tab3:
        app.forecast_tab()

if __name__ == "__main__":
    main()
