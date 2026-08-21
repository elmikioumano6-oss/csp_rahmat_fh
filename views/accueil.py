import base64
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Classe, Eleve, Enseignant, LogActivite, User
import os
import pandas as pd
import streamlit as st


def afficher_accueil():
    # Chargement sécurisé et conversion du logo en base64
    logo_filename = "Logo CSP-RAHMAT-FH.png"
    logo_src = ""
    if os.path.exists(logo_filename):
        with open(logo_filename, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            logo_src = f"data:image/png;base64,{encoded}"

    logo_html = (
        f'<img src="{logo_src}" alt="Logo" style="width:75px; height:75px; object-fit:contain;">'
        if logo_src
        else '<div style="font-size: 24px; font-weight: bold; color: #1a365d;">CSP</div>'
    )

    # En-tête de bienvenue stylisé : bordure gauche bleu marine, bordure droite bordeaux, logo à droite
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 6px solid #1a365d; border-right: 6px solid #800020; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; align-items: center; justify-content: space-between; gap: 20px;">
            <div style="flex-grow: 1;">
                <h2 style="color: #1a365d; margin-top: 0; margin-bottom: 5px;">🏫 Complexe Scolaire Privé RAHMAT-FH</h2>
                <p style="font-size: 14px; color: #555; margin-bottom: 8px;"><b>Devise :</b> Excellence - Persévérance - Réussite</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 8px 0;">
                <p style="margin: 3px 0; font-size: 13px;"><b>📍 Adresse :</b> Quartier Aéroport, Niamey - Niger &nbsp;|&nbsp; <b>📞 Contacts :</b> 97327752 / 89522398 / 92532710</p>
            </div>
            <div>
                {logo_html}
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    db = SessionLocal()

    # --- 1. STATISTIQUES GLOBALES ---
    st.write("### 📊 Tableau de Bord Général")
    col1, col2, col3, col4 = st.columns(4)

    total_eleves = db.query(Eleve).count()
    total_enseignants = db.query(Enseignant).count()
    total_classes = db.query(Classe).count()
    total_utilisateurs = db.query(User).count()

    col1.metric("Total Élèves", total_eleves)
    col2.metric("Total Enseignants", total_enseignants)
    col3.metric("Classes Actives", total_classes)
    col4.metric("Comptes Utilisateurs", total_utilisateurs)

    st.markdown("---")

    # --- 2. UTILISATEURS ACTIFS / CONNECTÉS DU JOUR ---
    st.write("### 🟢 Utilisateurs Actifs / Connectés Récemment")
    
    date_jour = datetime.now().strftime("%Y-%m-%d")
    logs_recents = db.query(LogActivite).filter(LogActivite.date.like(f"{date_jour}%")).all()
    utilisateurs_actifs = list(set([l.utilisateur for l in logs_recents if l.utilisateur]))
    
    if utilisateurs_actifs:
        cols_actifs = st.columns(min(len(utilisateurs_actifs), 4))
        for idx, user in enumerate(utilisateurs_actifs):
            with cols_actifs[idx % 4]:
                st.markdown(
                    f"""
                    <div style="background: #e6f4ea; border: 1px solid #ceead6; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                        <span style="font-size: 1.1rem;">🟢</span><br>
                        <b style="color: #137333;">{user}</b><br>
                        <span style="font-size: 0.8rem; color: #5f6368;">Actif aujourd'hui</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Aucun utilisateur actif enregistré pour l'instant aujourd'hui.")

    st.markdown("---")

    # --- 3. LISTE DE TOUS LES UTILISATEURS DU SYSTÈME ---
    st.write("### 👥 Tous les Comptes Utilisateurs")
    utilisateurs = db.query(User).all()
    if utilisateurs:
        data_users = [
            {"ID": u.id, "Nom d'utilisateur": u.username, "Rôle": u.role}
            for u in utilisateurs
        ]
        st.dataframe(pd.DataFrame(data_users), use_container_width=True)
    else:
        st.info("Aucun utilisateur enregistré.")

    st.markdown("---")

    # --- 4. JOURNAL DES DERNIÈRES ACTIVITÉS ---
    st.write("### 📜 Activités Récentes du Système")
    logs = (
        db.query(LogActivite).order_by(LogActivite.id.desc()).limit(10).all()
    )
    if logs:
        data_logs = [
            {
                "Date": l.date,
                "Utilisateur": l.utilisateur,
                "Action": l.action,
                "Détails": l.details,
            }
            for l in logs
        ]
        st.dataframe(pd.DataFrame(data_logs), use_container_width=True)
    else:
        st.info("Aucune activité récente enregistrée.")

    db.close()