import streamlit as st

def afficher_login():
    # Style CSS épuré, centré et professionnel
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            font-family: 'Inter', sans-serif;
        }

        /* Centrage et limitation de la largeur pour l'élégance */
        .main-wrapper { max-width: 1000px; margin: auto; padding-top: 50px; }

        /* Carte de connexion style SaaS */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 40px !important;
            border-radius: 25px !important;
        }

        /* Badge des modules (Dégradé Bordeaux/Orange) */
        .module-badge {
            background: linear-gradient(90deg, #800020, #f97316);
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px;
            display: inline-block;
            font-size: 13px;
            font-weight: 500;
            color: white;
            opacity: 0;
            animation: fadeIn 0.6s ease forwards;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* Bouton dynamique */
        div.stButton > button {
            background: #f97316 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Conteneur centré
    st.markdown("<div class='main-wrapper'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        st.markdown("<h1 style='font-size: 40px; font-weight: 900; line-height: 1.1;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 16px; color: #94a3b8; margin-bottom: 25px;'>Une interface unifiée pour gérer l'intégralité du cycle de vie scolaire.</p>", unsafe_allow_html=True)
        
        # Liste exhaustive des modules
        modules = [
            "📅 Année scolaire", "🏫 Classes", "📖 Matières", "👨‍🏫 Enseignants", "👥 Personnels", 
            "🔐 Comptes", "🧑‍🎓 Inscriptions", "📸 Photos", "🪪 Cartes", "📝 Saisie Notes", 
            "🔍 Consult. Notes", "🏆 Conseil Classe", "📄 Bulletins", "👁️ Supervision", 
            "📂 Programmes", "📊 Suivi Prog.", "🕒 Emploi Temps", "📓 Cahier Texte", 
            "🗓️ Planification", "✅ Présence", "💰 Encaissement", "📉 Soldes", 
            "📈 Finances", "💸 Dépenses", "📑 Rapports", "📜 Journal", "💬 Messages", "⚙️ Tableau Bord"
        ]
        
        # Affichage en nuage de tags
        for i, mod in enumerate(modules):
            delay = i * 0.05 # Apparition rapide mais séquentielle
            st.markdown(f"<div class='module-badge' style='animation-delay: {delay}s;'>{mod}</div>", unsafe_allow_html=True)

    with col2:
        with st.form("form_login_auth"):
            st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Connexion</h2>", unsafe_allow_html=True)
            identifiant = st.text_input("Numéro de téléphone")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            submitted = st.form_submit_button("Accéder au Système", use_container_width=True)
            
            if submitted:
                # Logique simplifiée
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()

        st.markdown("<p style='text-align: center; color: #64748b; font-size: 10px; margin-top: 15px;'>CSP RAHMAT-FH © 2026</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
