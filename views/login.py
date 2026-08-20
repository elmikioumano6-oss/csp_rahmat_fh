import streamlit as st

def afficher_login():
    # CSS pour le style "Pêle-mêle", le défilement vertical et le bloc vertical
    st.markdown("""
        <style>
        /* Fond global */
        .stApp {
            background: linear-gradient(135deg, #151a2d 0%, #2b1016 100%);
            color: #FFFFFF;
            overflow: hidden;
        }

        /* Arrière-plan avec icônes éparpillées */
        .bg-container {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0; pointer-events: none;
        }
        .icon-scatter {
            position: absolute; opacity: 0.1; font-size: 50px;
        }

        /* Bloc de connexion : Rectangle vertical */
        [data-testid="stForm"] {
            background: #FFFFFF !important;
            padding: 40px !important;
            border-radius: 15px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            min-height: 550px !important; /* Rend le bloc vertical */
            display: flex; flex-direction: column; justify-content: center;
        }

        /* Animation de défilement vertical */
        .vertical-marquee {
            height: 150px; overflow: hidden;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px; padding: 10px;
            text-align: center;
        }
        .vertical-marquee-inner {
            animation: scroll-up 10s linear infinite;
        }
        @keyframes scroll-up {
            0% { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
        </style>
    """, unsafe_allow_html=True)

    # Insertion des icônes en arrière-plan (Pêle-mêle)
    st.markdown("""
        <div class="bg-container">
            <div class="icon-scatter" style="top: 10%; left: 5%;">📚</div>
            <div class="icon-scatter" style="top: 20%; left: 85%;">🎓</div>
            <div class="icon-scatter" style="top: 50%; left: 15%;">🖊️</div>
            <div class="icon-scatter" style="top: 80%; left: 75%;">📐</div>
            <div class="icon-scatter" style="top: 30%; left: 40%;">💰</div>
            <div class="icon-scatter" style="top: 70%; left: 30%;">🏫</div>
        </div>
    """, unsafe_allow_html=True)

    # Disposition
    col_gauche, col_droite = st.columns([1.3, 1], gap="large")

    with col_gauche:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 50px; font-weight: 900;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: #cbd5e1;'>Analysez les performances en un coup d'œil.</p>", unsafe_allow_html=True)
        
        # Défilement vertical des modules
        modules = ["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte"]
        marquee_html = "".join([f"<p style='margin: 10px 0;'>{m}</p>" for m in modules])
        
        st.markdown(f"""
            <div class="vertical-marquee">
                <div class="vertical-marquee-inner">{marquee_html} {marquee_html}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_droite:
        # Formulaire Vertical
        with st.form("form_login_vertical"):
            st.markdown("<h2 style='color: #1E293B;'>Bienvenue 👋</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b;'>Connectez-vous à votre espace</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            st.checkbox("Se souvenir de moi")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Découvrir Rahmat-FH", use_container_width=True)
            
            if submitted:
                # Logique simplifiée
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()

        st.markdown("<p style='text-align: center; font-size: 11px; color: #cbd5e1; margin-top: 10px;'>Connexion sécurisée - Chiffrement AES 256</p>", unsafe_allow_html=True)
