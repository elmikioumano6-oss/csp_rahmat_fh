import streamlit as st
import pandas as pd
from sqlalchemy import text
from streamlit_option_menu import option_menu
from database.db_config import engine, SessionLocal
from database.models import Base, AnneeScolaire, Classe, Eleve, EcheancePaiement, User
from views.login import afficher_login

# Configuration de la page
st.set_page_config(
    page_title="CSP RAHMAT-FH - Gestion Scolaire",
    page_icon="Logo CSP-RAHMAT-FH.png",
    layout="wide"
)

# ==========================================
# PERSONNALISATION AVANCÉE (CSS CORRIGÉ)
# ==========================================
st.markdown("""
    <style>
    /* Fond global */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #581822 100%);
        color: #FFFFFF !important;
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

    /* Scrollbar visible */
    ::-webkit-scrollbar { width: 16px; height: 16px; }
    ::-webkit-scrollbar-track { background: #0b1329; }
    ::-webkit-scrollbar-thumb { background: #ffffff; border-radius: 8px; border: 3px solid #0b1329; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. INITIALISATION ET MIGRATIONS SÉCURISÉES (SQLite)
# ==========================================
Base.metadata.create_all(bind=engine)

with engine.connect() as connection:
    # Fonction utilitaire pour ajouter une colonne si elle n'existe pas
    def safe_add_column(table_name, column_name, column_definition):
        try:
            res = connection.execute(text(f"PRAGMA table_info({table_name});")).fetchall()
            cols = [row[1] for row in res]
            if column_name not in cols:
                connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};"))
                connection.commit()
        except Exception:
            pass

    # Application des migrations en toute sécurité
    safe_add_column("users", "entite_id", "INTEGER")
    safe_add_column("notes", "semestre", "INTEGER DEFAULT 1")
    safe_add_column("classes", "cycle", "TEXT")
    safe_add_column("classes", "tarif_scolarite", "FLOAT DEFAULT 0.0")
    safe_add_column("enseignants", "specialite", "TEXT")
    safe_add_column("eleves", "telephone", "TEXT")
    safe_add_column("eleves", "montant_reduction", "FLOAT DEFAULT 0.0")
    safe_add_column("eleves", "photo", "TEXT")
    safe_add_column("programmes", "document_pdf", "TEXT")

# ==========================================
# 2. INITIALISATION COMPTES
# ==========================================
def verifier_et_creer_comptes_par_defaut():
    db = SessionLocal()
    try:
        User.__table__.create(bind=engine, checkfirst=True)
        comptes = [
            {"username": "admin", "password": "Rahmatfh2026", "role": "admin", "entite_id": None},
            {"username": "prof", "password": "prof2026", "role": "prof", "entite_id": 1},
            {"username": "parent", "password": "parent2026", "role": "parent", "entite_id": 1}
        ]
        for data in comptes:
            user = db.query(User).filter(User.username == data["username"]).first()
            if not user:
                db.add(User(**data))
        db.commit()
    finally:
        db.close()

verifier_et_creer_comptes_par_defaut()

# ==========================================
# 3. SÉCURITÉ ET VUES
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state.update({'authenticated': False, 'user_role': 'admin', 'username': 'Admin'})

if not st.session_state['authenticated']:
    afficher_login()
    st.stop()

# Importation de toutes les vues
from views.classes import afficher_classes
from views.eleves import afficher_eleves
from views.finances import afficher_finances
from views.enseignants import afficher_enseignants
from views.personnels_roles import afficher_personnels
from views.notes import afficher_notes
from views.photos_masse import afficher_import_photos_masse
from views.cartes_scolaires import afficher_cartes_scolaires
from views.backup import afficher_backup
from views.bulletins import afficher_bulletins
from views.gestion_utilisateurs import afficher_gestion_utilisateurs
from views.presence import afficher_presence
from views.parent_space import afficher_espace_parent
from views.matieres import afficher_matieres
from views.consultation_notes import afficher_consultation_notes
from views.planification import afficher_planification
from views.conseil_classe import afficher_conseil_classe
from views.supervision_cahier import afficher_supervision_cahier
from views.upload_programmes import afficher_upload_programmes
from views.supervision_progression import afficher_supervision_progression
from views.emploi_du_temps import afficher_emploi_du_temps
from views.cahier_texte import afficher_cahier_texte
from views.tableau_finances import afficher_tableau_finances
from views.depenses import afficher_depenses
from views.rapports import afficher_rapports
from views.journal_activite import afficher_journal_activite
from views.messages import afficher_messages

def main():
    db = SessionLocal()
    annee = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
    annee_libelle = annee.libelle if annee else "Non configurée"
    
    role = st.session_state.get('user_role', 'admin')
    username = st.session_state.get('username', 'Utilisateur')

    with st.sidebar:
        st.markdown("### 🏫 CSP RAHMAT-FH")
        st.success(f"Bienvenue, **{username}**")
        st.info(f"🔒 Espace : **{role.upper()}**")
        st.markdown("---")
        
        if role == 'admin':
            page = option_menu(
                "NAVIGATION",
                [
                    "Année scolaire", "Classes & Tarifs", "Matières & Coeffs", "Enseignants", 
                    "Personnels et rôles", "Gestion Comptes", "Inscription Élèves", 
                    "Import Photos en Masse", "Cartes Scolaires", "Saisie de notes", 
                    "Consultations des notes", "Conseil de classe", "Bulletins", 
                    "Supervision cahier", "Import Programmes PDF", "Suivi des Programmes", "Emploi du temps", "Cahier de texte", 
                    "Planification des évaluations", "Présence", "Encaissement", 
                    "Soldes & Impayés", "Tableau Finances", "Dépenses", "Rapports", 
                    "Journal d'activité", "Messages", "Tableau de bord"
                ],
                icons=[
                    'calendar-event', 'building', 'book', 'person-badge', 'shield-lock', 'people-fill',
                    'people', 'folder-plus', 'card-list', 'pencil-square', 'journal-text', 'people-fill', 
                    'file-earmark-text', 'eye', 'file-earmark-pdf', 'graph-up-arrow', 'calendar3', 'journal-bookmark', 'calendar-check', 'check2-square',
                    'cash-coin', 'wallet2', 'graph-up', 'receipt', 'file-bar-graph', 'clock-history', 'chat-dots', 'speedometer'
                ],
                menu_icon="cast", default_index=0,
                styles={
                    "container": {"padding": "5px", "background-color": "#0b1329"},
                    "icon": {"color": "#ffffff", "font-size": "18px"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "4px 0px", "color": "white", "--hover-color": "#331318"},
                    "nav-link-selected": {"background-color": "#800020", "color": "white"},
                }
            )
        elif role == 'parent':
            page = option_menu(
                "ESPACE PARENT", ["Mon Enfant"], 
                icons=['person-badge'], menu_icon="shield-lock", default_index=0,
                styles={
                    "container": {"padding": "5px", "background-color": "#0b1329"}, 
                    "icon": {"color": "#28a745", "font-size": "18px"}, 
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "4px 0px", "color": "white", "--hover-color": "#331318"}, 
                    "nav-link-selected": {"background-color": "#28a745", "color": "white"}
                }
            )
        elif role == 'prof':
            page = option_menu(
                "ESPACE PROF", ["Saisie de notes", "Présence", "Cahier de texte"], 
                icons=['pencil-square', 'calendar-check', 'journal-bookmark'], menu_icon="book-half", default_index=0,
                styles={
                    "container": {"padding": "5px", "background-color": "#0b1329"}, 
                    "icon": {"color": "#ffc107", "font-size": "18px"}, 
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "4px 0px", "color": "white", "--hover-color": "#331318"}, 
                    "nav-link-selected": {"background-color": "#ffc107", "color": "black"}
                }
            )
        else: 
            page = "Accueil"

        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.update({'authenticated': False, 'user_role': 'admin', 'username': None})
            st.rerun()

    # --- EN-TÊTE ---
    col1, col2, col3 = st.columns([3, 1, 1])
    col1.markdown("### 🏫 COMPLEXE SCOLAIRE PRIVE RAHMAT-FH")
    col2.info(f"👤 Profil : {role.upper()}")
    col3.success(f"📅 {annee_libelle}")
    niveau_actif = st.selectbox("Cycle :", ["Primaire", "Collège", "Lycée"], index=1)
    if role == 'admin': st.markdown("---")

    # --- ROUTAGE ---
    if role == 'admin':
        if page == "Classes & Tarifs": afficher_classes()
        elif page == "Matières & Coeffs": afficher_matieres()
        elif page == "Enseignants": afficher_enseignants()
        elif page == "Personnels et rôles": afficher_personnels(niveau_actif)
        elif page == "Gestion Comptes": afficher_gestion_utilisateurs()
        elif page == "Inscription Élèves": afficher_eleves(niveau_actif)
        elif page == "Import Photos en Masse": afficher_import_photos_masse(niveau_actif)
        elif page == "Cartes Scolaires": afficher_cartes_scolaires(niveau_actif)
        elif page == "Saisie de notes": afficher_notes(niveau_actif)
        elif page == "Consultations des notes": afficher_consultation_notes(niveau_actif)
        elif page == "Conseil de classe": afficher_conseil_classe(niveau_actif)
        elif page == "Bulletins": afficher_bulletins(niveau_actif)
        elif page == "Supervision cahier": afficher_supervision_cahier(niveau_actif)
        elif page == "Import Programmes PDF": afficher_upload_programmes(niveau_actif)
        elif page == "Suivi des Programmes": afficher_supervision_progression(niveau_actif)
        elif page == "Emploi du temps": afficher_emploi_du_temps(niveau_actif)
        elif page == "Cahier de texte": afficher_cahier_texte(niveau_actif)
        elif page == "Planification des évaluations": afficher_planification(niveau_actif)
        elif page == "Présence": afficher_presence()
        elif page == "Encaissement": afficher_finances(niveau_actif)
        elif page == "Tableau Finances": afficher_tableau_finances(niveau_actif)
        elif page == "Dépenses": afficher_depenses(niveau_actif)
        elif page == "Rapports": afficher_rapports(niveau_actif)
        elif page == "Journal d'activité": afficher_journal_activite(niveau_actif)
        elif page == "Messages": afficher_messages(niveau_actif)
        elif page == "Tableau de bord": afficher_backup()
        else:
            if page == "Année scolaire":
                st.subheader("📅 Configuration de l'Année")
                with st.form("form_annee"):
                    nouvelle = st.text_input("Ajouter une année (ex: 2026-2027)")
                    if st.form_submit_button("Activer"):
                        db.query(AnneeScolaire).update({AnneeScolaire.active: False})
                        db.add(AnneeScolaire(libelle=nouvelle, active=True))
                        db.commit(); st.rerun()
            elif page == "Soldes & Impayés":
                st.subheader(f"📊 Suivi des Impayés - {niveau_actif}")
                eleves_cycle = db.query(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).all()
                for el in eleves_cycle:
                    exist_ech = db.query(EcheancePaiement).filter(EcheancePaiement.eleve_id == el.id).first()
                    if not exist_ech and el.classe:
                        tarif = el.classe.tarif_scolarite or 0.0
                        reduction = el.montant_reduction or 0.0
                        net = max(0.0, tarif - reduction)
                        db.add(EcheancePaiement(eleve_id=el.id, libelle="Scolarité", montant=net, montant_total=net, montant_paye=0.0))
                db.commit()
                ech = db.query(EcheancePaiement).join(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).all()
                data_impayes = [{"Matricule": e.eleve.matricule, "Nom & Prénom": f"{e.eleve.nom} {e.eleve.prenom}", "Reste (FCFA)": (e.montant_total-e.montant_paye)} for e in ech if (e.montant_total-e.montant_paye) > 0]
                if data_impayes: st.dataframe(pd.DataFrame(data_impayes), use_container_width=True)
                else: st.info(f"✅ Aucun impayé enregistré pour le cycle **{niveau_actif}**.")
            else: st.info(f"Page {page} en développement.")
    elif role == 'parent':
        afficher_espace_parent()
    elif role == 'prof':
        afficher_notes(niveau_actif)

    db.close()

if __name__ == "__main__":
    main()
