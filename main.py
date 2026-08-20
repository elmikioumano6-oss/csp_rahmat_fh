st.markdown("""
    <style>
    /* Fond global */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #581822 100%);
        color: #FFFFFF !important;
        overflow-y: auto !important;
    }
    
    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background-color: #0b1329;
        border-right: 1px solid #800020;
    }

    /* Textes et titres */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
    }

    /* Correction ciblée : Rendre le texte des menus déroulants noir sur fond blanc */
    div[data-baseweb="select"] div, div[data-baseweb="select"] span {
        color: #000000 !important;
    }

    /* Alertes */
    div.stAlert {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #FFFFFF !important;
        border: 1px solid #800020;
    }

    /* --- GESTION UNIVERSELLE DE LA BARRE DE DÉFILEMENT --- */
    /* Pour Chrome, Edge, Safari */
    ::-webkit-scrollbar {
        width: 14px !important;
        height: 14px !important;
        display: block !important;
    }
    ::-webkit-scrollbar-track {
        background: #0b1329 !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #ffffff !important;
        border-radius: 7px !important;
        border: 3px solid #0b1329 !important;
    }

    /* Pour Firefox */
    * {
        scrollbar-width: auto !important;
        scrollbar-color: #ffffff #0b1329 !important;
    }
    </style>
""", unsafe_allow_html=True)
