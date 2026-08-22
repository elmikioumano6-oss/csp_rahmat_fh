import streamlit as st
from database.db_config import SessionLocal
from database.models import User
import bcrypt

def afficher_login():
    # Injection de CSS personnalisé pour colorer et embellir la page de connexion
    st.markdown("""
        <style>
            /* Fond général de la page de connexion */
            .stApp {
                background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
            }
            /* Style de la carte de connexion */
            .login-card {
                background: rgba(255, 255, 255, 0.95);
                padding: 2.5rem;
                border-radius: 20px;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .login-title {
                color: #0F172A;
                font-weight: 800;
                font-size: 1.7rem;
                text-align: center;
                margin-bottom: 0.2rem;
            }
            .login-subtitle {
                color: #64748B;
                font-size: 0.9rem;
                text-align: center;
                margin-bottom: 1.5rem;
                font-weight: 500;
            }
        </style>
    """, unsafe_allow_html=True)

    # Espacement vertical pour centrer verticalement
    st.markdown("<div style='height: 3vh;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.25, 1])
    
    with col2:
        st.markdown("""
            <div class="login-card">
                <div style="text-align: center; font-size: 3rem; margin-bottom: 0.5rem;">🏫</div>
                <div class="login-title">CSP RAHMAT-FH</div>
                <div class="login-subtitle">Portail Numérique d'Excellence</div>
        """, unsafe_allow_html=True)
        
        with st.form("form_login_stylise"):
            st.markdown("<label style='font-weight: 600; color: #334155; font-size: 0.9rem;'>Nom d'utilisateur</label>", unsafe_allow_html=True)
            username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre identifiant...", label_visibility="collapsed")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown("<label style='font-weight: 600; color: #334155; font-size: 0.9rem;'>Mot de passe</label>", unsafe_allow_html=True)
            password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe...", label_visibility="collapsed")
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 Se connecter à la session", use_container_width=True)
            
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
                        st.success("✨ Authentification réussie ! Chargement...")
                        st.rerun()
                    else:
                        st.error("❌ Identifiant ou mot de passe incorrect.")
                finally:
                    db.close()
                    
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align: center; margin-top: 1.5rem;">
                <p style="color: #94A3B8; font-size: 0.8rem;">Sécurité Active • Complexe Scolaire Privé Rahmat-FH</p>
            </div>
        """, unsafe_allow_html=True)