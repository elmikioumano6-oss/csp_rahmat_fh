import streamlit as st
import streamlit_shadcn_ui as ui

def afficher_espace_profs():
    st.markdown("### 📱 Espace Enseignant - Mobile First")
    st.markdown("Interface optimisée pour la saisie rapide des notes et des absences.")
    
    # Indicateurs clés sous forme de cartes modernes
    col1, col2 = st.columns(2)
    with col1:
        ui.metric_card(
            title="Classes Assignées", 
            content="3 Classes", 
            description="Terminale D, 3ème", 
            key="profs_card_1"
        )
    with col2:
        ui.metric_card(
            title="État des Notes", 
            content="En cours", 
            description="Trimestre 1", 
            key="profs_card_2"
        )
    
    st.markdown("---")
    st.markdown("#### 📝 Gestion des Évaluations")
    
    # Sélection ergonomique pour smartphone
    classe_selection = st.selectbox("Sélectionner la classe", ["Terminale D", "Terminale A", "Troisième A"])
    matiere_selection = st.selectbox("Sélectionner la matière", ["Mathématiques", "Physique-Chimie", "SVT"])
    
    # Bouton d'action large (parfait pour le tactile)
    if st.button("🚀 Ouvrir la grille de saisie", use_container_width=True, type="primary"):
        st.success(f"Mode saisie activé : {matiere_selection} pour {classe_selection}")
        # Ici vous intégrerez votre tableau de saisie des notes existant