import streamlit as st
from database.db_config import SessionLocal
from database.models import User
import bcrypt

def afficher_login():
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2>🏫 COMPLEXE SCOLAIRE PRIVÉ RAHMAT-FH</h2>
            <p>Veuillez vous identifier pour accéder à la plateforme</p>
        </div>
    """, unsafe_allow_html=True)

    # Centrer le formulaire de connexion
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("form_login"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            
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