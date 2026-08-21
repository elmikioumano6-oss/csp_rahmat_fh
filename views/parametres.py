import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import AnneeScolaire

def afficher_parametres():
    st.subheader("⚙️ Paramètres du Système - Années Scolaires")
    db = SessionLocal()

    # --- AJOUTER UNE ANNÉE SCOLAIRE ---
    with st.form("form_ajout_annee", clear_on_submit=True):
        st.markdown("### Créer une nouvelle année scolaire")
        libelle = st.text_input("Libellé de l'année (ex: 2026-2027)")
        submit = st.form_submit_button("Enregistrer", type="primary")

        if submit:
            if libelle.strip():
                existe = db.query(AnneeScolaire).filter(AnneeScolaire.libelle == libelle.strip()).first()
                if existe:
                    st.error("Cette année scolaire existe déjà.")
                else:
                    nouvelle_annee = AnneeScolaire(libelle=libelle.strip(), active=False)
                    db.add(nouvelle_annee)
                    db.commit()
                    st.success(f"Année {libelle} créée avec succès !")
                    st.rerun()
            else:
                st.error("Veuillez saisir un libellé.")

    st.markdown("---")

    # --- GESTION DES ANNÉES (ACTIVER / SUPPRIMER) ---
    st.markdown("### Liste des années scolaires")
    annees = db.query(AnneeScolaire).all()

    if annees:
        donnees = []
        for a in annees:
            donnees.append({
                "ID": a.id,
                "Année Scolaire": a.libelle,
                "Statut": "✅ ACTIVE" if a.active else "Inactif"
            })
        
        st.dataframe(pd.DataFrame(donnees), use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        
        # Activer une année (désactive automatiquement les autres)
        with col1:
            with st.expander("✅ Définir l'année active"):
                options_an = {a.libelle: a for a in annees}
                choix_active = st.selectbox("Sélectionnez l'année en cours :", options_an.keys())
                
                if st.button("Activer cette année"):
                    # Désactiver toutes les années d'abord
                    for annee in annees:
                        annee.active = False
                    # Activer celle choisie
                    annee_a_activer = options_an[choix_active]
                    annee_a_activer.active = True
                    db.commit()
                    st.success(f"L'année {choix_active} est maintenant active !")
                    st.rerun()

        # Supprimer une année
        with col2:
            with st.expander("🗑️ Supprimer une année"):
                choix_suppr = st.selectbox("Sélectionnez l'année à supprimer :", options_an.keys(), key="suppr_an")
                if st.button("Supprimer", type="primary"):
                    annee_a_suppr = options_an[choix_suppr]
                    if annee_a_suppr.active:
                        st.error("Impossible de supprimer l'année active. Activez-en une autre d'abord.")
                    else:
                        db.delete(annee_a_suppr)
                        db.commit()
                        st.success("Année supprimée !")
                        st.rerun()
    else:
        st.info("Aucune année scolaire n'est configurée.")

    db.close()