import streamlit as st
from database.db_config import SessionLocal
from database.models import AnneeScolaire
# Si vous gérez des utilisateurs en base de données, importez votre modèle utilisateur ici
# from database.models import Utilisateur 

def afficher_login():
    # Style CSS spécifique pour la page de connexion (carte moderne et effets)
    st.markdown("""
        <style>
        /* Masquer le menu natif de Streamlit et le header sur la page de login */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Fond de la page de connexion */
        .stApp {
            background: linear-gradient(135deg, #0F172A 0%, #581822 100%);
            color: #FFFFFF;
        }

        /* Carte de connexion moderne à droite */
        .login-card {
            background: #FFFFFF;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
            color: #1E293B;
            max-width: 450px;
            margin: auto;
        }

        .login-card h2 {
            color: #0F172A !important;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .login-card p {
            color: #64748b !important;
            font-size: 14px;
            margin-bottom: 25px;
        }

        /* Forcer les labels du formulaire en noir pour la lisibilité sur fond blanc */
        .login-card label {
            color: #1E293B !important;
            font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Espacement vertical pour centrer verticalement
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Division de l'écran en deux colonnes (Gauche : Présentation / Droite : Carte de connexion)
    col_gauche, col_droite = st.columns([1.3, 1], gap="large")

    with col_gauche:
        st.markdown("<br>", unsafe_allow_html=True)
        # Logo ou titre principal de l'établissement
        st.markdown("### 🏫 **CSP RAHMAT-FH**")
        st.markdown("<h1 style='font-size: 42px; font-weight: 800; line-height: 1.2;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 16px; color: #cbd5e1; margin-top: 15px;'>La solution complète pour gérer les inscriptions, les notes, les bulletins, la comptabilité et le suivi des élèves en temps réel.</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("✅ **Suivez les présences et les notes en temps réel**")
        st.markdown("✅ **Espace sécurisé dédié aux parents et professeurs**")
        st.markdown("✅ **Génération automatique des bulletins et cartes scolaires**")

    with col_droite:
        # Conteneur simulant la carte blanche élégante
        with st.container():
            st.markdown("""
                <div class="login-card">
                    <h2>Bienvenue 👋</h2>
                    <p>Connectez-vous à votre espace de gestion</p>
                </div>
            """, unsafe_allow_html=True)

            # Formulaire de connexion à l'intérieur de la zone
            with st.form("form_connexion_moderne"):
                identifiant = st.text_input("Nom d'utilisateur ou Téléphone", placeholder="Entrez votre identifiant...")
                mot_de_passe = st.text_input("Mot de passe", type="password", placeholder="••••••••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Bouton de validation stylisé
                submitted = st.form_submit_button("Se connecter", use_container_width=True)

                if submitted:
                    # Logique de vérification basique (ou vérification depuis votre base de données)
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

            st.markdown("<p style='text-align: center; font-size: 11px; color: #94a3b8; margin-top: 20px;'>Connexion sécurisée - Chiffrement des données<br>CSP RAHMAT-FH © 2026</p>", unsafe_allow_html=True)
