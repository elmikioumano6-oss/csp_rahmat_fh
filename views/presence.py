from datetime import datetime
import pandas as pd
from database.db_config import SessionLocal
from database.models import Affectation, Classe, Eleve, Enseignant, LogActivite, Presence, User
import streamlit as st


def afficher_presence(prof_id=None):
    db_temp = SessionLocal()
    try:
        # Récupération automatique du prof_id depuis la session si non fourni
        if not prof_id and st.session_state.get("user_role") == "prof":
            username = st.session_state.get("username")
            user = db_temp.query(User).filter(User.username == username).first()
            if user:
                ens = (
                    db_temp.query(Enseignant)
                    .filter(Enseignant.user_id == user.id)
                    .first()
                )
                if ens:
                    prof_id = ens.id
    finally:
        db_temp.close()

    role_actuel = st.session_state.get("user_role", "Admin")

    if role_actuel == "prof":
        st.subheader("✅ Gestion des Présences (Espace Professeur)")
    else:
        st.subheader("✅ Gestion des Présences")

    db = SessionLocal()
    try:
        # --- FILTRAGE DES CLASSES SELON LE RÔLE ---
        classes = []
        if prof_id:
            affectations_prof = (
                db.query(Affectation)
                .filter(Affectation.enseignant_id == prof_id)
                .all()
            )
            classes_dict = {
                aff.classe.id: aff.classe for aff in affectations_prof if aff.classe
            }
            classes = list(classes_dict.values())
        else:
            classes = db.query(Classe).all()

        # --- FORMULAIRE DE SAISIE DE PRÉSENCE ---
        with st.form("form_presence"):
            st.write("### Enregistrer une présence/absence")

            if not classes:
                st.warning(
                    "⚠️ Aucune classe ne vous est assignée."
                    if prof_id
                    else "⚠️ Aucune classe enregistrée."
                )
                return

            options_classes = {c.nom: c.id for c in classes}
            classe_nom = st.selectbox("Classe", list(options_classes.keys()))
            classe_id = options_classes[classe_nom]

            eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
            if eleves:
                options_eleves = {
                    f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in eleves
                }
                eleve_label = st.selectbox("Élève", list(options_eleves.keys()))
                eleve_id = options_eleves[eleve_label]

                date_presence = st.date_input("Date", value=datetime.today())
                statut = st.selectbox("Statut", ["Présent", "Absent", "Retard"])

                submitted = st.form_submit_button("Enregistrer la présence")
                if submitted:
                    date_str = date_presence.strftime("%Y-%m-%d")
                    existe = (
                        db.query(Presence)
                        .filter(
                            Presence.eleve_id == eleve_id,
                            Presence.date == date_str,
                        )
                        .first()
                    )

                    if existe:
                        existe.statut = statut
                        action_str = "MODIFICATION PRÉSENCE"
                    else:
                        nouvelle_pres = Presence(
                            eleve_id=eleve_id, date=date_str, statut=statut
                        )
                        db.add(nouvelle_pres)
                        action_str = "SAISIE PRÉSENCE"

                    db.add(
                        LogActivite(
                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            utilisateur=st.session_state.get(
                                "user_role", "Admin"
                            ),
                            action=action_str,
                            details=f"Élève ID {eleve_id} le {date_str} : {statut}",
                        )
                    )

                    db.commit()
                    st.success(f"✅ Présence enregistrée ({statut}) !")
                    st.rerun()
            else:
                st.info("Aucun élève dans cette classe.")

        st.markdown("---")

        if prof_id:
            classe_ids = [c.id for c in classes]
            presences_autorisees = (
                db.query(Presence)
                .join(Eleve)
                .filter(Eleve.classe_id.in_(classe_ids))
                .order_by(Presence.date.desc())
                .all()
            )
        else:
            presences_autorisees = (
                db.query(Presence).order_by(Presence.date.desc()).all()
            )

        with st.expander("🛠️ Supprimer ou corriger une présence erronée"):
            if presences_autorisees:
                options_p = {
                    f"{p.date} | {p.eleve.nom} {p.eleve.prenom} | {p.statut}": p.id
                    for p in presences_autorisees
                }
                choix_p = st.selectbox(
                    "Sélectionner l'entrée à supprimer", list(options_p.keys())
                )

                if st.button(
                    "🗑️ Supprimer définitivement cette présence", type="primary"
                ):
                    p_id = options_p[choix_p]
                    p_obj = (
                        db.query(Presence).filter(Presence.id == p_id).first()
                    )
                    if p_obj:
                        db.add(
                            LogActivite(
                                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                utilisateur=st.session_state.get(
                                    "user_role", "Admin"
                                ),
                                action="SUPPRESSION PRÉSENCE",
                                details=f"Suppression présence ID {p_obj.id} ({p_obj.eleve.nom} - {p_obj.date})",
                            )
                        )
                        db.delete(p_obj)
                        db.commit()
                        st.success(
                            "✅ Entrée supprimée et action tracée avec succès !"
                        )
                        st.rerun()
            else:
                st.info("Aucune présence enregistrée à corriger pour vos classes.")

        st.markdown("---")

        st.write("### 📋 Historique des présences")
        if presences_autorisees:
            data = [
                {
                    "Date": p.date,
                    "Élève": f"{p.eleve.nom} {p.eleve.prenom}",
                    "Classe": p.eleve.classe.nom if p.eleve.classe else "N/A",
                    "Statut": p.statut,
                }
                for p in presences_autorisees
            ]
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("Aucune présence enregistrée pour l'instant.")
    finally:
        db.close()