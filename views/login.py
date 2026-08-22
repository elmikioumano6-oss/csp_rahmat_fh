import streamlit as st
from database.db_config import SessionLocal
from database.models import User
import bcrypt

def afficher_login():
    # Design CSS ultra-moderne, professionnel et captivant
    st.markdown("""
        <style>
            /* Masquer les éléments superflus de Streamlit sur la page de login */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Fond de page immersif aux teintes académiques d'élite */
            .stApp {
                background: radial-gradient(circle at 50% 20%, #1E293B 0%, #0F172A 100%);
            }
            
            /* Carte de connexion élégante avec effet verre et ombre portée raffinée */
            .auth-card {
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 2.8rem 2.5rem;
                border-radius: 24px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }
            
            /* Typographie des titres */
            .auth-title {
                color: #FFFFFF;
                font-weight: 800;
                font-size: 1.5rem;
                text-align: center;
                margin-top: 0.5rem;
                letter-spacing: -0.5px;
            }
            .auth-subtitle {
                color: #94A3B8;
                font-size: 0.85rem;
                text-align: center;
                margin-bottom: 2rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
            }
            
            /* Personnalisation des étiquettes de formulaires */
            label {
                color: #E2E8F0 !important;
                font-weight: 500 !important;
                font-size: 0.9rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Espacement vertical pour un centrage parfait sur l'écran
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 1.3, 1])

    with col_center:
        st.markdown("""
            <div class="auth-card">
                <div style="text-align: center;">
                    <span style="background: rgba(217, 119, 6, 0.15); border: 1px solid rgba(217, 119, 6, 0.3); padding: 12px; border-radius: 50%; font-size: 1.8rem; display: inline-block; box-shadow: 0 0 20px rgba(217,119,6,0.2);">🏫</span>
                </div>
                <div class="auth-title">CSP RAHMAT-FH</div>
                <div class="auth-subtitle">Espace d'Authentification Sécurisé</div>
        """, unsafe_allow_html=True)

        with st.form("form_login_premium"):
            username = st.text_input(
                "Nom d'utilisateur", 
                placeholder="Ex: admin ou prof..."
            )
            password = st.text_input(
                "Mot de passe", 
                type="password", 
                placeholder="••••••••••••"
            )
            
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("Se connecter au portail", use_container_width=True)
            
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
                        st.success("✨ Accès autorisé. Redirection en cours...")
                        st.rerun()
                    else:
                        st.error("⚠️ Identifiant ou mot de passe incorrect.")
                finally:
                    db.close()
                    
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align: center; margin-top: 2rem;">
                <p style="color: #64748B; font-size: 0.8rem; font-weight: 500;">
                    Plateforme Officielle • Complexe Scolaire Privé Rahmat-FH
                </p>
            </div>
        """, unsafe_allow_html=True)