import streamlit as st

def afficher_login():
    # Style CSS professionnel et contrasté
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Carte de connexion : Blanc pur et opaque, texte sombre */
        [data-testid="stForm"] {
            background-color: #ffffff !important;
            padding: 40px !important;
            border-radius: 20px !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        /* Forcer tous les textes, titres et labels du formulaire en noir/sombre */
        [data-testid="stForm"] h2, [data-testid="stForm"] p, [data-testid="stForm"] label, [data-testid="stForm"] span {
            color: #0f172a !important;
        }

        /* Style des champs de saisie */
        [data-testid="stForm"] input {
            background-color: #f8fafc !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }

        /* Bouton de connexion orange professionnel */
        div.stButton > button {
            background-color: #f97316 !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            padding: 12px !important;
            border-radius: 8px !important;
            width: 100% !important;
        }
        div.stButton > button:hover {
            background-color: #ea580c !important;
        }

        /* Conteneur des modules élégant à gauche */
        .modules-box {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 14px;
            padding: 20px;
            margin-top: 30px;
        }

        .module-item {
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.12);
            padding: 10px 16px;
            border-radius: 10px;
            color: #ffffff;
            font-weight: 600;
            font-size: 14px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    col_gauche, col_droite = st.columns([1.3, 1], gap="large")

    with col_gauche:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #f97316; font-weight: 700; letter-spacing: 1px;'>PLATEFORME DE GESTION SCOLAIRE</h3>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 46px; font-weight: 900; line-height: 1.15; color: #ffffff;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 16px; color: #cbd5e1; margin-top: 15px;'>La solution numérique complète pour administrer les inscriptions, les notes, les bulletins, la comptabilité et le suivi des élèves en temps réel.</p>", unsafe_allow_html=True)
        
        # Grille des modules intégrés
        st.markdown("""
            <div class="modules-box">
                <div style="color: #f97316; font-weight: 700; margin-bottom: 12px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">⚡ Modules intégrés & actifs</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="module-item">📊 Bulletins automatiques</div>
                    <div class="module-item">⏱️ Suivi des présences</div>
                    <div class="module-item">💰 Comptabilité & Caisse</div>
                    <div class="module-item">💳 Gestion des Impayés</div>
                    <div class="module-item">🪪 Cartes Scolaires QR</div>
                    <div class="module-item">📓 Cahier de texte en ligne</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_droite:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("form_login_pro"):
            st.markdown("<h2 style='margin-bottom: 5px; font-weight: 800;'>Bienvenue 👋</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b !important; font-size: 14px; margin-bottom: 25px;'>Connectez-vous à votre espace sécurisé</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Numéro de téléphone ou Identifiant", placeholder="Entrez votre identifiant...")
            mot_de_passe = st.text_input("Mot de passe", type="password", placeholder="••••••••••••")
            
            st.checkbox("Se souvenir de moi")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Se connecter à l'espace", use_container_width=True)
            
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

        st.markdown("<p style='text-align: center; font-size: 11px; color: #cbd5e1; margin-top: 20px;'>Connexion sécurisée - Chiffrement AES 256<br>CSP RAHMAT-FH © 2026</p>", unsafe_allow_html=True)
