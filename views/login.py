import streamlit as st

def afficher_login():
    # Style CSS épuré et moderne
    st.markdown("""
        <style>
        /* Fond global sombre professionnel */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
        }

        /* Carte de connexion : Blanc pur avec ombre douce */
        [data-testid="stForm"] {
            background: #ffffff !important;
            padding: 40px !important;
            border-radius: 20px !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3) !important;
            border: none !important;
        }

        /* Inputs : Style minimaliste */
        [data-testid="stForm"] input {
            background-color: #f1f5f9 !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 12px !important;
        }

        /* Bouton : Couleur accentuée (Bleu électrique) */
        div.stButton > button {
            background-color: #3b82f6 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 12px !important;
        }

        /* Modules : Cartes "Glassmorphism" */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            transition: transform 0.3s ease;
        }
        .glass-card:hover { transform: scale(1.02); }
        </style>
    """, unsafe_allow_html=True)

    # Disposition
    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #3b82f6; text-transform: uppercase; letter-spacing: 2px; font-size: 14px;'>CSP RAHMAT-FH</h3>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 52px; font-weight: 800; line-height: 1;'>L'excellence scolaire numérique.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: #94a3b8; margin-top: 20px;'>Une interface intuitive pour piloter votre établissement avec précision et fluidité.</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Modules en grille élégante au lieu de défilement chaotique
        modules = [
            ("📊", "Gestion des Bulletins"), ("⏱️", "Suivi Présences"), 
            ("💰", "Comptabilité"), ("💳", "Gestion Impayés"), 
            ("🪪", "Cartes Scolaires"), ("📓", "Cahier de texte")
        ]
        
        # Affichage des modules en colonnes pour une meilleure lisibilité
        cols_mod = st.columns(2)
        for i, (icon, name) in enumerate(modules):
            with cols_mod[i % 2]:
                st.markdown(f"<div class='glass-card'>{icon} {name}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("form_login_final"):
            st.markdown("<h2 style='color: #0f172a; font-weight: 700;'>Accès Espace</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 30px;'>Connectez-vous pour continuer</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Identifiant")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submitted:
                # Logique simplifiée
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()

        st.markdown("<p style='text-align: center; font-size: 11px; color: #475569; margin-top: 20px;'>Sécurisé par Rahmat-FH © 2026</p>", unsafe_allow_html=True)
