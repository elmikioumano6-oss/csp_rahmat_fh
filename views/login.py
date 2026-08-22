import streamlit as st
import bcrypt
from database.db_config import SessionLocal
from database.models import User

def afficher_login():
    # Design CSS épuré et professionnel pour la page de connexion
    st.markdown("""
        <style>
            .stForm {
                background-color: #1E1E1E;
                padding: 2.5rem;
                border-radius: 12px;
                border: 1px solid #333;
                box-shadow: 0 8px 16px rgba(0,0,0,0.4);
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #0078D4; font-weight: 700;'>🔐 Connexion Sécurisée</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #aaa; margin-bottom: 2rem;'>CSP RAHMAT-FH - Gestion Scolaire</p>", unsafe_allow_html=True)
        
        with st.form("form_connexion"):
            username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre identifiant")
            password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.warning("Veuillez remplir tous les champs.")
                else:
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.username == username).first()
                        
                        # Vérification sécurisée du mot de passe haché avec bcrypt
                        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                            st.session_state['authenticated'] = True
                            st.session_state['user_role'] = user.role
                            st.session_state['user_entity_id'] = user.id
                            
                            # Enregistrement du témoin persistant dans l'URL
                            st.query_params["logged_in"] = "true"
                            
                            st.success("Connexion réussie ! Redirection...")
                            st.rerun()
                        else:
                            st.error("Identifiants incorrects. Veuillez vérifier vos accès.")
                    except Exception as e:
                        st.error(f"Erreur technique : {e}")
                    finally:
                        db.close()