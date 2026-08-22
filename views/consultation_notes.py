import streamlit as st
import streamlit_shadcn_ui as ui

def afficher_consultation_notes():
    st.markdown("### 🎓 Espace Parents & Élèves")
    st.markdown("Consultez les notes et les moyennes en temps réel.")
    
    # Barre de recherche par matricule adaptée aux mobiles
    matricule = st.text_input("Entrez le Matricule de l'élève", placeholder="Ex: RAHMAT-2026-001")
    
    if matricule:
        # Simulation de récupération des données (à lier à votre base PostgreSQL)
        st.markdown("---")
        st.markdown("#### 📄 Fiche de l'Élève")
        
        # Affichage des métriques de l'élève en cartes modernes
        col1, col2 = st.columns(2)
        with col1:
            ui.metric_card(
                title="Moyenne Trimestrielle", 
                content="14.5 / 20", 
                description="Rang : 3ème / 45", 
                key="eleve_moy"
            )
        with col2:
            ui.metric_card(
                title="Assiduité", 
                content="0 Absence", 
                description="Comportement exemplaire", 
                key="eleve_abs"
            )
        
        st.markdown("---")
        st.markdown("#### 📊 Dernières Notes Enregistrées")
        
        # Tableau récapitulatif propre
        notes_data = [
            {"Matière": "Mathématiques", "Note": "15/20",appréciation: "Très bien"},
            {"Matière": "Physique-Chimie", "Note": "14/20", appréciation: "Bien"},
            {"Matière": "Français", "Note": "13.5/20", appréciation: "Assez bien"}
        ]
        
        for n in notes_data:
            ui.card(
                title=n["Matière"],
                content=f"Note : {n['Note']}",
                description=f"Appréciation : {n['appréciation']}",
                key=f"note_{n['Matière']}"
            )
    else:
        st.info("💡 Veuillez entrer un matricule valide pour afficher le bulletin de l'élève.")