import streamlit as st

def afficher_login():
    # Style CSS pour la page de connexion moderne, les icônes de fond et la carte blanche
    st.markdown("""
        <style>
        /* Masquer les éléments natifs superflus */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Fond global avec un magnifique dégradé professionnel */
        .stApp {
            background: linear-gradient(135deg, #0F172A 0%, #581822 100%);
            color: #FFFFFF;
            overflow: hidden;
        }

        /* Transformation du formulaire en carte blanche élégante à droite */
        [data-testid="stForm"] {
            background: #FFFFFF !important;
            padding: 40px !important;
            border-radius: 20px !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
            border: none !important;
        }

        /* Textes à l'intérieur de la carte blanche */
        [data-testid="stForm"] label p, [data-testid="stForm"] label, [data-testid="stForm"] h2 {
            color: #1E293B !important;
            font-weight: 600 !important;
        }

        /* Champs de saisie stylisés */
        [data-testid="stForm"] input {
            color: #1E293B !important;
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }

        /* Boîte élégante pour mettre en avant les modules configurés */
        .module-card {
            background: rgba(255, 255, 255, 0.08);
            border-left: 4px solid #ff4b4b;
            padding: 18px 22px;
            border-radius: 0 12px 12px 0;
            margin-top: 25px;
            backdrop-filter: blur(8px);
            font-size: 16px;
            font-weight: 500;
            color: #FFFFFF;
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        }

        /* Style des icônes d'arrière-plan éparpillées sur l'écran */
        .bg-icon {
            position: absolute;
            opacity: 0.06;
            font-size: 65px;
            z-index: 0;
            pointer-events: none;
            user-select: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Arrière-plan riche en icônes représentant vos modules (Livres, Notes, Finances, etc.)
    st.markdown("""
        <div style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; pointer-events: none; overflow: hidden;">
            <div class="bg-icon" style="top: 8%; left: 4%;">📚</div>
            <div class="bg-icon" style="top: 72%; left: 10%;">🎓</div>
            <div class="bg-icon" style="top: 18%; left: 42%;">📊</div>
            <div class="bg-icon" style="top: 82%; left: 38%;">💳</div>
            <div class="bg-icon" style="top: 12%; left: 68%;">📝</div>
            <div class="bg-icon" style="top: 68%; left: 82%;">💰</div>
            <div class="bg-icon" style="top: 42%; left: 22%;">🏫</div>
            <div class="bg-icon" style="top: 35%; left: 88%;">📋</div>
        </div>
    """, unsafe_allow_html=True)

    # Espacement vertical
    st.markdown("<br>", unsafe_allow_html=True)

    # Division de l'écran en deux colonnes
    col_gauche, col_droite = st.columns([1.3, 1], gap="large")

    with col_gauche:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #cbd5e1; letter-spacing: 1px;'>🏫 COMPLEXE SCOLAIRE PRIVÉ</h3>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 44px; font-weight: 900; line-height: 1.15; color: #FFFFFF;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 16px; color: #94a3b8; margin-top: 15px;'>La solution numérique complète pour administrer les inscriptions, les notes, les bulletins, la comptabilité et le suivi des élèves.</p>", unsafe_allow_html=True)
        
        # Bloc de mise en valeur des modules de l'application
        st.markdown("""
            <div class="module-card">
                📊 <b>Modules configurés :</b> Gestion des Bulletins en 1 clic • Suivi des Présences • Comptabilité & Impayés • Cartes Scolaires • Cahier de texte
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='color: #cbd5e1; font-size: 14px;'>🔒 Espace sécurisé dédié à l'administration, aux enseignants et aux parents d'élèves.</p>", unsafe_allow_html=True)

    with col_droite:
        # Formulaire de connexion intégré dans la carte blanche
        with st.form("form_connexion_moderne"):
            st.markdown("<h2 style='color: #0F172A; margin-bottom: 0px;'>Bienvenue 👋</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b; font-size: 13px; margin-bottom: 25px;'>Connectez-vous à votre espace de gestion</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Nom d'utilisateur ou Téléphone", placeholder="Entrez votre identifiant...")
            mot_de_passe = st.text_input("Mot de passe", type="password", placeholder="••••••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
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
