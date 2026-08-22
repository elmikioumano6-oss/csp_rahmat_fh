import streamlit as st
from database.db_config import SessionLocal
from database.models import User
import bcrypt
from PIL import Image
import os
import base64
from io import BytesIO

def afficher_login():
    # Fonction pour convertir l'image en base64 afin de l'insérer proprement en HTML centré
    def get_image_base64(path):
        if os.path.exists(path):
            img = Image.open(path)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        return ""

    logo_b64 = get_image_base64("Logo CSP-RAHMAT-FH.png")
    
    st.markdown(f"""
        <style>
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            
            .stApp {{
                background: linear-gradient(135deg, #0B132B 0%, #1C2541 50%, #581C25 100%);
            }}
            
            .auth-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                padding: 10px;
            }}
            
            .auth-card {{
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(220, 38, 38, 0.3);
                padding: 1.8rem 1.2rem;
                border-radius: 20px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
                width: 100%;
                max-width: 380px;
                margin: 0 auto;
            }
            
            @media (max-width: 640px) {{
                .auth-card {{
                    padding: 1.2rem 0.8rem;
                    border: none;
                    box-shadow: none;
                    background: transparent;
                }}
            }}
            
            .auth-header-title {{
                color: #CBD5E1;
                font-size: 0.7rem;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 700;
                margin-bottom: 6px;
            }}
            
            .modules-ticker-container {{
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(220, 38, 38, 0.4);
                border-radius: 10px;
                overflow: hidden;
                white-space: nowrap;
                padding: 5px 0;
                margin-bottom: 1rem;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
            }}
            
            .modules-ticker-text {{
                display: inline-block;
                padding-left: 100%;
                animation: ticker 25s linear infinite;
                color: #F8FAFC;
                font-size: 0.75rem;
                font-weight: 600;
            }}
            
            @keyframes ticker {{
                0% {{ transform: translate3d(0, 0, 0); }}
                100% {{ transform: translate3d(-100%, 0, 0); }}
            }}
            
            /* --- CENTRAGE ABSOLU DU LOGO EN HTML/CSS --- */
            .logo-wrapper {{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                margin-bottom: 0.5rem;
            }}
            .logo-wrapper img {{
                width: 75px;
                height: auto;
                display: block;
            }}
            
            .auth-title {{
                color: #F8FAFC;
                font-weight: 800;
                font-size: 1.25rem;
                text-align: center;
                margin-top: 0.2rem;
            }}
            .auth-subtitle {{
                color: #EF4444;
                font-size: 0.7rem;
                text-align: center;
                margin-bottom: 1rem;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-weight: 700;
            }}
            
            .stTextInput input {{
                background-color: #1E293B !important;
                color: #FFFFFF !important;
                border: 1px solid #334155 !important;
                border-radius: 8px !important;
                padding: 7px 10px !important;
                font-size: 0.85rem !important;
            }}
            
            label {{
                color: #EF4444 !important;
                font-weight: 700 !important;
                font-size: 0.9rem !important;
            }}
            
            .stButton button {{
                background: linear-gradient(135deg, #991B1B 0%, #7F1D1D 100%) !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
                border-radius: 8px !important;
                border: none !important;
                padding: 0.45rem 1rem !important;
            }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='auth-container'><div class='auth-card'>", unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-header-title">
            ✨ Complexe Scolaire Privé ✨
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="modules-ticker-container">
            <div class="modules-ticker-text">
                📚 Suivi Académique &nbsp;&bull;&nbsp; 
                📝 Saisie des Notes &nbsp;&bull;&nbsp; 
                📊 Bulletins & Conseils de Classe &nbsp;&bull;&nbsp; 
                💳 Cartes Scolaires &nbsp;&bull;&nbsp; 
                💰 Gestion Financière & Encaissements &nbsp;&bull;&nbsp; 
                🏫 Emplois du Temps & &Eacute;valuations &nbsp;&bull;&nbsp; 
                👨‍👩‍👧 Espace Parent &nbsp;&bull;&nbsp; 
                📋 Cahier de Texte & Suivi des Programmes
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Affichage du logo centré par CSS pur
    if logo_b64:
        st.markdown(f"""
            <div class="logo-wrapper">
                <img src="data:image/png;base64,{logo_b64}" alt="Logo RAHMAT-FH">
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; font-size: 2rem;'>🏫</div>", unsafe_allow_html=True)

    st.markdown("""
            <div class="auth-title">CSP RAHMAT-FH</div>
            <div class="auth-subtitle">Portail d'Administration</div>
    """, unsafe_allow_html=True)

    with st.form("form_login_css_centre"):
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
                
    st.markdown("</div></div>", unsafe_allow_html=True)