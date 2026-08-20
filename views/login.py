import streamlit as st

def afficher_login():
    # Style CSS avec largeur maîtrisée
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
        }

        /* Limiter la largeur globale pour un aspect premium */
        .main-container {
            max-width: 1000px;
            margin: 0 auto;
            padding-top: 50px;
        }

        /* Carte de connexion élégante */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 35px !important;
            border-radius: 25px !important;
        }

        /* Badges Bordeaux-Orange */
        .module-badge {
            background: linear-gradient(90deg, #800020, #f97316);
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            display: inline-block;
            font-size: 13px;
            font-weight: 600;
            color: white;
            opacity: 0;
            animation: fadeIn 0.8s ease forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Bouton */
        div.stButton > button {
            background: #f97316 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Utilisation de colonnes tampons pour réduire la largeur globale
    # [1, 10, 1] crée des marges sur les côtés
    _, main_col, _ = st.columns([0.5, 10, 0.5])
    
    with main_col:
        col1, col2 = st.columns([1.2, 1], gap="large")

        with col1:
            st.markdown("<h1 style='font-size: 42px; font-weight: 900; line-height: 1.1;'>L'excellence numérique pour votre école.</h1>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 16px; color: #94a3b8; margin-top: 15px;'>Une plateforme unifiée, intuitive et sécurisée.</p>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Modules apparaissant un par un
            modules = ["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte"]
            for i, mod in enumerate(modules):
                delay = i * 0.15
                st.markdown(f"<div class='module-badge' style='animation-delay: {delay}s;'>{mod}</div>", unsafe_allow_html=True)

        with col2:
            with st.form("form_login_auth"):
                st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Connexion</h2>", unsafe_allow_html=True)
                identifiant = st.text_input("Identifiant")
                mot_de_passe = st.text_input("Mot de passe", type="password")
                
                submitted = st.form_submit_button("Accéder au Système", use_container_width=True)
                
                if submitted:
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()

            st.markdown("<p style='text-align: center; color: #64748b; font-size: 10px; margin-top: 10px;'>CSP RAHMAT-FH © 2026</p>", unsafe_allow_html=True)
