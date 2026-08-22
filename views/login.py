import streamlit as st
import bcrypt
from database.db_config import SessionLocal
from database.models import User

def afficher_login():
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style='color: #F8FAFC;'>🏫 COMPLEXE SCOLAIRE PRIVÉ RAHMAT-FH</h2>
            <p style='color: #94A3B8;'>Veuillez vous identifier pour accéder à la plateforme</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        with st.form("form_login"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)

            if submit:
                if not username.strip() or not password.strip():
                    st.warning("⚠️ Veuillez remplir tous les champs.")
                else:
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.username == username.strip()).first()
                        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                            st.session_state["authenticated"] = True
                            st.session_state["user_role"] = user.role
                            st.session_state["user_entity_id"] = user.id
                            
                            # Persistance de la session dans l'URL pour éviter la déconnexion au F5
                            st.query_params["logged_in"] = "true"
                            
                            st.success("✅ Connexion réussie ! Chargement...")
                            st.rerun()
                        else:
                            st.error("❌ Nom d'utilisateur ou mot de passe incorrect.")
                    finally:
                        db.close()

    # Style épuré pour le formulaire de connexion
    st.markdown(
        """
        <style>
            div[data-testid="stForm"] {
                background: #1E293B;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.1);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )