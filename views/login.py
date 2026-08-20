import streamlit as st

def afficher_login():
    # Style CSS combinant Glassmorphism, animations et dégradés Bordeaux/Orange
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
        }

        /* Carte de connexion (Droite) */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 40px !important;
            border-radius: 30px !important;
        }

        /* Dégradé Bordeaux-Orange pour les modules */
        .module-badge {
            background: linear-gradient(90deg, #800020, #f97316);
            padding: 10px 20px;
            border-radius: 25px;
            margin: 5px;
            display: inline-block;
            font-weight: 600;
            font-size: 14px;
            color: white;
            box-shadow: 0 4px 15px rgba(128, 0, 32, 0.3);
            opacity: 0;
            animation: fadeIn 0.8s ease forwards;
        }

        /* Animation apparition un par un */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Bouton dynamique */
        div.stButton > button {
            background: #f97316 !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.4, 1], gap="large")

    with col1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 56px; font-weight: 900; line-height: 1;'>L'intelligence au service de l'éducation.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: #94a3b8; margin-top: 20px;'>Une plateforme unifiée pour transformer la donnée scolaire en réussite pédagogique.</p>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Section des modules apparaissant un par un
        modules = ["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte"]
        
        # On génère les badges avec un délai d'apparition progressif
        for i, mod in enumerate(modules):
            delay = i * 0.2  # Décalage de 0.2s par module
            st.markdown(f"""
                <div class='module-badge' style='animation-delay: {delay}s;'>{mod}</div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Piliers d'excellence
        cols_pilars = st.columns(3)
        pilars = [("📈", "Performance"), ("🛡️", "Sécurité"), ("🤖", "IA Scolaire")]
        for i, (ico, name) in enumerate(pilars):
            with cols_pilars[i]:
                st.markdown(f"<div style='background: rgba(255,255,255,0.03); padding:20px; border-radius:20px; text-align:center;'>{ico}<br><b>{name}</b></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("form_login_auth"):
            st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'>Connexion</h2>", unsafe_allow_html=True)
            identifiant = st.text_input("Identifiant")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            submitted = st.form_submit_button("Accéder au Système", use_container_width=True)
            
            if submitted:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()

        st.markdown("<p style='text-align: center; color: #64748b; font-size: 11px; margin-top: 20px;'>CSP RAHMAT-FH © 2026</p>", unsafe_allow_html=True)
