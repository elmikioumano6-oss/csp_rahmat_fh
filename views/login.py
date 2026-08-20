import streamlit as st

def afficher_login():
    # Style CSS avec palette institutionnelle (Rubis & Or)
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }

        /* Lignes de défilement (Parallax) */
        .marquee-wrapper {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0; pointer-events: none; opacity: 0.12;
        }
        .marquee-line {
            display: flex; white-space: nowrap;
            animation: scroll 60s linear infinite;
            font-size: 20px; gap: 80px;
        }
        
        /* Couleur des modules défilants : Dégradé Rubis vers Or */
        .mod-item {
            background: linear-gradient(90deg, #881337, #d97706);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

        /* Carte de connexion minimaliste */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(30px);
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding: 50px !important;
            border-radius: 30px !important;
        }

        /* Bouton "Or" pour un aspect premium */
        div.stButton > button {
            background: linear-gradient(90deg, #b45309, #d97706) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            padding: 15px !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    # Lignes de modules en arrière-plan
    modules = ["📊 BULLETINS", "⏱️ PRÉSENCES", "💰 COMPTABILITÉ", "💳 IMPAYÉS", "🪪 CARTES SCOLAIRES", "📓 CAHIER DE TEXTE", "📅 EMPLOI DU TEMPS", "📝 NOTES"]
    line = " &nbsp;&nbsp;&nbsp; ".join([f"<span class='mod-item'>{m}</span>" for m in modules])
    
    st.markdown(f"""
        <div class="marquee-wrapper">
            <div class="marquee-line" style="margin-top: 100px;">{line} {line}</div>
            <div class="marquee-line" style="margin-top: 200px; animation-direction: reverse;">{line} {line}</div>
            <div class="marquee-line" style="margin-top: 200px;">{line} {line}</div>
        </div>
    """, unsafe_allow_html=True)

    # Contenu centré (Largeur maîtrisée)
    st.markdown("<div style='max-width: 1000px; margin: auto; position: relative; z-index: 1;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #d97706; letter-spacing: 3px; font-size: 12px;'>CSP RAHMAT-FH</h3>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 55px; font-weight: 900; line-height: 1.1;'>L'intelligence au service de l'éducation.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: #94a3b8; margin-top: 20px;'>Une plateforme de gestion de nouvelle génération. Robuste, sécurisée et pensée pour la réussite.</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown("<h2 style='text-align: center; font-weight: 800;'>Connexion</h2>", unsafe_allow_html=True)
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            submitted = st.form_submit_button("Accéder au Système", use_container_width=True)
            if submitted:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
