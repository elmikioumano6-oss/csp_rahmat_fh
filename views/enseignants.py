from datetime import datetime
import pandas as pd
from database.db_config import SessionLocal
from database.models import (
    Affectation,
    Classe,
    Enseignant,
    Eleve,
    LogActivite,
    Matiere,
    Note,
    User,
)
import streamlit as st


def afficher_enseignants(niveau_actif=None):
    user_role = st.session_state.get("user_role", "admin")

    # --- SI C'EST UN PROFESSEUR : Afficher son Espace Dédié ---
    if user_role == "prof":
        afficher_espace_prof_dedie()
        return

    # --- SI C'EST UN ADMIN : Gestion complète des enseignants & affectations ---
    st.subheader("👨‍🏫 Gestion des Enseignants & Affectations")

    db = SessionLocal()
    try:
        tab_liste, tab_ajout, tab_affectation = st.tabs(
            [
                "📋 Liste des Enseignants",
                "➕ Ajouter un Enseignant",
                "🔗 Affectations",
            ]
        )

        with tab_liste:
            st.write("### Enseignants enregistrés")
            enseignants = db.query(Enseignant).all()
            if enseignants:
                data = [
                    {
                        "ID": e.id,
                        "Nom": e.nom,
                        "Prénom": e.prenom,
                        "Spécialité": e.specialite or "N/A",
                        "Téléphone": e.telephone or "N/A",
                        "Compte Utilisateur ID": e.user_id or "Aucun",
                    }
                    for e in enseignants
                ]
                st.dataframe(
                    pd.DataFrame(data), use_container_width=True, hide_index=True
                )
            else:
                st.info(
                    "Aucun enseignant enregistré pour le moment. Utilisez l'onglet 'Ajouter un Enseignant'."
                )

        with tab_ajout:
            st.write("### Enregistrer un nouvel enseignant")
            
            # Récupérer les comptes ayant le rôle "prof" pour liaison
            comptes_profs = db.query(User).filter(User.role == "prof").all()
            compte_options = {"Aucun compte associé": None}
            for u in comptes_profs:
                compte_options[f"Compte: {u.username} (ID: {u.id})"] = u.id

            with st.form("form_ajout_enseignant", clear_on_submit=True):
                nom = st.text_input("Nom de l'enseignant")
                prenom = st.text_input("Prénom de l'enseignant")
                specialite = st.text_input("Spécialité (ex: Mathématiques, Histoire...)")
                telephone = st.text_input("Numéro de téléphone")
                sel_compte_label = st.selectbox("Lier à un Compte Utilisateur (Rôle Prof)", list(compte_options.keys()))

                submitted = st.form_submit_button("Enregistrer l'enseignant")
                if submitted:
                    if nom.strip() and prenom.strip():
                        user_id_associe = compte_options[sel_compte_label]
                        nouveau_prof = Enseignant(
                            nom=nom.strip().upper(),
                            prenom=prenom.strip(),
                            specialite=specialite.strip(),
                            telephone=telephone.strip(),
                            user_id=user_id_associe,
                        )
                        db.add(nouveau_prof)
                        db.add(
                            LogActivite(
                                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                utilisateur=st.session_state.get(
                                    "username", "Admin"
                                ),
                                action="AJOUT ENSEIGNANT",
                                details=f"Ajout de {nom} {prenom} avec compte ID: {user_id_associe}",
                            )
                        )
                        db.commit()
                        st.success(
                            "✅ Enseignant enregistré et lié à son compte avec succès !"
                        )
                        st.rerun()
                    else:
                        st.warning("⚠️ Le nom et le prénom sont obligatoires.")

        with tab_affectation:
            st.write("### Assigner un enseignant à une classe et une matière")
            
            enseignants_all = db.query(Enseignant).all()
            classes_all = db.query(Classe).all()
            matieres_all = db.query(Matiere).all()

            if not enseignants_all or not classes_all or not matieres_all:
                st.warning("⚠️ Assurez-vous d'avoir enregistré des enseignants, des classes et des matières avant de faire des affectations.")
            else:
                with st.form("form_affectation"):
                    ens_dict = {f"{e.nom} {e.prenom}": e.id for e in enseignants_all}
                    classe_dict = {f"{c.nom} ({c.cycle}) [ID:{c.id}]": c.id for c in classes_all}
                    matiere_dict = {m.nom: m.id for m in matieres_all}

                    sel_ens = st.selectbox("Sélectionner l'enseignant", list(ens_dict.keys()))
                    sel_classe = st.selectbox("Sélectionner la classe", list(classe_dict.keys()))
                    sel_matiere = st.selectbox("Sélectionner la matière", list(matiere_dict.keys()))

                    if st.form_submit_button("Lier l'enseignant à la classe et matière"):
                        nouvelle_aff = Affectation(
                            enseignant_id=ens_dict[sel_ens],
                            classe_id=classe_dict[sel_classe],
                            matiere_id=matiere_dict[sel_matiere]
                        )
                        db.add(nouvelle_aff)
                        db.commit()
                        st.success("✅ Affectation enregistrée avec succès !")
                        st.rerun()

    finally:
        db.close()


