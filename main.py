import streamlit as st
import pandas as pd
from sqlalchemy import text
from streamlit_option_menu import option_menu
from database.db_config import engine, SessionLocal
from database.models import Base, AnneeScolaire, Classe, Eleve, EcheancePaiement, User
from views.login import afficher_login

# Configuration de la page
st.set_page_config(
    page_title="CSP RAHMAT-FH - Gestion Scolaire",
    page_icon="Logo CSP-RAHMAT-FH.png",
    layout="wide"
)

# ==========================================
# PERSONNALISATION AVANCÉE (CSS CORRIGÉ)
# ==========================================
st.markdown("""
    <style>
    /* Fond global */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #581822 100%);
        color: #FFFFFF !important;
    }
    
    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background-color: #0b1329;
        border-right: 1px solid #800020;
    }

    /* Textes et titres (Suppression du 'div' global pour éviter les conflits) */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
    }

    /* Correction ciblée : Rendre le texte des menus déroulants noir sur fond blanc */
    div[data-baseweb="select"] div, div[data-baseweb="select"] span {
        color: #000000 !important;
    }

    /* Alertes */
    div.stAlert {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #FFFFFF !important;
        border: 1px solid #800020;
    }

    /* Scrollbar visible */
    ::-webkit-scrollbar { width: 16px; height: 16px; }
    ::-webkit-scrollbar-track { background: #0b1329; }
    ::-webkit-scrollbar-thumb { background: #ffffff; border-radius: 8px; border: 3px solid #0b1329; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. INITIALISATION ET MIGRATIONS
# ==========================================
Base.metadata.create_all(bind=engine)

with engine.connect() as connection:
    try:
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS entite_id INTEGER;"))
        connection.execute(text("ALTER TABLE notes ADD COLUMN IF NOT EXISTS semestre INTEGER DEFAULT 1;"))
        connection.execute(text("ALTER TABLE classes ADD COLUMN IF NOT EXISTS cycle TEXT;"))
        connection.execute(text("ALTER TABLE classes ADD COLUMN IF NOT EXISTS tarif_scolarite FLOAT DEFAULT 0.0;"))
        connection.execute(text("ALTER TABLE enseignants ADD COLUMN IF NOT EXISTS specialite TEXT;"))
        connection.execute(text("ALTER TABLE eleves ADD COLUMN IF NOT EXISTS telephone TEXT;"))
        connection.execute(text("ALTER TABLE eleves ADD COLUMN IF NOT EXISTS montant_reduction FLOAT DEFAULT 0.0;"))
        connection.execute(text("ALTER TABLE eleves ADD COLUMN IF NOT EXISTS photo TEXT;"))
        connection.execute(text("ALTER TABLE programmes ADD COLUMN IF NOT EXISTS document_pdf TEXT;"))
        connection.commit()
    except Exception: pass

# ==========================================
# 2. INITIALISATION COMPTES
# ==========================================
def verifier_et_creer_comptes_par_defaut():
    db = SessionLocal()
    try:
        User.__table__.create(bind=engine, checkfirst=True)
        comptes = [
            {"username": "admin", "password": "Rahmatfh2026", "role": "admin", "entite_id": None},
            {"username": "prof", "password": "prof2026", "role": "prof", "entite_id": 1},
            {"username": "parent", "password": "parent2026", "role": "parent", "entite_id": 1}
        ]
        for data in comptes:
            user = db.query(User).filter(User.username == data["username"]).first()
            if not user:
                db.add(User(**data))
        db.commit()
    finally:
        db.close()

verifier_et_creer_comptes_par_defaut()

# ==========================================
# 3. SÉCURITÉ ET VUES
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state.update({'authenticated': False, 'user_role': 'admin', 'username': 'Admin'})

if not st.session_state['authenticated']:
    afficher_login()
    st.stop()

# Import des vues
from views.classes import afficher_classes
from views.eleves import afficher_eleves
from views.finances import afficher_finances
from views.enseignants import afficher_enseignants
from views.personnels_roles import afficher_personnels
from views.notes import afficher_notes
from views.gestion_utilisateurs import afficher_gestion_utilisateurs
from views.parent_space import afficher_espace_parent
from views.matieres import afficher_matieres
# ... (Gardez vos autres imports)

def main():
    db = SessionLocal()
    role = st.session_state.get('user_role', 'admin')
    username = st.session_state.get('username', 'Utilisateur')

    with st.sidebar:
        st.markdown("### 🏫 CSP RAHMAT-FH")
        st.success(f"Bienvenue, **{username}**")
        
        if role == 'admin':
            page = option_menu("NAVIGATION", ["Classes & Tarifs", "Enseignants", "Gestion Comptes", "Inscription Élèves", "Saisie de notes"], menu_icon="cast", default_index=0)
        elif role == 'parent':
            page = option_menu("ESPACE PARENT", ["Mon Enfant"], menu_icon="shield-lock")
        else:
            page = option_menu("ESPACE PROF", ["Saisie de notes"], menu_icon="book-half")

        if st.button("🚪 Déconnexion"):
            st.session_state.update({'authenticated': False})
            st.rerun()

    # Routeur
    if role == 'admin':
        if page == "Gestion Comptes": afficher_gestion_utilisateurs()
        elif page == "Classes & Tarifs": afficher_classes()
        # ... (Le reste de votre logique de navigation)
    elif role == 'parent':
        afficher_espace_parent()

    db.close()

if __name__ == "__main__":
    main()
