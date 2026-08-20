import streamlit as st

def afficher_login():
    # Style CSS pour transformer le formulaire en carte blanche moderne
    st.markdown("""
        <style>
        /* Masquer les éléments natifs superflus sur la page de connexion */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Fond global de la page de connexion */
        .stApp {
            background: linear-gradient(135deg, #0F172A 0%, #581822 100%);
            color: #FFFFFF;
        }

        /* Transformation du conteneur st.form en une carte blanche élégante */
        [data-testid="stForm"] {
            background: #FFFFFF !important;
            padding: 35px !important;
            border-radius: 20px !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
            border: none !important;
        }

        /* Forcer tous les textes et libellés à l'intérieur de la carte en couleur sombre pour la lisibilité */
        [data-testid="stForm"] label p, [data-testid="stForm"] label, [data-testid="stForm"] h2 {
            color: #1E293B !important;
            font-weight: 600 !important;
        }

        /* Style des champs de saisie à l'intérieur de la carte */
        [data-testid="stForm"] input {
            color: #1E293B !important;
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Espacement vertical pour centrer l'ensemble
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Division de l'écran en deux colonnes (Gauche : Présentation / Droite : Carte de connexion)
    col_gauche, col_droite = st.columns([1.3, 1], gap="large")

    with col_gauche:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🏫 **CSP RAHMAT-FH**")
        st.markdown("<h1 style='font-size: 42px; font-weight: 800; line-height: 1.2;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 16px; color: #cbd5e1; margin-top: 15px;'>La solution complète pour gérer les inscriptions, les notes, les bulletins, la comptabilité et le suivi des élèves en temps réel.</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("✅ **Suivez les présences et les notes en temps réel**")
        st.markdown("✅ **Espace sécurisé dédié aux parents et professeurs**")
        st.markdown("✅ **Génération automatique des bulletins et cartes scolaires**")

    with col_droite:
        # Le formulaire devient automatiquement la carte blanche élégante
        with st.form("form_connexion_moderne"):
            st.markdown("<h2>Bienvenue 👋</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 20px;'>Connectez-vous à votre espace de gestion</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Nom d'utilisateur ou Téléphone", placeholder="Entrez votre identifiant...")
            mot_de_passe = st.text_input("Mot de passe", type="password", placeholder="••••••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Bouton de validation
            submitted = st.form_submit_button("Se connecter", use_container_width=True)

            if submitted:
                if identifiant == "admin" and mot_de_passe == "Rahmatfh2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'admin'
                    st.success("Connexion réussie !")
                    st.rerun()
                elif identifiant == "prof" and mot_de_passe == "prof2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'prof'
                    st.success("Connexion réussie !")
                    st.rerun()
                elif identifiant == "parent" and mot_de_passe == "parent2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'parent'
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")

        st.markdown("<p style='text-align: center; font-size: 11px; color: #cbd5e1; margin-top: 20px;'>Connexion sécurisée - Chiffrement des données<br>CSP RAHMAT-FH © 2026</p>", unsafe_allow_html=True)
