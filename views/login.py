import streamlit as st
from database.db_config import SessionLocal
from database.models import User

def afficher_login():
    # Style CSS optimisé pour une visibilité maximale (High Contrast)
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }

        /* Conteneur de défilement plus visible */
        .marquee-wrapper {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0; pointer-events: none; opacity: 0.4;
        }
        .marquee-line {
            display: flex; white-space: nowrap;
            animation: scroll 60s linear infinite;
            font-size: 22px; gap: 40px;
        }
        @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

        /* Badges opaques pour une lisibilité totale */
        .mod-chip {
            background-color: rgba(136, 19, 55, 0.9);
            border: 2px solid #f97316;
            padding: 10px 25px;
            border-radius: 50px;
            color: #ffffff;
            font-weight: 800;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        }

        /* Carte de connexion (Formulaire) */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            padding: 50px !important;
            border-radius: 30px !important;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5) !important;
        }
        
        [data-testid="stForm"] h2, [data-testid="stForm"] label, [data-testid="stForm"] p { 
            color: #ffffff !important; 
        }
        
        /* Bouton dynamique */
        div.stButton > button {
            background: linear-gradient(90deg, #881337, #f97316) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            padding: 16px !important;
            border-radius: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Contenu défilant (Marquee)
    modules = ["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte", "📅 Emploi du temps", "📝 Notes"]
    line = "".join([f"<div class='mod-chip'>{m}</div>" for m in modules])
    
    st.markdown(f"""
        <div class="marquee-wrapper">
            <div class="marquee-line" style="margin-top: 50px;">{line} {line}</div>
            <div class="marquee-line" style="margin-top: 150px; animation-direction: reverse;">{line} {line}</div>
            <div class="marquee-line" style="margin-top: 250px;">{line} {line}</div>
        </div>
    """, unsafe_allow_html=True)

    # Contenu principal
    st.markdown("<div style='max-width: 1100px; margin: auto; position: relative; z-index: 1;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #f97316; letter-spacing: 2px; font-size: 14px;'>CSP RAHMAT-FH</h3>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 55px; font-weight: 900; line-height: 1;'>L'intelligence au service de l'éducation.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: #cbd5e1; margin-top: 20px;'>Gérez votre établissement avec puissance et sérénité. Une suite complète pour l'administration, les enseignants et les parents.</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown("<h2 style='text-align: center; font-weight: 700;'>Connexion</h2>", unsafe_allow_html=True)
            identifiant = st.text_input("Nom d'utilisateur")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submitted:
                if not identifiant or not mot_de_passe:
                    st.error("Veuillez remplir tous les champs.")
                else:
                    db = SessionLocal()
                    try:
                        # Interrogation directe de la table User sur le Cloud
                        user = db.query(User).filter(User.username == identifiant).first()
                        
                        if user and user.password == mot_de_passe:
                            st.session_state['authenticated'] = True
                            st.session_state['user_role'] = user.role  # 'admin', 'prof', 'parent'
                            st.session_state['user_entity_id'] = user.entite_id
                            st.session_state['username'] = user.username
                            db.close()
                            st.rerun()
                        else:
                            st.error("Identifiants incorrects.")
                    except Exception as e:
                        st.error(f"Erreur technique : {e}")
                    finally:
                        db.close()

    st.markdown("</div>", unsafe_allow_html=True)
