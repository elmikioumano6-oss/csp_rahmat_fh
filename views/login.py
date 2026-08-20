import streamlit as st

def afficher_login():
    # CSS final : Couleur professionnelle (Orange/Bordeaux) et visibilité parfaite
    st.markdown("""
        <style>
        /* Fond global académique */
        .stApp {
            background-color: #f8fafc;
            color: #1e293b;
        }

        /* La Carte blanche */
        [data-testid="stForm"] {
            background: #FFFFFF !important;
            padding: 40px !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
            border: 1px solid #e2e8f0 !important;
        }

        /* Bouton de connexion style "Lokkol" (Orange professionnel) */
        div.stButton > button {
            background-color: #f97316 !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
        }

        /* Champs de saisie (Focus en orange) */
        [data-testid="stForm"] input:focus {
            border: 2px solid #f97316 !important;
        }

        /* Modules défilants (Couleur Bordeaux et Orange) */
        .vertical-marquee {
            height: 150px; overflow: hidden;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 10px; padding: 10px;
            text-align: center;
            border-left: 5px solid #f97316; /* Bordure Orange */
        }
        .module-item {
            color: #581822; /* Texte Bordeaux */
            font-weight: 700;
            margin: 10px 0;
            display: block;
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

    # Arrière-plan icônes
    st.markdown("""
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; opacity: 0.1;">
            <div style="position: absolute; top: 10%; left: 5%; font-size: 50px;">📚</div>
            <div style="position: absolute; top: 20%; left: 85%; font-size: 50px;">🎓</div>
            <div style="position: absolute; top: 50%; left: 15%; font-size: 50px;">🖊️</div>
            <div style="position: absolute; top: 80%; left: 75%; font-size: 50px;">📐</div>
            <div style="position: absolute; top: 30%; left: 40%; font-size: 50px;">💰</div>
        </div>
    """, unsafe_allow_html=True)

    col_gauche, col_droite = st.columns([1.3, 1], gap="large")

    with col_gauche:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #f97316; letter-spacing: 2px;'>LOKKOL ITA / RAHMAT-FH</h3>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 45px; font-weight: 900; color: #1e293b;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: #64748b;'>La solution complète pour gérer les inscriptions, notes, bulletins, comptabilité et le suivi des élèves.</p>", unsafe_allow_html=True)
        
        # Modules défilants (texte Bordeaux)
        modules = ["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte"]
        marquee_html = "".join([f"<span class='module-item'>{m}</span>" for m in modules])
        
        st.markdown(f"""
            <div class="vertical-marquee">
                <div class="vertical-marquee-inner">{marquee_html} {marquee_html}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_droite:
        with st.form("form_login_vertical"):
            st.markdown("<h2 style='color: #1e293b;'>Bienvenue 👋</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b;'>Connectez-vous à votre espace</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            st.checkbox("Se souvenir de moi")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Découvrir Lokkol Ita", use_container_width=True)
            
            if submitted:
                # Logique simplifiée
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()

        st.markdown("<p style='text-align: center; font-size: 11px; color: #94a3b8; margin-top: 10px;'>Connexion sécurisée - Chiffrement AES 256</p>", unsafe_allow_html=True)
