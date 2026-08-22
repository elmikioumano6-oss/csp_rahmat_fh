import streamlit as st
from database.db_config import SessionLocal
from database.models import User
import bcrypt

def afficher_login():
    # Design CSS personnalisé : Rouge bordeaux, bleu marine et champs compacts
    st.markdown("""
        <style>
            /* Masquer les éléments superflus de Streamlit */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Fond immersif mélangeant Bleu Marine et touches de Bordeaux */
            .stApp {
                background: linear-gradient(135deg, #0B132B 0%, #1C2541 50%, #581C25 100%);
            }
            
            /* Carte de connexion centrale sophistiquée */
            .auth-card {
                background: rgba(15, 23, 42, 0.85);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(220, 38, 38, 0.2);
                padding: 2.5rem 2rem;
                border-radius: 20px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            }
            
            /* Titres */
            .auth-title {
                color: #F8FAFC;
                font-weight: 800;
                font-size: 1.5rem;
                text-align: center;
                margin-top: 0.5rem;
                letter-spacing: -0.5px;
            }
            .auth-subtitle {
                color: #EF4444;
                font-size: 0.8rem;
                text-align: center;
                margin-bottom: 1.8rem;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-weight: 700;
            }
            
            /* Réduction de la hauteur et style des champs de saisie */
            .stTextInput input {
                background-color: #1E293B !important;
                color: #FFFFFF !important;
                border: 1px solid #334155 !important;
                border-radius: 8px !important;
                padding: 8px 12px !important;
                font-size: 0.9rem !important;
            }
            .stTextInput input:focus {
                border-color: #DC2626 !important;
                box-shadow: 0 0 0 1px #DC2626 !important;
            }
            
            /* Étiquettes des champs */
            label {
                color: #CBD5E1 !important;
                font-weight: 500 !important;
                font-size: 0.85rem !important;
            }
            
            /* Bouton de connexion bordeaux stylisé */
            .stButton button {
                background: linear-gradient(135deg, #991B1B 0%, #7F1D1D 100%) !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
                border-radius: 8px !important;
                border: none !important;
                padding: 0.5rem 1rem !important;
                transition: all 0.3s ease;
            }
            .stButton button:hover {
                background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%) !important;
                box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
            }
        </style>
    """, unsafe_allow_html=True)

    # Espacement vertical pour centrer la carte
    st.markdown("<div style='height: 6vh;'></div>", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 1.15, 1])

    with col_center:
        st.markdown("""
            <div class="auth-card">
                <div style="text-align: center;">
                    <span style="background: rgba(220, 38, 38, 0.15); border: 1px solid rgba(220, 38, 38, 0.3); padding: 10px; border-radius: 50%; font-size: 1.6rem; display: inline-block;">🏫</span>
                </div>
                <div class="auth-title">CSP RAHMAT-FH</div>
                <div class="auth-subtitle">Portail d'Administration</div>
        """, unsafe_allow_html=True)

        with st.form("form_login_bordeaux"):
            username = st.text_input(
                "Nom d'utilisateur", 
                placeholder="Votre identifiant..."
            )
            password = st.text_input(
                "Mot de passe", 
                type="password", 
                placeholder="••••••••"
            )
            
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
        
        st.markdown("""
            <div style="text-align: center; margin-top: 1.5rem;">
                <p style="color: #64748B; font-size: 0.75rem; font-weight: 500;">
                    Sécurité Renforcée • RAHMAT-FH
                </p>
            </div>
        """, unsafe_allow_html=True)