import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import LogActivite

def afficher_journal_activite(niveau_actif=None):
    st.subheader("📜 Journal d'Activité et Traçabilité")
    
    db = SessionLocal()
    logs = db.query(LogActivite).order_by(LogActivite.id.desc()).all()
    
    if logs:
        st.write("### 🕒 Historique des actions enregistrées")
        data = []
        for l in logs:
            data.append({
                "Date / Heure": l.date,
                "Utilisateur": l.utilisateur or "Admin",
                "Action": l.action,
                "Détails": l.details or "N/A"
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucune activité enregistrée pour le moment. Les actions effectuées dans l'application s'afficheront ici.")
        
    db.close()