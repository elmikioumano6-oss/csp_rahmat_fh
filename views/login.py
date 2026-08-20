import streamlit as st

def afficher_login():
    # Style CSS optimisé pour la visibilité totale des icônes
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }

        /* Lignes de défilement immersives */
        .marquee-wrapper {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0; pointer-events: none; opacity: 0.15;
            display: flex; flex-direction: column; justify-content: space-around;
        }
        .marquee-line {
            display: flex; white-space: nowrap;
            animation: scroll 60s linear infinite;
            font-size: 22px; gap: 60px;
        }
        @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

        /* Badge élégant pour les modules (Bordeaux/Or) */
        .mod-chip {
            background: rgba(128, 0, 32, 0.4);
            border: 1px solid #d97706;
            padding: 8px 20px;
            border-radius: 50px;
            color: #ffffff;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }

        /* Formulaire de connexion */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.04) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 45px !important;
            border-radius: 30px !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
        }
        
        [data-testid="stForm"] h2, [data-testid="stForm"] label { color: white !important; }
        
        div.stButton > button {
            background: linear-gradient(90deg, #881337, #d97706) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            padding: 15px !important;
            border-radius: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Contenu défilant (les icones + les noms)
    modules = ["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte", "📅 Emploi du temps", "📝 Notes"]
    line = "".join([f"<div class='mod-chip'>{m}</div>" for m in modules])
    
    st.markdown(f"""
        <div class="marquee-wrapper">
            <div class="marquee-line">{line} {line}</div>
            <div class="marquee-line" style="animation-direction: reverse;">{line} {line}</div>
            <div class="marquee-line">{line} {line}</div>
        </div>
    """, unsafe_allow_html=True)

    # Contenu principal
    st.markdown("<div style='max-width: 1000px; margin: auto; position: relative; z-index: 1;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #d97706; letter-spacing: 2px; font-size: 13px;'>CSP RAHMAT-FH</h3>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 50px; font-weight: 900; line-height: 1;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 17px; color: #94a3b8; margin-top: 20px;'>Une interface intuitive, puissante et esthétique pour la gestion scolaire nouvelle génération.</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown("<h2 style='text-align: center; font-weight: 700;'>Connexion</h2>", unsafe_allow_html=True)
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("Accéder au Système", use_container_width=True):
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
