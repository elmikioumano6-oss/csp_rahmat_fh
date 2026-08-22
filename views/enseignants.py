import streamlit as st

@st.cache_data(ttl=600)
def charger_infos_enseignant():
    # Données statiques ou pré-chargées mises en cache pour un affichage instantané
    return {
        "classes": ["Terminale D", "Terminale A", "Troisième A"],
        "matieres": ["Mathématiques", "Physique-Chimie", "SVT"]
    }

def afficher_enseignants():
    st.markdown("### 📱 Espace Enseignant - Mobile First")
    st.markdown("Interface optimisée pour la saisie rapide des notes et des absences.")
    
    # Récupération rapide via le cache
    infos = charger_infos_enseignant()

    # Indicateurs clés sous forme de colonnes stylisées (cartes natives)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div style="background-color: #1E293B; padding: 15px; border-radius: 10px; border-left: 5px solid #D97706; color: white;">
                <h4 style="margin: 0; font-size: 0.9rem; color: #94A3B8;">Classes Assignées</h4>
                <h2 style="margin: 5px 0 0 0; font-size: 1.5rem; color: #F8FAFC;">3 Classes</h2>
                <p style="margin: 5px 0 0 0; font-size: 0.8rem; color: #CBD5E1;">Terminale D, 3ème</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div style="background-color: #1E293B; padding: 15px; border-radius: 10px; border-left: 5px solid #10B981; color: white;">
                <h4 style="margin: 0; font-size: 0.9rem; color: #94A3B8;">État des Notes</h4>
                <h2 style="margin: 5px 0 0 0; font-size: 1.5rem; color: #F8FAFC;">En cours</h2>
                <p style="margin: 5px 0 0 0; font-size: 0.8rem; color: #CBD5E1;">Trimestre 1</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📝 Gestion des Évaluations")
    
    # Sélection ergonomique pour smartphone
    classe_selection = st.selectbox("Sélectionner la classe", infos["classes"])
    matiere_selection = st.selectbox("Sélectionner la matière", infos["matieres"])
    
    # Bouton d'action large (parfait pour le tactile)
    if st.button("🚀 Ouvrir la grille de saisie", use_container_width=True, type="primary"):
        st.success(f"Mode saisie activé : {matiere_selection} pour {classe_selection}")