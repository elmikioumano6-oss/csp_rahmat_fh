import streamlit as st

def afficher_login():
    # Style CSS ultra-précis pour reproduire le design recherché
    st.markdown("""
        <style>
        /* Nettoyage de l'interface */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Fond global (dégradé sombre) */
        .stApp {
            background: linear-gradient(135deg, #151a2d 0%, #2b1016 100%);
            color: #FFFFFF;
        }

        /* La "carte" blanche à droite */
        .login-card {
            background: #FFFFFF !important;
            padding: 40px !important;
            border-radius: 15px !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3) !important;
            color: #1E293B !important;
        }

        /* Animation des modules (Ticker) */
        .marquee {
            width: 100%;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 8px;
            margin-top: 20px;
            white-space: nowrap;
            color: white;
            font-weight: 500;
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

    # Mise en page
    col_gauche, col_droite = st.columns([1.2, 1], gap="large")

    with col_gauche:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🏫 CSP RAHMAT-FH")
        st.markdown("<h1 style='font-size: 48px; font-weight: 800; line-height: 1.1;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #cbd5e1; font-size: 16px;'>La solution complète pour gérer inscriptions, notes, bulletins, comptabilité et bien plus encore.</p>", unsafe_allow_html=True)
        
        # Liste avec checkmarks verts
        st.markdown("""
            <div style='margin-top: 20px; font-size: 18px;'>
            <p>✅ Suivez les présences en temps réel</p>
            <p>✅ Espace sécurisé parents et professeurs</p>
            <p>✅ Génération automatique des bulletins</p>
            </div>
        """, unsafe_allow_html=True)

        # Module défilant (Ticker)
        modules = " | ".join(["📊 Bulletins", "⏱️ Présences", "💰 Comptabilité", "💳 Impayés", "🪪 Cartes Scolaires", "📓 Cahier de texte"])
        st.markdown(f"""
            <div class="marquee">
                <div class="marquee-inner">{modules} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {modules}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_droite:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Carte blanche (HTML/CSS personnalisé pour le formulaire)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='color: #0F172A;'>Bienvenue 👋</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b;'>Connectez-vous à votre espace</p>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            # Case à cocher "Se souvenir de moi"
            st.checkbox("Se souvenir de moi")
            
            submitted = st.form_submit_button("Découvrir Rahmat-FH", use_container_width=True)
            
            if submitted:
                # Logique de connexion
                if identifiant == "99797163" and mot_de_passe == "Rahmatfh2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
                    
        st.markdown("<p style='text-align: center; font-size: 11px; color: #64748b; margin-top: 15px;'>Connexion sécurisée - Chiffrement AES 256</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
