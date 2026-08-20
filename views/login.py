import streamlit as st

def afficher_login():
    # Style CSS pour unifier la carte blanche à droite et embellir la page
    st.markdown("""
        <style>
        /* Masquer les éléments natifs superflus */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Fond global de la page de connexion */
        .stApp {
            background: linear-gradient(135deg, #151a2d 0%, #2b1016 100%);
            color: #FFFFFF;
        }

        /* Transformation complète du formulaire en une magnifique carte blanche unique */
        [data-testid="stForm"] {
            background: #FFFFFF !important;
            padding: 35px !important;
            border-radius: 20px !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
            border: none !important;
        }

        /* Forcer les textes et libellés à l'intérieur du formulaire en couleur sombre */
        [data-testid="stForm"] label p, [data-testid="stForm"] label, [data-testid="stForm"] span {
            color: #1E293B !important;
            font-weight: 600 !important;
        }

        /* Style des champs de saisie */
        [data-testid="stForm"] input {
            background-color: #f8fafc !important;
            color: #1E293B !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }

        /* Animation de défilement des modules (Ticker) à gauche */
        .marquee {
            width: 100%;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.08);
            padding: 12px 15px;
            border-radius: 10px;
            margin-top: 25px;
            white-space: nowrap;
            color: white;
            font-weight: 500;
            border-left: 4px solid #800020;
        }
        .marquee-inner {
            display: inline-block;
            animation: marquee 25s linear infinite;
        }
        @keyframes marquee {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-50%, 0); }
        }
        </style>
    """, unsafe_allow_html=True)

    # Disposition en deux colonnes
    col_gauche, col_droite = st.columns([1.3, 1], gap="large")

    with col_gauche:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🏫 CSP RAHMAT-FH")
        st.markdown("<h1 style='font-size: 44px; font-weight: 800; line-height: 1.1;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #cbd5e1; font-size: 16px; margin-top: 10px;'>La solution complète pour gérer inscriptions, notes, bulletins, comptabilité et bien plus encore.</p>", unsafe_allow_html=True)
        
        # Liste avec checkmarks
        st.markdown("""
            <div style='margin-top: 25px; font-size: 16px; line-height: 1.8;'>
            <p>✅ Suivez les présences en temps réel</p>
            <p>✅ Espace sécurisé parents et professeurs</p>
            <p>✅ Génération automatique des bulletins</p>
            </div>
        """, unsafe_allow_html=True)

        # Modules défilants
        modules = " &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; ".join(["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte"])
        st.markdown(f"""
            <div class="marquee">
                <div class="marquee-inner">{modules} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; {modules}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_droite:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Le formulaire forme maintenant une seule et unique carte blanche élégante
        with st.form("form_login"):
            st.markdown("<h2 style='color: #0F172A; margin-bottom: 0px;'>Bienvenue 👋</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b; font-size: 13px; margin-bottom: 20px;'>Connectez-vous à votre espace de gestion</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Numéro de téléphone ou Identifiant", placeholder="Entrez votre identifiant...")
            mot_de_passe = st.text_input("Mot de passe", type="password", placeholder="••••••••••••")
            
            st.checkbox("Se souvenir de moi")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Découvrir Rahmat-FH", use_container_width=True)
            
            if submitted:
                if identifiant == "admin" and mot_de_passe == "Rahmatfh2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()
                elif identifiant == "prof" and mot_de_passe == "prof2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'prof'
                    st.rerun()
                elif identifiant == "parent" and mot_de_passe == "parent2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'parent'
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
                    
        st.markdown("<p style='text-align: center; font-size: 11px; color: #cbd5e1; margin-top: 15px;'>Connexion sécurisée - Chiffrement AES 256</p>", unsafe_allow_html=True)
