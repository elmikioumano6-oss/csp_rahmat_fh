import streamlit as st
import hashlib
from database.db_config import SessionLocal
from database.models import User

# Fonction de hachage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialisation admin
def init_default_admin():
    db = SessionLocal()
    try:
        if not db.query(User).first():
            # Création de l'admin sans argument de référence si la colonne n'existe pas
            admin = User(
                username="admin", 
                password=hash_password("admin123"), 
                role="admin"
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

def afficher_login():
    # Initialisation
    init_default_admin()
    
    # CSS pour le design de la boîte
    st.markdown("""
        <style>
        .login-card {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid #e6e6e6;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Création de colonnes pour centrer la fenêtre
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.title("🔐 Connexion")
        st.write("CSP RAHMAT-FH")
        
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

        if submit:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.username == username).first()
                if user and user.password == hash_password(password):
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = user.role
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")
            finally:
                db.close()
        st.markdown('</div>', unsafe_allow_html=True)