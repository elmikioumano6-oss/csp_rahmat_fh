from datetime import datetime
from database.db_config import SessionLocal
from database.models import Eleve, Note, Presence
import pandas as pd
import streamlit as st


def afficher_espace_parent():
    st.subheader("👨‍👩‍👧 Espace Parent - Suivi de l'Enfant")

    db = SessionLocal()
    # Récupération de l'ID du parent connecté depuis la session
    parent_id = st.session_state.get("user_entity_id")

    # 1. Filtrer uniquement les élèves rattachés à ce parent
    enfants = db.query(Eleve).filter(Eleve.parent_id == parent_id).all()

    if not enfants:
        st.warning(
            "⚠️ Aucun élève n'est actuellement rattaché à votre compte parent. Veuillez contacter l'administration de l'établissement."
        )
        db.close()
        return

    # 2. Sélecteur si le parent a plusieurs enfants inscrits
    noms_enfants = [
        f"{e.nom} {e.prenom} - Classe : {e.classe.libelle if e.classe else 'Non assignée'}"
        for e in enfants
    ]
    choix_enfant = st.selectbox("🎯 Sélectionnez votre enfant :", noms_enfants)

    # Récupération de l'objet élève correspondant au choix
    index_selection = noms_enfants.index(choix_enfant)
    enfant_actif = enfants[index_selection]

    st.markdown("---")
    st.markdown(
        f"### 📂 Dossier Académique de : **{enfant_actif.nom} {enfant_actif.prenom}** (Matricule : `{enfant_actif.matricule}`)"
    )

    # 3. Onglets sécurisés pour afficher uniquement les données de cet enfant
    tab_notes, tab_presence, tab_bulletin = st.tabs([
        "📝 Notes & Évaluations",
        "⏰ Présences, Retards & Absences",
        "📄 Bulletins Scolaires",
    ])

    with tab_notes:
        st.markdown("#### Notes obtenues")
        notes = db.query(Note).filter(Note.eleve_id == enfant_actif.id).all()
        if notes:
            data_notes = []
            for n in notes:
                matiere_libelle = (
                    n.matiere.nom
                    if hasattr(n, "matiere") and n.matiere
                    else "Matière"
                )
                data_notes.append({
                    "Matière": matiere_libelle,
                    "Note Classe": getattr(n, "note_classe", 0.0) or 0.0,
                    "Note Compo": getattr(n, "note_compo", 0.0) or 0.0,
                    "Semestre": getattr(n, "semestre", 1),
                })
            st.dataframe(
                pd.DataFrame(data_notes),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Aucune note enregistrée pour le moment.")

    with tab_presence:
        st.markdown("#### Suivi des présences, retards et absences")
        presences = (
            db.query(Presence)
            .filter(Presence.eleve_id == enfant_actif.id)
            .all()
        )
        if presences:
            data_pres = []
            for p in presences:
                data_pres.append({
                    "Date": getattr(p, "date", "N/A"),
                    "Statut": getattr(p, "statut", "Présent"),
                    "Motif": getattr(p, "motif", "-"),
                })
            st.dataframe(
                pd.DataFrame(data_pres),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Aucun incident de présence ou d'absence enregistré.")

    with tab_bulletin:
        st.markdown("#### Bulletins scolaires")
        st.info(
            "📄 Les bulletins officiels et récapitulatifs de notes sont édités et mis à disposition par l'administration de l'établissement."
        )

    db.close()