def afficher_espace_prof_dedie():
    st.subheader("👨‍🏫 Mon Espace Enseignant")
    st.markdown(
        "Interface dédiée pour consulter vos classes assignées et saisir vos notes en toute sécurité."
    )

    db = SessionLocal()
    try:
        current_username = st.session_state.get("username", "")
        current_user_id = st.session_state.get("user_entity_id")

        # Recherche de l'enseignant connecté par son user_id ou son nom
        enseignant = None
        if current_user_id:
            enseignant = db.query(Enseignant).filter(Enseignant.user_id == current_user_id).first()
        
        if not enseignant:
            enseignant = db.query(Enseignant).filter(Enseignant.nom.ilike(f"%{current_username}%")).first()
            
        if not enseignant:
            # Fallback de secours si aucun lien direct n'est trouvé
            enseignant = db.query(Enseignant).first()

        if not enseignant:
            st.warning("⚠️ Aucun profil enseignant n'est associé à votre compte utilisateur. Contactez l'administrateur.")
            return

        st.markdown(
            f"**Bienvenue, Professeur {enseignant.nom} {enseignant.prenom}**"
        )
        st.markdown("---")

        affectations = (
            db.query(Affectation)
            .filter(Affectation.enseignant_id == enseignant.id)
            .all()
        )
        if not affectations:
            st.info(
                "ℹ️ Aucune classe ne vous a encore été assignée par l'administration."
            )
            return

        classes_assignees = {
            f"{aff.classe.nom} ({aff.classe.cycle}) [ID:{aff.classe.id}]": aff.classe_id
            for aff in affectations
            if aff.classe
        }

        if not classes_assignees:
            st.warning("⚠️ Vos affectations ne comportent aucune classe valide.")
            return

        col1, col2 = st.columns(2)
        with col1:
            classe_libelle = st.selectbox(
                "🎯 Mes Classes Assignées", list(classes_assignees.keys())
            )
            classe_id_selectionnee = classes_assignees[classe_libelle]

        matieres_disponibles = {
            aff.matiere.nom: aff.matiere_id
            for aff in affectations
            if aff.classe_id == classe_id_selectionnee and aff.matiere
        }

        with col2:
            if matieres_disponibles:
                matiere_nom = st.selectbox(
                    "📚 Matières", list(matieres_disponibles.keys())
                )
                matiere_id_selectionnee = matieres_disponibles[matiere_nom]
            else:
                st.warning("Aucune matière liée à cette classe.")
                return

        st.markdown("---")

        tab_eleves, tab_notes = st.tabs(
            ["👥 Liste des Élèves", "📝 Saisie des Notes"]
        )

        with tab_eleves:
            eleves = (
                db.query(Eleve)
                .filter(Eleve.classe_id == classe_id_selectionnee)
                .order_by(Eleve.nom)
                .all()
            )
            if eleves:
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "Matricule": e.matricule,
                                "Nom": e.nom,
                                "Prénom": e.prenom,
                            }
                            for e in eleves
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("Aucun élève dans cette classe.")

        with tab_notes:
            st.write(f"### Saisie des Notes - {matiere_nom}")
            eleves = (
                db.query(Eleve)
                .filter(Eleve.classe_id == classe_id_selectionnee)
                .order_by(Eleve.nom)
                .all()
            )
            semestre = st.selectbox("Semestre", [1, 2], key="sem_prof_n")

            if eleves:
                with st.form("form_notes_prof_unique"):
                    notes_saisies = []
                    for el in eleves:
                        note_ex = (
                            db.query(Note)
                            .filter(
                                Note.eleve_id == el.id,
                                Note.matiere_id == matiere_id_selectionnee,
                                Note.semestre == semestre,
                            )
                            .first()
                        )
                        val_c = note_ex.note_classe if note_ex else 0.0
                        val_co = note_ex.note_compo if note_ex else 0.0

                        c1, c2, c3 = st.columns([3, 2, 2])
                        with c1:
                            st.text(f"{el.nom} {el.prenom}")
                        with c2:
                            nc = st.number_input(
                                "Classe (/20)",
                                0.0,
                                20.0,
                                float(val_c),
                                0.25,
                                key=f"nc_{el.id}",
                                label_visibility="collapsed",
                            )
                        with c3:
                            nco = st.number_input(
                                "Compo (/20)",
                                0.0,
                                20.0,
                                float(val_co),
                                0.25,
                                key=f"nco_{el.id}",
                                label_visibility="collapsed",
                            )

                        notes_saisies.append(
                            {"eleve_id": el.id, "nc": nc, "nco": nco}
                        )

                    if st.form_submit_button("Enregistrer les notes"):
                        for item in notes_saisies:
                            n_obj = (
                                db.query(Note)
                                .filter(
                                    Note.eleve_id == item["eleve_id"],
                                    Note.matiere_id == matiere_id_selectionnee,
                                    Note.semestre == semestre,
                                )
                                .first()
                            )
                            if n_obj:
                                n_obj.note_classe = item["nc"]
                                n_obj.note_compo = item["nco"]
                            else:
                                db.add(
                                    Note(
                                        eleve_id=item["eleve_id"],
                                        matiere_id=matiere_id_selectionnee,
                                        note_classe=item["nc"],
                                        note_compo=item["nco"],
                                        semestre=semestre,
                                    )
                                )
                        db.commit()
                        st.success("✅ Notes enregistrées avec succès !")

    finally:
        db.close()