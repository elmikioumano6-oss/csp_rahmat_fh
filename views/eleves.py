from datetime import datetime
from database.db_config import SessionLocal
from database.models import Classe, Eleve, LogActivite, User
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def charger_donnees_eleves_cache(niveau_actif):
    db = SessionLocal()
    try:
        parents = (
            db.query(User.id, User.username)
            .filter(User.role == "parent")
            .all()
        )
        classes = (
            db.query(Classe.id, Classe.nom, Classe.cycle)
            .filter(Classe.cycle == niveau_actif)
            .all()
        )

        eleves_query = (
            db.query(Eleve)
            .join(Classe)
            .filter(Classe.cycle == niveau_actif)
            .order_by(Eleve.nom)
            .all()
        )
        eleves_data = [
            {
                "id": e.id,
                "matricule": e.matricule,
                "nom": e.nom,
                "prenom": e.prenom,
                "sexe": e.sexe,
                "telephone": e.telephone,
                "classe_id": e.classe_id,
                # Formatage unique pour éviter toute confusion entre classes homonymes
                "classe_nom": (
                    f"{e.classe.nom} ({e.classe.cycle}) [ID:{e.classe.id}]"
                    if e.classe
                    else "N/A"
                ),
                "parent_id": e.parent_id,
                "parent_nom": e.parent.username if e.parent else "Aucun",
            }
            for e in eleves_query
        ]

        return {
            "parents": {p.username: p.id for p in parents},
            # Classes avec clé unique Nom (Cycle) [ID: X]
            "classes": {
                f"{c.nom} ({c.cycle}) [ID:{c.id}]": c.id for c in classes
            },
            "eleves": eleves_data,
        }
    finally:
        db.close()


def afficher_eleves(niveau_actif=None):
    st.subheader(f"👥 Inscription et Gestion des Élèves - {niveau_actif}")

    db = SessionLocal()

    # Chargement rapide via le cache
    donnees_cache = charger_donnees_eleves_cache(niveau_actif)
    parent_options = donnees_cache["parents"]
    options_classes = donnees_cache["classes"]

    # --- FORMULAIRE D'INSCRIPTION ---
    with st.form("form_inscription_eleve"):
        st.write("### Inscrire un nouvel élève")

        if not options_classes:
            st.warning(
                f"⚠️ Veuillez d'abord créer des classes pour le cycle {niveau_actif}."
            )
            db.close()
            return

        classe_nom = st.selectbox("Classe", list(options_classes.keys()))
        classe_id = options_classes[classe_nom]

        col1, col2 = st.columns(2)
        with col1:
            matricule = st.text_input("Matricule unique")
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")

        with col2:
            sexe = st.selectbox("Sexe", ["Garçon", "Fille"])
            telephone = st.text_input("Téléphone (Contact)")
            montant_reduction = st.number_input(
                "Montant de réduction (FCFA)", min_value=0.0, step=1000.0
            )

            parent_select = st.selectbox(
                "Assigner un compte parent (Optionnel)",
                ["Aucun"] + list(parent_options.keys()),
            )

        submitted = st.form_submit_button("Inscrire l'élève")
        if submitted:
            if matricule.strip() and nom.strip() and prenom.strip():
                existe = (
                    db.query(Eleve)
                    .filter(Eleve.matricule == matricule)
                    .first()
                )
                if existe:
                    st.error(
                        "❌ Ce matricule existe déjà dans la base de données."
                    )
                else:
                    parent_id = parent_options.get(parent_select)

                    nouvel_eleve = Eleve(
                        matricule=matricule,
                        nom=nom,
                        prenom=prenom,
                        sexe=sexe,
                        telephone=telephone,
                        montant_reduction=montant_reduction,
                        classe_id=classe_id,
                        parent_id=parent_id,
                    )
                    db.add(nouvel_eleve)

                    db.add(
                        LogActivite(
                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            utilisateur=st.session_state.get(
                                "user_role", "Admin"
                            ),
                            action="INSCRIPTION ÉLÈVE",
                            details=f"Inscription de {nom} {prenom} (Matricule: {matricule}). Parent lié: {parent_select}",
                        )
                    )

                    db.commit()
                    st.cache_data.clear()  # Vider le cache après l'écriture
                    st.success(f"✅ Élève {nom} {prenom} inscrit avec succès !")
                    st.rerun()
            else:
                st.warning(
                    "⚠️ Veuillez remplir le matricule, le nom et le prénom."
                )

    st.markdown("---")

    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger un élève"):
        eleves_cycle = donnees_cache["eleves"]
        if eleves_cycle:
            options_e = {
                f"Matricule: {e['matricule']} - {e['nom']} {e['prenom']}": e[
                    "id"
                ]
                for e in eleves_cycle
            }
            choix_e = st.selectbox(
                "Sélectionner l'élève", list(options_e.keys())
            )

            if st.button(
                "🗑️ Supprimer définitivement cet élève", type="primary"
            ):
                e_id = options_e[choix_e]
                e_obj = db.query(Eleve).filter(Eleve.id == e_id).first()
                if e_obj:
                    nom_complet = (
                        f"{e_obj.nom} {e_obj.prenom} ({e_obj.matricule})"
                    )
                    db.delete(e_obj)
                    db.commit()
                    st.cache_data.clear()  # Vider le cache après suppression
                    st.success(f"✅ L'élève {nom_complet} a été supprimé.")
                    st.rerun()
        else:
            st.info("Aucun élève enregistré pour ce cycle.")

    st.markdown("---")

    # --- LISTE DES ÉLÈVES (Via le cache) ---
    st.write(f"### 📋 Liste des élèves inscrits - {niveau_actif}")
    tous_eleves = donnees_cache["eleves"]
    if tous_eleves:
        data = [
            {
                "Matricule": e["matricule"],
                "Nom": e["nom"],
                "Prénom": e["prenom"],
                "Classe": e["classe_nom"],
                "Parent lié": e["parent_nom"],
            }
            for e in tous_eleves
        ]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun élève inscrit pour le moment.")

    db.close()