import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import User, Eleve, Note, Presence, Matiere

def afficher_espace_parent():
    st.subheader("👨‍👩‍👧 Espace Parent - Suivi de l'enfant")
    db = SessionLocal()
    
    try:
        username = st.session_state.get('username')
        parent_user = db.query(User).filter(User.username == username).first()
        
        if not parent_user:
            st.error("Utilisateur non trouvé.")
            return

        # Récupération des IDs des enfants rattachés (multi-enfants ou rétrocompatibilité)
        eleve_ids = []
        raw_enfants = getattr(parent_user, 'enfants_ids', None)
        if raw_enfants:
            eleve_ids = [int(i) for i in raw_enfants.split(",") if i.isdigit()]
        elif parent_user.entite_id:
            eleve_ids = [parent_user.entite_id]

        if not eleve_ids:
            st.warning("⚠️ Aucun enfant n'est actuellement rattaché à votre compte. Veuillez contacter l'administration de l'école.")
            return

        eleves = db.query(Eleve).filter(Eleve.id.in_(eleve_ids)).all()
        if not eleves:
            st.warning("⚠️ Fiche élève introuvable pour vos enfants rattachés.")
            return

        # Sélectionner l'enfant si le parent en a plusieurs
        if len(eleves) > 1:
            choix_eleve = st.selectbox(
                "Sélectionner l'enfant à consulter", 
                eleves, 
                format_func=lambda x: f"{x.nom} {x.prenom} (Classe : {x.classe.nom if x.classe else 'N/A'})"
            )
        else:
            choix_eleve = eleves[0]

        st.markdown("---")
        st.markdown(f"### 📚 Dossier de : **{choix_eleve.nom} {choix_eleve.prenom}**")
        st.info(f"📌 Matricule : **{choix_eleve.matricule}** | 🏫 Classe : **{choix_eleve.classe.nom if choix_eleve.classe else 'N/A'}**")

        # Organisation par onglets pour une clarté maximale
        tab1, tab2, tab3 = st.tabs(["📝 Notes & Évaluations", "📋 Absences & Retards", "📊 Résultats & Bulletins"])

        with tab1:
            st.markdown("#### 📝 Notes par matière")
            notes = db.query(Note).filter(Note.eleve_id == choix_eleve.id).all()
            if notes:
                data_notes = []
                for n in notes:
                    matiere = db.query(Matiere).filter(Matiere.id == n.matiere_id).first()
                    data_notes.append({
                        "Matière": matiere.nom if matiere else "Inconnue",
                        "Note Classe /20": n.note_classe,
                        "Note Compo /20": n.note_compo,
                        "Semestre": n.semestre
                    })
                st.dataframe(pd.DataFrame(data_notes), use_container_width=True)
            else:
                st.info("Aucune note enregistrée pour le moment.")

        with tab2:
            st.markdown("#### 📋 Historique des Absences et Retards")
            presences = db.query(Presence).filter(Presence.eleve_id == choix_eleve.id).all()
            if presences:
                data_pres = [{"Date": p.date, "Statut": p.statut} for p in presences]
                st.dataframe(pd.DataFrame(data_pres), use_container_width=True)
            else:
                st.success("✅ Aucune absence ni retard enregistré. Excellent assiduité !")

        with tab3:
            st.markdown("#### 📊 Aperçu des Résultats & Moyenne")
            notes = db.query(Note).filter(Note.eleve_id == choix_eleve.id).all()
            if notes:
                total_points = 0
                total_coeffs = 0
                for n in notes:
                    matiere = db.query(Matiere).filter(Matiere.id == n.matiere_id).first()
                    coeff = matiere.coefficient if matiere else 1
                    # Calcul de la moyenne de la matière (Exemple : (Classe + Compo*2) / 3)
                    moy_mat = (n.note_classe + (n.note_compo * 2)) / 3
                    total_points += moy_mat * coeff
                    total_coeffs += coeff
                
                if total_coeffs > 0:
                    moyenne_generale = total_points / total_coeffs
                    st.metric("Moyenne Générale Estimée", f"{moyenne_generale:.2f} / 20")
                else:
                    st.info("Calcul de moyenne indisponible.")
            else:
                st.info("Pas assez de notes pour estimer la moyenne générale.")
            
            st.markdown("---")
            st.info("💡 Les bulletins officiels semestriels validés par le conseil de classe sont disponibles auprès de la direction de l'établissement.")

    finally:
        db.close()
