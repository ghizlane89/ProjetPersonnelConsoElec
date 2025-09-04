#!/usr/bin/env python3
"""
Onglet Prévisions - Phase 1
Affiche un message informatif en attendant l'implémentation Prophet
"""

import streamlit as st
from core.shared.forecast_interface import forecast_interface

def show_forecast_page():
    """
    Affiche l'onglet Prévisions
    Conforme au cahier des charges - Section 3.3
    """
    st.title("📈 Prévisions")
    st.markdown("---")
    
    # Vérifier le statut des prévisions
    status = forecast_interface.get_forecast_status()
    
    if not status["available"]:
        # Phase 1 : Prévisions non disponibles
        st.info("🚧 **Prévisions en cours de développement**")
        
        st.markdown("""
        ### 📋 Fonctionnalités prévues
        
        **Onglet 3 : Prévisions** (prochaine version)
        
        ✅ **Graphiques de projection** (courbes) pour des périodes :
        - Journalières
        - Hebdomadaires  
        - Mensuelles
        
        ✅ **Indication des incertitudes** via bandes ou infobulles
        - Exemple : "Prévision : 2,5 ± 0,3 kWh"
        
        ✅ **Mise en avant des tendances** ou pics anticipés
        - Exemple : "Pic prévu à 18h demain"
        
        ✅ **Performance** : Génération des graphiques en <2 secondes
        """)
        
        # Suggestions pour l'utilisateur
        st.markdown("### 💡 En attendant les prévisions...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 Consultez l'historique :**
            - Analysez vos consommations passées
            - Identifiez vos habitudes de consommation
            - Détectez les pics et les tendances
            """)
        
        with col2:
            st.markdown("""
            **🔍 Explorez le tableau de bord :**
            - Visualisez la répartition par zones
            - Comparez les périodes
            - Analysez les patterns saisonniers
            """)
        
        # Placeholder pour les graphiques futurs
        st.markdown("### 📈 Graphiques de prévisions (à venir)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**Prévisions journalières**\n\nCourbes de projection pour les prochaines 24h")
        
        with col2:
            st.info("**Prévisions hebdomadaires**\n\nTendances pour les 7 prochains jours")
        
        with col3:
            st.info("**Prévisions mensuelles**\n\nProjections pour le mois à venir")
        
        # Informations techniques
        st.markdown("---")
        st.caption("""
        **Technologies utilisées :**
        - Prophet (Facebook) pour les prévisions temporelles
        - Intégration avec l'architecture MCP existante
        - Respect du SLA <2 secondes
        """)
        
    else:
        # Phase 2 : Prévisions disponibles (Prophet implémenté)
        st.success("✅ **Prévisions disponibles**")
        
        # Interface de sélection
        col1, col2 = st.columns(2)
        
        with col1:
            horizon = st.selectbox(
                "Horizon de prévision",
                ["1d", "7d", "30d"],
                format_func=lambda x: {
                    "1d": "1 jour",
                    "7d": "7 jours", 
                    "30d": "30 jours"
                }[x]
            )
        
        with col2:
            model = st.selectbox(
                "Modèle de prévision",
                ["simple", "advanced"],
                format_func=lambda x: {
                    "simple": "Simple",
                    "advanced": "Avancé"
                }[x]
            )
        
        # Génération des prévisions
        if st.button("🔮 Générer les prévisions", type="primary"):
            with st.spinner("Génération des prévisions..."):
                result = forecast_interface.generate_forecast(horizon, model)
                
                if result["status"] == "success":
                    st.success("✅ Prévisions générées avec succès")
                    # TODO: Affichage des graphiques Prophet
                else:
                    st.error(f"❌ Erreur : {result['message']}")

if __name__ == "__main__":
    show_forecast_page()









