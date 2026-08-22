import streamlit as st
from database.db_config import SessionLocal
from database.models import User
import bcrypt
from PIL import Image
import os

def afficher_login():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            .stApp {
                background: linear-gradient(135deg, #0B132B 0%, #1C2541 50%, #581C25 100%);
            }
            
            /* Boîte de connexion étroite et centrée */
            .auth-card {
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(220, 38, 38, 0.3);
                padding: 2rem 1.5rem;
                border-radius: 20px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
                max-width: 380px;
                margin: 0 auto;
            }
            
            .auth-title {
                color: #F8FAFC;
                font-weight: 800;
                font-size: 1.35rem;
                text-align: center;
                margin-top: 0.2rem;
                letter-spacing: -0.5px;
            }
            .auth-subtitle {
                color: #EF4444;
                font-size: 0.75rem;
                text-align: center;
                margin-bottom: 1.2rem;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-weight: 700;
            }
            
            .stTextInput input {
                background-color: #1E293B !important;
                color: #FFFFFF !important;
                border: 1px solid #334155 !important;
                border-radius: 8px !important;
                padding: 7px 10px !important;
                font-size: 0.85rem !important;
            }
            .stTextInput input:focus {
                border-color: #EF4444 !important;
                box-shadow: 0 0 0 1px #EF4444 !important;
            }
            
            label {
                color: #EF4444 !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
            }
            
            .stButton button {
                background: linear-gradient(135deg, #991B1B 0%, #7F1D1D 100%) !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
                border-radius: 8px !important;
                border: none !important;
                padding: 0.45rem 1rem !important;
                transition: all 0.3s ease;
            }
            .stButton button:hover {
                background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%) !important;
                box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1.5, 1, 1.5])

    with col_center:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        
        # --- CENTRAGE STRICT DU LOGO AVEC DES COLONNES INTERNES ÉQUILIBRÉES ---
        c_left, c_mid, c_right = st.columns([1, 1.2, 1])
        with c_mid:
            try:
                logo_path = "Logo CSP-RAHMAT-FH.png"
                if os.path.exists(logo_path):
                    logo_img = Image.open(logo_path)
                    st.image(logo_img, width=75)
                else:
                    st.markdown("<div style='text-align: center; font-size: 2rem;'>🏫</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("<div style='text-align: center; font-size: 2rem;'>🏫</div>", unsafe_allow_html=True)

        st.markdown("""
                <div class="auth-title">CSP RAHMAT-FH</div>
                <div class="auth-subtitle">Portail d'Administration</div>
        """, unsafe_allow_html=True)

        with st.form("form_login_parfait"):
            username = st.text_input("Nom d'utilisateur", placeholder="Votre identifiant...")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            
            st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.username == username).first()
                    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user.username
                        st.session_state["user_role"] = user.role
                        st.session_state["user_entity_id"] = user.id
                        st.query_params["logged_in"] = "true"
                        st.success("✨ Accès autorisé. Redirection...")
                        st.rerun()
                    else:
                        st.error("⚠️ Identifiant ou mot de passe incorrect.")
                finally:
                    db.close()
                    
        st.markdown("</div>", unsafe_allow_html=True)