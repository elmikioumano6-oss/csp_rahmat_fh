from datetime import datetime
import os
from PIL import Image
import bcrypt
from database.db_config import SessionLocal, engine
from database.models import AnneeScolaire, Base, User
from sqlalchemy import text
import streamlit as st
from streamlit_option_menu import option_menu
from views.login import afficher_login

# Initialisation
try:
    Base.metadata.create_all(bind=engine)
except: pass

# ==========================================
# GESTION DES RERUNS ET ÉTAT
# ==========================================
st.set_page_config(page_title="CSP RAHMAT-FH", layout="wide", initial_sidebar_state="expanded")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = "admin"

if st.query_params.get("logged_in") == "true":
    st.session_state["authenticated"] = True

if not st.session_state["authenticated"]:
    afficher_login()
    st.stop()

def main():
    db = SessionLocal()
    annee = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
    annee_libelle = annee.libelle if annee else "2026-2027"
    role = st.session_state.get("user_role", "admin")
    db.close()

    with st.sidebar:
        st.markdown(f"## 🏫 RAHMAT-FH\n### SESSION : {role.upper()}")
        st.markdown("---")

        if role == "admin":
            page = option_menu("NAVIGATION", 
                ["Accueil", "Année scolaire", "Classes & Tarifs", "Matières & Coeffs", "Enseignants", "Personnels et rôles", "Gestion Comptes", "Inscription Élèves", "Import Photos en Masse", "Cartes Scolaires", "Espace Profs", "Consultations des notes", "Conseil de classe", "Bulletins", "Supervision cahier", "Import Programmes PDF", "Suivi des Programmes", "Emploi du temps", "Planification des évaluations", "Encaissement", "Stats Encaissements", "Soldes & Impayés", "Tableau Finances", "Dépenses", "Rapports", "Journal d'activité", "Messages", "Espace Parent", "Tableau de bord", "Alerte Pédagogique", "Sauvegarde & BD"],
                icons=["house", "calendar-event", "building", "book", "person-badge", "shield-lock", "people-fill", "people", "folder-plus", "card-list", "book-half", "journal-text", "people-fill", "file-earmark-text", "eye", "file-earmark-pdf", "graph-up-arrow", "calendar3", "calendar-check", "cash-coin", "graph-up", "wallet2", "graph-up", "receipt", "file-bar-graph", "clock-history", "chat-dots", "person-badge", "speedometer", "exclamation-triangle", "hdd-stack"],
                key="main_menu")
        elif role == "prof":
            page = option_menu("ESPACE PROF", ["Saisie de notes", "Présence", "Cahier de texte"], icons=["pencil-square", "calendar-check", "journal-bookmark"], key="prof_menu")
        else:
            page = "Accueil"

        if st.button("🚪 Déconnexion"):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- ZONE D'AFFICHAGE ISOLÉE ---
    niveau_actif = st.selectbox("🎯 Cycle Actif :", ["Primaire", "Collège", "Lycée"], index=1)
    
    # Appel dynamique de la vue sans recharger toute la page
    placeholder = st.container()
    with placeholder:
        if role == "admin":
            if page == "Accueil":
                from views.accueil import afficher_accueil; afficher_accueil()
            elif page == "Année scolaire":
                from views.annee_scolaire import afficher_annee_scolaire; afficher_annee_scolaire()
            elif page == "Classes & Tarifs":
                from views.classes import afficher_classes; afficher_classes(niveau_actif)
            elif page == "Notes & Bulletins" or page == "Bulletins":
                from views.bulletins import afficher_bulletins; afficher_bulletins(niveau_actif)
            elif page == "Saisie de notes":
                from views.notes import afficher_notes; afficher_notes(niveau_actif)
            # ... (ajoutez les autres elif ici)
            elif page == "Tableau de bord":
                from views.tableau_de_bord import afficher_tableau_bord; afficher_tableau_bord(niveau_actif)

if __name__ == "__main__":
    main()