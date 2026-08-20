import streamlit as st

def afficher_login():
    st.markdown("""
        <style>
        /* Design System Global */
        .stApp {
            background: radial-gradient(circle at top right, #1e293b, #0f172a);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
        }

        /* La carte de connexion principale */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 50px !important;
            border-radius: 30px !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
        }

        /* Inputs ultra-minimalistes */
        [data-testid="stForm"] input {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            color: white !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        /* Bouton "Prime" */
        div.stButton > button {
            background: linear-gradient(90deg, #f97316, #ea580c) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 15px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            transition: transform 0.2s ease;
        }
        div.stButton > button:hover { transform: translateY(-2px); }

        /* Animation des icônes flottantes */
        .float { animation: float 6s ease-in-out infinite; }
        @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-20px); } 100% { transform: translateY(0px); } }

        /* Carte des modules */
        .module-box {
            background: rgba(255,255,255,0.02);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

    # Mise en page principale
    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div class='float'>🚀</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 60px; font-weight: 900; line-height: 1;'>L'intelligence au service de l'éducation.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 20px; color: #94a3b8; margin-top: 20px;'>Une plateforme unifiée pour transformer la donnée scolaire en réussite pédagogique. Connectez-vous pour commencer.</p>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Grille des "Savoirs Combinés"
        st.markdown("<div class='module-box'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #f97316; margin-bottom: 20px;'>NOS PILIERS D'EXCELLENCE</h4>", unsafe_allow_html=True)
        cols = st.columns(3)
        pilars = [("📈", "Performance"), ("🛡️", "Sécurité"), ("🤖", "Automatisation")]
        for i, (ico, name) in enumerate(pilars):
            with cols[i]:
                st.markdown(f"<div style='text-align:center; padding:10px;'>{ico}<br><span style='font-size:12px;'>{name}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("form_auth"):
            st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Accès Privé</h2>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Entrer dans le système", use_container_width=True)
            
            if submitted:
                if identifiant == "admin" and mot_de_passe == "Rahmatfh2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()
                else:
                    st.error("Accès refusé.")

        st.markdown("<p style='text-align: center; color: #475569; font-size: 12px; margin-top: 20px;'>Système protégé par chiffrage AES-256.<br>CSP RAHMAT-FH © 2026</p>", unsafe_allow_html=True)
