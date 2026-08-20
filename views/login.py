import streamlit as st

def afficher_login():
    # Style CSS avec animations plein écran
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            overflow: hidden; /* Empêche les barres de défilement liées au fond */
        }

        /* Conteneur de défilement plein écran */
        .marquee-wrapper {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0; pointer-events: none;
            opacity: 0.15;
            display: flex; flex-direction: column; justify-content: space-around;
        }

        .marquee-line {
            display: flex;
            white-space: nowrap;
            animation: scroll 40s linear infinite;
            font-size: 24px;
            gap: 50px;
        }

        @keyframes scroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }

        /* Contenu principal au-dessus */
        .main-content {
            position: relative;
            z-index: 1;
            max-width: 1100px;
            margin: auto;
            padding-top: 50px;
        }

        /* Carte de connexion élégante */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 40px !important;
            border-radius: 25px !important;
            color: white !important;
        }

        [data-testid="stForm"] label, [data-testid="stForm"] h2 { color: white !important; }
        
        div.stButton > button {
            background: #f97316 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Lignes de modules défilants en arrière-plan
    modules = ["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte", "📅 Emploi du temps", "📝 Notes"]
    line = " &nbsp;&nbsp;&nbsp; ".join([f"<span>{m}</span>" for m in modules])
    
    st.markdown(f"""
        <div class="marquee-wrapper">
            <div class="marquee-line">{line} {line}</div>
            <div class="marquee-line" style="animation-direction: reverse;">{line} {line}</div>
            <div class="marquee-line">{line} {line}</div>
        </div>
    """, unsafe_allow_html=True)

    # Contenu principal
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 55px; font-weight: 900; line-height: 1;'>Pilotez l'école de demain.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: #94a3b8;'>Une architecture logicielle complète pour l'administration, le suivi pédagogique et la gestion financière.</p>", unsafe_allow_html=True)

    with col2:
        with st.form("form_login"):
            st.markdown("<h2 style='text-align: center;'>Connexion</h2>", unsafe_allow_html=True)
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("Entrer dans le système", use_container_width=True):
                st.session_state['authenticated'] = True
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
