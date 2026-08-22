from database.db_config import SessionLocal
from database.models import Classe, Eleve, Note, User
import pandas as pd
import streamlit as st


def afficher_espace_parent():
    st.subheader("👨‍👩‍👧 Espace Parent - Suivi de l'Enfant")

    db = SessionLocal()
    try:
        user_role = st.session_state.get("user_role", "admin")
        current_username = st.session_state.get("username", "")

        # Si l'utilisateur est admin, on lui permet de choisir le compte parent à superviser
        if user_role == "admin":
            parents_all = db.query(User).filter(User.role == "parent").all()
            if not parents_all:
                st.warning(
                    "⚠️ Aucun compte parent n'a été créé dans le système."
                )
                return

            parent_dict = {p.username: p.id for p in parents_all}
            choix_parent_nom = st.selectbox(
                "🔍 [Admin] Sélectionner le compte parent à superviser",
                list(parent_dict.keys()),
            )
            parent_user_id = parent_dict[choix_parent_nom]
        else:
            parent_user = (
                db.query(User)
                .filter(User.username == current_username)
                .first()
            )
            if not parent_user:
                st.warning("⚠️ Compte parent introuvable.")
                return
            parent_user_id = parent_user.id

        # Récupérer les élèves liés à ce parent via parent_id
        enfants = (
            db.query(Eleve).filter(Eleve.parent_id == parent_user_id).all()
        )

        if not enfants:
            st.info(
                "ℹ️ Aucun enfant n'est actuellement associé à ce compte parent."
            )
            return

        # Sélectionner l'enfant si le parent en a plusieurs
        enfant_options = {
            f"{e.nom} {e.prenom} - Classe : {e.classe.nom if e.classe else 'Non assignée'} [Matricule: {e.matricule}]": e.id
            for e in enfants
        }

        choix_enfant = st.selectbox(
            "Sélectionner l'enfant", list(enfant_options.keys())
        )
        enfant_id = enfant_options[choix_enfant]

        enfant_actif = db.query(Eleve).filter(Eleve.id == enfant_id).first()

        if enfant_actif:
            st.markdown("---")
            st.write(
                f"### 📋 Bulletins & Notes de : {enfant_actif.nom} {enfant_actif.prenom}"
            )

            # Récupérer les notes de l'élève
            notes = (
                db.query(Note).filter(Note.eleve_id == enfant_actif.id).all()
            )
            if notes:
                data_notes = []
                for n in notes:
                    matiere_nom = (
                        n.matiere.nom if n.matiere else "Matière inconnue"
                    )
                    data_notes.append(
                        {
                            "Matière": matiere_nom,
                            "Semestre": n.semestre,
                            "Note Classe (/20)": n.note_classe or 0.0,
                            "Note Compo (/20)": n.note_compo or 0.0,
                        }
                    )
                st.dataframe(
                    pd.DataFrame(data_notes),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("Aucune note enregistrée pour le moment.")

    finally:
        db.close()