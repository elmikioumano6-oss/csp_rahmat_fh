from datetime import datetime
import pandas as pd
from database.db_config import SessionLocal
from database.models import (
    Classe,
    Eleve,
    Enseignant,
    LogActivite,
    Matiere,
    Note,
    Affectation, # NOUVEAU : Import de la table d'affectation
)
import streamlit as st


def afficher_notes(niveau_actif=None, prof_id=None):
    # Récupération automatique du prof_id depuis la session si non fourni
    if not prof_id and st.session_state.get("user_role") == "prof":
        # Note: assurez-vous que user_entity_id contient bien l'ID de l'enseignant
        # ou cherchez-le via le compte User comme vu précédemment.
        db_temp = SessionLocal()
        username = st.session_state.get("username")
        from database.models import User
        user = db_temp.query(User).filter(User.username == username).first()
        if user:
            ens = db_temp.query(Enseignant).filter(Enseignant.user_id == user.id).first()
            if ens:
                prof_id = ens.id
        db_temp.close()

    role_actuel = st.session_state.get("user_role", "Admin")

    if role_actuel == "prof":
        st.subheader(
            f"📝 Saisie et Gestion des Notes (Espace Professeur) - {niveau_actif}"
        )
    else:
        st.subheader(f"📝 Saisie et Gestion des Notes - {niveau_actif}")

    db = SessionLocal()

    # --- FILTRAGE DES CLASSES ET MATIÈRES SELON LE RÔLE ---
    classes = []
    affectations_prof = []

    if prof_id:
        enseignant = db.query(Enseignant).filter(Enseignant.id == prof_id).first()
        if enseignant:
            # Récupération de TOUTES les affectations de ce prof
            affectations_prof = db.query(Affectation).filter(Affectation.enseignant_id == prof_id).all()
            
            # On filtre les affectations pour ne garder que celles du cycle actif (ex: Collège)
            affectations_cycle = [aff for aff in affectations_prof if aff.classe and aff.classe.cycle == niveau_actif]
            
            # Extraction des classes uniques à partir des affectations
            classes_dict = {aff.classe.id: aff.classe for aff in affectations_cycle}
            classes = list(classes_dict.values())
    else:
        # Administrateur : accès à toutes les classes du cycle
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()

    # --- FORMULAIRE DE SAISIE DE NOTES ---
    with st.form("form_saisie_notes"):
        st.write("### Saisir ou modifier une note")

        if not classes:
            st.warning(
                f"⚠️ Aucune classe ne vous est assignée pour le cycle {niveau_actif}."
                if prof_id
                else f"⚠️ Aucune classe trouvée pour le cycle {niveau_actif}."
            )
            db.close()
            return

        options_classes = {c.nom: c.id for c in classes}
        classe_nom = st.selectbox(
            "Sélectionner la classe", list(options_classes.keys())
        )
        classe_id = options_classes[classe_nom]

        # 2. Sélectionner l'élève de cette classe
        eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
        if not eleves:
            st.warning("⚠️ Aucun élève inscrit dans cette classe.")
            db.close()
            return

        options_eleves = {
            f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in eleves
        }
        eleve_label = st.selectbox(
            "Sélectionner l'élève", list(options_eleves.keys())
        )
        eleve_id = options_eleves[eleve_label]

        # 3. Sélectionner la matière (Filtrée dynamiquement pour le prof)
        matieres_disponibles = []
        if prof_id:
            # Le prof ne voit QUE les matières qu'il enseigne DANS CETTE classe spécifique
            matieres_pour_classe = [aff.matiere for aff in affectations_prof if aff.classe_id == classe_id]
            matieres_dict = {m.id: m for m in matieres_pour_classe if m}
            matieres_disponibles = list(matieres_dict.values())
        else:
            # L'admin voit toutes les matières
            matieres_disponibles = db.query(Matiere).all()

        if not matieres_disponibles:
            st.warning(
                "⚠️ Aucune matière ne vous est assignée pour cette classe."
                if prof_id
                else "⚠️ Aucune matière enregistrée dans le système."
            )
            db.close()
            return

        options_matieres = {m.nom: m.id for m in matieres_disponibles}
        matiere_nom = st.selectbox(
            "Sélectionner la matière", list(options_matieres.keys())
        )
        matiere_id = options_matieres[matiere_nom]

        # 4. Semestre et notes
        semestre = st.selectbox("Semestre", [1, 2])
        col1, col2 = st.columns(2)
        note_classe = col1.number_input(
            "Note de Classe / Interro (sur 20)",
            min_value=0.0,
            max_value=20.0,
            step=0.25,
        )
        note_compo = col2.number_input(
            "Note de Composition (sur 20)",
            min_value=0.0,
            max_value=20.0,
            step=0.25,
        )

        submitted = st.form_submit_button("Enregistrer la note")
        if submitted:
            # Vérifier si une note existe déjà pour cet élève, cette matière et ce semestre
            note_existante = (
                db.query(Note)
                .filter(
                    Note.eleve_id == eleve_id,
                    Note.matiere_id == matiere_id,
                    Note.semestre == semestre,
                )
                .first()
            )

            if note_existante:
                note_existante.note_classe = note_classe
                note_existante.note_compo = note_compo
                action_str = "MODIFICATION NOTE"
                details_str = f"Mise à jour note élève ID {eleve_id}, matière ID {matiere_id} (Semestre {semestre})"
            else:
                nouvelle_note = Note(
                    eleve_id=eleve_id,
                    matiere_id=matiere_id,
                    note_classe=note_classe,
                    note_compo=note_compo,
                    semestre=semestre,
                )
                db.add(nouvelle_note)
                action_str = "SAISIE NOTE"
                details_str = f"Ajout note élève ID {eleve_id}, matière ID {matiere_id} (Semestre {semestre})"

            # Traçabilité dans le journal d'activité
            db.add(
                LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get("user_role", "Admin"),
                    action=action_str,
                    details=details_str,
                )
            )

            db.commit()
            st.success("✅ Note enregistrée et tracée avec succès !")
            st.rerun()

    st.markdown("---")

    # --- ESPACE DE CORRECTION / MODIFICATION / SUPPRESSION DES NOTES ---
    with st.expander("🛠️ Modifier ou supprimer une note enregistrée"):
        if prof_id:
            # Le prof ne peut modifier que les notes des classes et matières qui lui sont assignées
            classe_ids = [c.id for c in classes]
            matiere_ids = [m.id for aff in affectations_prof if (m:=aff.matiere)]
            notes_cycle = (
                db.query(Note)
                .join(Eleve)
                .join(Classe)
                .filter(
                    Classe.cycle == niveau_actif,
                    Eleve.classe_id.in_(classe_ids),
                    Note.matiere_id.in_(matiere_ids),
                )
                .order_by(Note.id.desc())
                .all()
            )
        else:
            # L'admin peut tout modifier
            notes_cycle = (
                db.query(Note)
                .join(Eleve)
                .join(Classe)
                .filter(Classe.cycle == niveau_actif)
                .order_by(Note.id.desc())
                .all()
            )

        if notes_cycle:
            options_n = {
                f"Note ID {n.id} - {n.eleve.nom} {n.eleve.prenom} (Semestre {n.semestre}) | Classe: {n.note_classe} | Compo: {n.note_compo}": n.id
                for n in notes_cycle
            }
            choix_n = st.selectbox(
                "Sélectionner la note",
                list(options_n.keys()),
                key="select_note_modif",
            )
            n_id = options_n[choix_n]
            n_obj = db.query(Note).filter(Note.id == n_id).first()

            if n_obj:
                action_type = st.radio(
                    "Action à effectuer",
                    ["Modifier", "Supprimer"],
                    horizontal=True,
                    key="radio_action_note",
                )

                if action_type == "Modifier":
                    with st.form("form_modif_note"):
                        c_m1, c_m2 = st.columns(2)
                        nouveau_classe = c_m1.number_input(
                            "Note de Classe / Interro (sur 20)",
                            min_value=0.0,
                            max_value=20.0,
                            step=0.25,
                            value=float(n_obj.note_classe or 0.0),
                        )
                        nouveau_compo = c_m2.number_input(
                            "Note de Composition (sur 20)",
                            min_value=0.0,
                            max_value=20.0,
                            step=0.25,
                            value=float(n_obj.note_compo or 0.0),
                        )

                        submit_modif_note = st.form_submit_button(
                            "💾 Mettre à jour la note"
                        )
                        if submit_modif_note:
                            n_obj.note_classe = nouveau_classe
                            n_obj.note_compo = nouveau_compo

                            db.add(
                                LogActivite(
                                    date=datetime.now().strftime(
                                        "%Y-%m-%d %H:%M"
                                    ),
                                    utilisateur=st.session_state.get(
                                        "user_role", "Admin"
                                    ),
                                    action="MODIFICATION NOTE",
                                    details=f"Mise à jour directe de la note ID {n_obj.id} (Classe: {nouveau_classe}, Compo: {nouveau_compo})",
                                )
                            )
                            db.commit()
                            st.success("✅ Note mise à jour avec succès !")
                            st.rerun()
                else:
                    if st.button(
                        "🗑️ Supprimer définitivement cette note",
                        type="primary",
                        key="btn_suppr_note",
                    ):
                        db.add(
                            LogActivite(
                                date=datetime.now().strftime(
                                    "%Y-%m-%d %H:%M"
                                ),
                                utilisateur=st.session_state.get(
                                    "user_role", "Admin"
                                ),
                                action="SUPPRESSION NOTE",
                                details=f"Suppression de la note ID {n_obj.id} (Élève ID {n_obj.eleve_id}, Semestre {n_obj.semestre})",
                            )
                        )
                        db.delete(n_obj)
                        db.commit()
                        st.success(
                            "✅ Note supprimée et action tracée avec succès !"
                        )
                        st.rerun()
        else:
            st.info("Aucune note enregistrée pour ce cycle à modifier ou supprimer.")

    db.close()