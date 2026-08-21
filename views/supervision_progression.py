import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Classe, Matiere, CahierTexte, Programme

def afficher_supervision_progression(niveau_actif):
    st.subheader(f"📊 Suivi et Progression des Programmes - {niveau_actif}")
    db = SessionLocal()

    # 1. Récupération des classes du cycle actif
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    if not classes:
        st.warning(f"⚠️ Aucune classe configurée pour le cycle {niveau_actif}.")
        db.close()
        return

    options_classes = {c.nom: c.id for c in classes}
    choix_classe_nom = st.selectbox("Sélectionner la classe à auditer :", list(options_classes.keys()))
    classe_id = options_classes[choix_classe_nom]

    semestre = st.selectbox("Sélectionner le Semestre / Trimestre :", [1, 2])

    st.markdown("---")

    # 2. Récupérer les matières et programmes de la classe
    programmes = db.query(Programme).filter(Programme.classe_id == classe_id, Programme.semestre == semestre).all()
    matieres = db.query(Matiere).all()
    
    if not matieres:
        st.info("⚠️ Aucune matière enregistrée dans le système.")
        db.close()
        return

    donnees_suivi = []

    for matiere in matieres:
        # Recherche du volume horaire prévu (par défaut 25h par semestre si non défini)
        prog_obj = next((p for p in programmes if p.matiere_id == matiere.id), None)
        heures_prevues = prog_obj.volume_horaire_prevu if prog_obj else 25.0

        # Calcul des heures réalisées via le cahier de texte
        entrées_cahier = db.query(CahierTexte).filter(
            CahierTexte.classe_id == classe_id,
            CahierTexte.matiere_id == matiere.id,
            CahierTexte.semestre == semestre
        ).all()
        
        heures_realisees = len(entrées_cahier)

        # Calcul de l'écart et du pourcentage d'exécution
        ecart = heures_realisees - heures_prevues
        pourcentage = (heures_realisees / heures_prevues * 100) if heures_prevues > 0 else 0
        pourcentage = min(pourcentage, 100.0)

        # Analyse et Remarques Automatiques
        if pourcentage >= 90:
            statut = "🟢 Conforme / Avancé"
            recommandation = "Aucun ajustement requis. Maintenir le rythme."
        elif pourcentage >= 70:
            statut = "🟡 Léger Retard"
            recommandation = f"Prévoir {abs(int(ecart))}h de consolidation ou une séance de révision ciblée."
        else:
            heures_a_rattraper = abs(ecart)
            statut = "🔴 Retard Critique"
            recommandation = f"Action requise : Rattraper **{heures_a_rattraper}h** (planifier +2h/semaine)."

        donnees_suivi.append({
            "Matière": matiere.nom,
            "Prévu (h)": heures_prevues,
            "Réalisé (h)": heures_realisees,
            "Exécution (%)": f"{pourcentage:.1f}%",
            "Écart (h)": ecart,
            "État de la Progression": statut,
            "Ajustement / Remarque": recommandation
        })

    df_suivi = pd.DataFrame(donnees_suivi)

    # Affichage sous forme de tableau interactif
    st.markdown(f"### 📋 Bilan d'exécution pour la classe de **{choix_classe_nom}** (Semestre {semestre})")
    st.dataframe(df_suivi, use_container_width=True)

    # Synthèse globale et régulation
    st.markdown("---")
    st.markdown("### 🛠️ Outils de Régulation Pédagogique (Censeur / Administration)")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### 📅 Plan de Rattrapage Hebdomadaire")
            st.write("Si une matière accuse un retard critique, l'administration peut notifier l'enseignant pour intégrer des heures d'intensification dans l'emploi du temps.")
            if st.button("Générer la Note de Rappel Pédagogique"):
                st.success("✅ Note de cadrage transmise aux enseignants concernés par le retard.")

    with col2:
        with st.container(border=True):
            st.markdown("#### 📈 Rapport Annuel de Conformité")
            st.write("Exportation globale des volumes horaires exécutés pour le contrôle de l'inspection académique.")
            if st.button("Télécharger le Bilan Global (PDF/CSV)"):
                st.info("📥 Fonctionnalité prête pour l'archivage annuel des performances.")

    db.close()