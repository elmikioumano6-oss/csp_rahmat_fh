import streamlit as st
import base64
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="CSP RAHMAT-FH - Gestion d'Élèves",
    page_icon="Logo CSP-RAHMAT-FH.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour encoder le logo en base64 pour les balises PWA mobiles
def get_favicon_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

logo_base64 = get_favicon_base64("Logo CSP-RAHMAT-FH.png")

# --- INJECTION DES BALISES POUR L'ÉCRAN D'ACCUEIL MOBILE (PWA) ---
if logo_base64:
    st.markdown(f"""
        <head>
            <link rel="apple-touch-icon" href="data:image/png;base64,{logo_base64}">
            <link rel="shortcut icon" href="data:image/png;base64,{logo_base64}">
            <meta name="apple-mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
            <meta name="apple-mobile-web-app-title" content="CSP RAHMAT-FH">
        </head>
    """, unsafe_allow_html=True)

# --- IMPORTATION DES VUES ET DE LA DB ---
from database.db_config import engine
from database.models import Base
from views.login import afficher_login

# Initialisation sécurisée des tables pour éviter les plantages de connexion
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    st.warning("⚠️ Connexion à la base de données en cours de rétablissement...")

# --- GESTION DE LA SESSION ET DES PARAMÈTRES URL ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

query_params = st.query_params
if query_params.get("logged_in") == "true":
    st.session_state["authenticated"] = True

# --- ROUTAGE PRINCIPAL ---
if not st.session_state["authenticated"]:
    afficher_login()
else:
    role = st.session_state.get("user_role", "admin")
    
    with st.sidebar:
        if os.path.exists("Logo CSP-RAHMAT-FH.png"):
            st.image("Logo CSP-RAHMAT-FH.png", width=80)
        st.markdown(f"### CSP RAHMAT-FH")
        st.markdown(f"**Session :** `{st.session_state.get('username', 'Utilisateur').upper()}`")
        st.markdown(f"**Rôle :** `{role.upper()}`")
        
        st.divider()
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    st.markdown(f"""
        <div style="background: #1E293B; padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
            <h2>🏫 COMPLEXE SCOLAIRE PRIVÉ RAHMAT-FH</h2>
            <p>Plateforme de Gestion Administrative & Académique</p>
        </div>
    """, unsafe_allow_html=True)

    if role == "parent":
        try:
            from views.parent_space import afficher_espace_parent
            afficher_espace_parent()
        except ImportError:
            st.warning("Module Espace Parent en cours de chargement...")
    else:
        st.info(f"Bienvenue sur votre tableau de bord. Sélectionnez un module dans le menu de navigation.")