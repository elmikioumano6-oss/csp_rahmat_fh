import streamlit as st

def afficher_login():
    # Style CSS avec animation de défilement (Marquee)
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        .stApp {
            background: linear-gradient(135deg, #0F172A 0%, #581822 100%);
            color: #FFFFFF;
        }

        /* Carte blanche élégante */
        [data-testid="stForm"] {
            background: #FFFFFF !important;
            padding: 40px !important;
            border-radius: 20px !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
        }

        /* Animation de défilement pour les modules */
        .marquee-container {
            width: 100%;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 12px;
            margin-top: 30px;
            border-left: 4px solid #800020;
        }
        
        .marquee-text {
            display: inline-block;
            white-space: nowrap;
            animation: scroll-left 30s linear infinite;
            font-size: 17px;
            font-weight: 500;
            color: #FFFFFF;
        }

        @keyframes scroll-left {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }

        .module-item {
            display: inline-block;
            margin-right: 40px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Division de l'écran
    col_gauche, col_droite = st.columns([1.3, 1], gap="large")

    with col_gauche:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🏫 **CSP RAHMAT-FH**")
        st.markdown("<h1 style='font-size: 42px; font-weight: 900;'>Tout pour piloter votre établissement.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 16px; color: #cbd5e1;'>La solution numérique complète pour gérer les inscriptions, notes, bulletins, comptabilité et le suivi des élèves.</p>", unsafe_allow_html=True)
        
        # --- BLOC DÉFILANT (MARQUEE) ---
        modules = [
            ("📊 Bulletins", "📊"), ("⏱️ Présences", "⏱️"), 
            ("💰 Comptabilité", "💰"), ("💳 Impayés", "💳"), 
            ("🪪 Cartes Scolaires", "🪪"), ("📓 Cahier de texte", "📓"),
            ("📅 Emploi du temps", "📅"), ("📝 Notes", "📝")
        ]
        
        # Création de la chaîne de texte défilante
        marquee_content = "".join([f"<span class='module-item'>{icon} {name}</span>" for name, icon in modules])
        
        st.markdown(f"""
            <div class="marquee-container">
                <div class="marquee-text">{marquee_content} &nbsp;&nbsp;&nbsp; {marquee_content}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_droite:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("form_connexion_moderne"):
            st.markdown("<h2 style='color: #0F172A;'>Bienvenue 👋</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b; font-size: 14px;'>Connectez-vous à votre espace</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Identifiant / Téléphone", placeholder="Entrez votre identifiant...")
            mot_de_passe = st.text_input("Mot de passe", type="password", placeholder="••••••••••••")
            
            submitted = st.form_submit_button("Se connecter", use_container_width=True)

            if submitted:
                if identifiant == "admin" and mot_de_passe == "Rahmatfh2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()
                elif identifiant == "prof" and mot_de_passe == "prof2026":
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'prof'
                    st.rerun()
                else:
                    st.error("Identifiant incorrect.")

        st.markdown("<p style='text-align: center; font-size: 11px; color: #cbd5e1;'>CSP RAHMAT-FH © 2026</p>", unsafe_allow_html=True)
