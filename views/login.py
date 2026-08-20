import streamlit as st

def afficher_login():
    # CSS professionnel pour reproduire l'identité visuelle de votre modèle
    st.markdown("""
        <style>
        /* Nettoyage */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Fond global académique clair */
        .stApp {
            background-color: #f5f7f9;
            color: #1e293b;
        }

        /* Arrière-plan avec icônes dispersées (pele-mêle) */
        .bg-icon-container {
            position: absolute; width: 100%; height: 100%; z-index: 0; pointer-events: none;
        }
        .icon { position: absolute; opacity: 0.15; font-size: 60px; }

        /* Carte de connexion (Rectangle vertical) */
        [data-testid="stForm"] {
            background: #ffffff !important;
            padding: 45px !important;
            border-radius: 20px !important;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1) !important;
            border: none !important;
        }

        /* Bouton de connexion Orange (Lokkol style) */
        div.stButton > button {
            background-color: #f8961e !important;
            color: white !important;
            border: none !important;
            padding: 12px !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
        }

        /* Typographie */
        h1 { color: #1e293b !important; font-weight: 900 !important; }
        h2 { color: #1e293b !important; margin-bottom: 25px !important; }
        .feature-text { color: #1e293b !important; font-weight: 600 !important; font-size: 16px; margin: 10px 0; }
        </style>
    """, unsafe_allow_html=True)

    # Icônes de fond (Pêle-mêle)
    st.markdown("""
        <div class="bg-icon-container">
            <div class="icon" style="top: 10%; left: 5%;">📚</div>
            <div class="icon" style="top: 25%; left: 40%;">✏️</div>
            <div class="icon" style="top: 60%; left: 10%;">🎓</div>
            <div class="icon" style="top: 80%; left: 85%;">🏫</div>
            <div class="icon" style="top: 15%; left: 90%;">💰</div>
        </div>
    """, unsafe_allow_html=True)

    # Mise en page
    col_gauche, col_droite = st.columns([1.2, 1], gap="large")

    with col_gauche:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🏫 CSP RAHMAT-FH")
        st.markdown("<h1>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 16px;'>La solution complète pour gérer inscriptions, notes, bulletins, comptabilité et bien plus encore.</p>", unsafe_allow_html=True)
        
        # Liste des fonctionnalités (identique visuellement)
        st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("<p class='feature-text'>✅ Suivez les présences en temps réel</p>", unsafe_allow_html=True)
        st.markdown("<p class='feature-text'>✅ Espace sécurisé parents et professeurs</p>", unsafe_allow_html=True)
        st.markdown("<p class='feature-text'>✅ Génération automatique des bulletins</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_droite:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown("<h2>Bienvenue 👋</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b; font-size: 14px;'>Connectez-vous à votre espace</p>", unsafe_allow_html=True)
            
            # Champs de saisie
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            st.checkbox("Se souvenir de moi")
            
            # Bouton de connexion
            submitted = st.form_submit_button("Découvrir Rahmat-FH", use_container_width=True)
            
            if submitted:
                if identifiant == "admin" and mot_de_passe == "Rahmatfh2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")

        st.markdown("<p style='text-align: center; font-size: 11px; color: #94a3b8; margin-top: 15px;'>Connexion sécurisée - Chiffrement AES 256</p>", unsafe_allow_html=True)
