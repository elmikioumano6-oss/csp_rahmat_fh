import streamlit as st
from database.db_config import SessionLocal
from database.models import User
import bcrypt

def afficher_login():
    # En-tête captivant avec fond et style moderne
    st.markdown("""
        <div style="text-align: center; padding: 2.5rem 1rem 1rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🏫</div>
            <h1 style="color: #0F172A; font-weight: 800; font-size: 1.8rem; margin: 0; letter-spacing: -0.5px;">CSP RAHMAT-FH</h1>
            <p style="color: #64748B; font-size: 1rem; margin-top: 5px; font-weight: 500;">Plateforme Numérique de Gestion Administrative & Pédagogique</p>
        </div>
    """, unsafe_allow_html=True)

    # Centrage du formulaire dans une disposition élégante
    _, col_center, _ = st.columns([1, 1.2, 1])
    
    with col_center:
        st.markdown("""
            <div style="background: #FFFFFF; padding: 2rem; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05); border: 1px solid #F1F5F9;">
        """, unsafe_allow_html=True)
        
        with st.form("form_login_captivant"):
            st.markdown("<p style='font-weight: 600; color: #1E293B; margin-bottom: 15px; font-size: 1.1rem;'>🔒 Connexion à votre session</p>", unsafe_allow_html=True)
            
            username = st.text_input(
                "Nom d'utilisateur", 
                placeholder="Entrez votre identifiant...", 
                label_visibility="collapsed"
            )
            password = st.text_input(
                "Mot de passe", 
                type="password", 
                placeholder="Entrez votre mot de passe...", 
                label_visibility="collapsed"
            )
            
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("Se connecter à la plateforme", use_container_width=True)
            
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
                        st.success("✨ Connexion réussie, redirection...")
                        st.rerun()
                    else:
                        st.error("❌ Identifiant ou mot de passe incorrect.")
                finally:
                    db.close()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Petit texte d'aide en bas
        st.markdown("""
            <div style="text-align: center; margin-top: 1.5rem;">
                <p style="color: #94A3B8; font-size: 0.85rem;">En cas de problème d'accès, contactez l'administrateur du complexe.</p>
            </div>
        """, unsafe_allow_html=True)