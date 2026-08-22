import streamlit as st
from database.db_config import SessionLocal
from database.models import User
import bcrypt

def afficher_login():
    st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
            <h2 style="color: #0F172A; font-weight: 700; font-size: 1.6rem; margin-bottom: 5px;">🏫 COMPLEXE SCOLAIRE PRIVÉ RAHMAT-FH</h2>
            <p style="color: #64748B; font-size: 0.95rem;">Veuillez vous identifier pour accéder à la plateforme</p>
        </div>
    """, unsafe_allow_html=True)

    # Centrer le formulaire de connexion
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        with st.form("form_login"):
            # Champs épurés avec placeholders à l'intérieur et labels masqués proprement
            username = st.text_input(
                "Nom d'utilisateur", 
                placeholder="Nom d'utilisateur", 
                label_visibility="collapsed"
            )
            password = st.text_input(
                "Mot de passe", 
                type="password", 
                placeholder="Mot de passe", 
                label_visibility="collapsed"
            )
            
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
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
                        st.success("Connexion réussie !")
                        st.rerun()
                    else:
                        st.error("Identifiant ou mot de passe incorrect.")
                finally:
                    db.close()