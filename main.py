import streamlit as st
import pandas as pd
from sqlalchemy import text
from streamlit_option_menu import option_menu
from database.db_config import engine, SessionLocal
from database.models import Base, AnneeScolaire, Classe, Eleve, EcheancePaiement
from views.login import afficher_login

# Initialisation de la base de données
Base.metadata.create_all(bind=engine)

# ==========================================
# MIGRATIONS AUTOMATIQUES ET ROBUSTES
# ==========================================
with engine.connect() as connection:
    # Table notes
    try:
        res = connection.execute(text("PRAGMA table_info(notes);")).fetchall()
        cols = [row[1] for row in res]
        if "semestre" not in cols: 
            connection.execute(text("ALTER TABLE notes ADD COLUMN semestre INTEGER DEFAULT 1;"))
            connection.commit()
    except Exception: pass

    # Table classes
    try:
        res = connection.execute(text("PRAGMA table_info(classes);")).fetchall()
        cols = [row[1] for row in res]
        if "cycle" not in cols: 
            connection.execute(text("ALTER TABLE classes ADD COLUMN cycle TEXT;"))
        if "tarif_scolarite" not in cols: 
            connection.execute(text("ALTER TABLE classes ADD COLUMN tarif_scolarite FLOAT DEFAULT 0.0;"))
        connection.commit()
    except Exception: pass

    # Table enseignants
    try:
        res = connection.execute(text("PRAGMA table_info(enseignants);")).fetchall()
        cols = [row[1] for row in res]
        if "specialite" not in cols: 
            connection.execute(text("ALTER TABLE enseignants ADD COLUMN specialite TEXT;"))
            connection.commit()
    except Exception: pass

    # Table eleves (SÉCURISATION INDIVIDUELLE DES COLONNES)
    try:
        connection.execute(text("ALTER TABLE eleves ADD COLUMN telephone TEXT;"))
        connection.commit()
    except Exception: pass

    try:
        connection.execute(text("ALTER TABLE eleves ADD COLUMN montant_reduction FLOAT DEFAULT 0.0;"))
        connection.commit()
    except Exception: pass

    try:
        connection.execute(text("ALTER TABLE eleves ADD COLUMN photo TEXT;"))
        connection.commit()
    except Exception: pass

    # Table programmes (Migration automatique de la colonne document_pdf)
    try:
        res = connection.execute(text("PRAGMA table_info(programmes);")).fetchall()
        cols = [row[1] for row in res]
        if "document_pdf" not in cols: 
            connection.execute(text("ALTER TABLE programmes ADD COLUMN document_pdf TEXT;"))
            connection.commit()
    except Exception: pass

    # Table echeances_paiement
    try:
        res = connection.execute(text("PRAGMA table_info(echeances_paiement);")).fetchall()
        cols = [row[1] for row in res]
        if "eleve_id" not in cols: connection.execute(text("ALTER TABLE echeances_paiement ADD COLUMN eleve_id INTEGER;"))
        if "libelle" not in cols: connection.execute(text("ALTER TABLE echeances_paiement ADD COLUMN libelle TEXT DEFAULT 'Scolarité';"))
        if "montant" not in cols: connection.execute(text("ALTER TABLE echeances_paiement ADD COLUMN montant FLOAT DEFAULT 0.0;"))
        if "montant_total" not in cols: connection.execute(text("ALTER TABLE echeances_paiement ADD COLUMN montant_total FLOAT DEFAULT 0.0;"))
        if "montant_paye" not in cols: connection.execute(text("ALTER TABLE echeances_paiement ADD COLUMN montant_paye FLOAT DEFAULT 0.0;"))
        connection.commit()
    except Exception: pass

    # Table paiements_details
    try:
        res = connection.execute(text("PRAGMA table_info(paiements_details);")).fetchall()
        cols = [row[1] for row in res]
        if "echeance_id" not in cols: connection.execute(text("ALTER TABLE paiements_details ADD COLUMN echeance_id INTEGER;"))
        if "eleve_id" not in cols: connection.execute(text("ALTER TABLE paiements_details ADD COLUMN eleve_id INTEGER;"))
        if "montant" not in cols: connection.execute(text("ALTER TABLE paiements_details ADD COLUMN montant FLOAT DEFAULT 0.0;"))
        if "date" not in cols: connection.execute(text("ALTER TABLE paiements_details ADD COLUMN date TEXT;"))
        if "mode" not in cols: connection.execute(text("ALTER TABLE paiements_details ADD COLUMN mode TEXT;"))
        connection.commit()
    except Exception: pass

# Configuration de la page
st.set_page_config(page_title="CSP RAHMAT-FH - Gestion Scolaire", layout="wide")

# ==========================================
# BLOC DE SÉCURITÉ
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_role'] = 'admin'
    st.session_state['user_entity_id'] = None

if not st.session_state['authenticated']:
    afficher_login()
    st.stop()

# ==========================================
# IMPORTATION DES VUES
# ==========================================
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

    # --- BARRE LATÉRALE : MENU INTÉGRAL ---
    with st.sidebar:
        st.markdown("### 🏫 CSP RAHMAT-FH")
        st.caption(f"🔒 Connecté : **{role.upper()}**")
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
                    "container": {"padding": "5px", "background-color": "#1c1c1c"},
                    "icon": {"color": "#0078D4", "font-size": "18px"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "4px 0px", "--hover-color": "#333"},
                    "nav-link-selected": {"background-color": "#0078D4"},
                }
            )
        elif role == 'parent':
            page = option_menu("ESPACE PARENT", ["Mon Enfant"], icons=['person-badge'], menu_icon="shield-lock", default_index=0,
                               styles={"container": {"padding": "5px", "background-color": "#1c1c1c"}, "icon": {"color": "#28a745", "font-size": "18px"}, "nav-link": {"font-size": "14px", "text-align": "left", "margin": "4px 0px", "--hover-color": "#333"}, "nav-link-selected": {"background-color": "#28a745"}})
        elif role == 'prof':
            page = option_menu("ESPACE PROF", ["Saisie de notes", "Présence", "Cahier de texte"], icons=['pencil-square', 'calendar-check', 'journal-bookmark'], menu_icon="book-half", default_index=0,
                               styles={"container": {"padding": "5px", "background-color": "#1c1c1c"}, "icon": {"color": "#ffc107", "font-size": "18px"}, "nav-link": {"font-size": "14px", "text-align": "left", "margin": "4px 0px", "--hover-color": "#333"}, "nav-link-selected": {"background-color": "#ffc107"}})
        else: page = "Accueil"

        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state['authenticated'] = False
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

    db.close()

if __name__ == "__main__":
    main()