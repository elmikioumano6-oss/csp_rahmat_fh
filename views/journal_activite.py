import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import LogActivite

def afficher_journal_activite(niveau_actif=None):
    st.subheader("📜 Journal d'Activité et Traçabilité")
    st.markdown("Historique complet des actions et des événements de sécurité sur la plateforme.")
    
    db = SessionLocal()
    logs = db.query(LogActivite).order_by(LogActivite.id.desc()).all()
    
    if not logs:
        st.info("Aucune activité enregistrée pour le moment. Les actions effectuées dans l'application s'afficheront ici.")
        db.close()
        return

    data = []
    for l in logs:
        data.append({
            "Date / Heure": l.date,
            "Utilisateur": l.utilisateur or "Admin",
            "Action": l.action,
            "Détails": l.details or "N/A"
        })
    
    df = pd.DataFrame(data)

    # Filtres interactifs pour affiner l'audit
    col1, col2 = st.columns(2)
    with col1:
        recherche_utilisateur = st.text_input("🔍 Filtrer par utilisateur")
    with col2:
        recherche_action = st.text_input("🔍 Filtrer par type d'action")

    if recherche_utilisateur:
        df = df[df["Utilisateur"].str.contains(recherche_utilisateur, case=False, na=False)]
    if recherche_action:
        df = df[df["Action"].str.contains(recherche_action, case=False, na=False)]

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    if st.button("🗑️ Vider tout le journal", type="secondary"):
        try:
            db.query(LogActivite).delete()
            db.commit()
            st.success("Le journal d'activité a été vidé avec succès.")
            st.rerun()
        except Exception as e:
            st.error(f"Erreur lors de la suppression : {e}")

    db.close()