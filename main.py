from datetime import datetime
import os
from PIL import Image
import bcrypt
import pandas as pd
from database.db_config import SessionLocal, engine
from database.models import (
    AnneeScolaire,
    Base,
    Classe,
    EcheancePaiement,
    Eleve,
    User,
)
from sqlalchemy import text
import streamlit as st
from streamlit_option_menu import option_menu
from views.login import afficher_login

# Initialisation sécurisée de la base de données
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Tables déjà existantes ou initialisées : {e}")

# ==========================================
# AUTO-INITIALISATION DE L'ADMIN SÉCURISÉ
# ==========================================
db_init = SessionLocal()
try:
    admin_check = db_init.query(User).filter(User.username == "admin").first()
    if not admin_check:
        sel = bcrypt.gensalt()
        hashed_pwd = bcrypt.hashpw(
            "password123".encode("utf-8"), sel
        ).decode("utf-8")
        nouvel_admin = User(username="admin", password=hashed_pwd, role="admin")
        db_init.add(nouvel_admin)
        db_init.commit()
except Exception as e:
    print(f"Erreur lors de l'initialisation de l'admin : {e}")
finally:
    db_init.close()

# ==========================================
# MIGRATIONS AUTOMATIQUES (Uniquement pour SQLite en local)
# ==========================================
if "sqlite" in str(engine.url):
    with engine.connect() as connection:
        # Table notes
        try:
            res = connection.execute(text("PRAGMA table_info(notes);")).fetchall()
            cols = [row[1] for row in res]
            if "semestre" not in cols:
                connection.execute(
                    text("ALTER TABLE notes ADD COLUMN semestre INTEGER DEFAULT 1;")
                )
                connection.commit()
        except Exception:
            pass

        # Table classes
        try:
            res = connection.execute(text("PRAGMA table_info(classes);")).fetchall()
            cols = [row[1] for row in res]
            if "cycle" not in cols:
                connection.execute(
                    text("ALTER TABLE classes ADD COLUMN cycle TEXT;")
                )
            if "tarif_scolarite" not in cols:
                connection.execute(
                    text(
                        "ALTER TABLE classes ADD COLUMN tarif_scolarite FLOAT DEFAULT 0.0;"
                    )
                )
            connection.commit()
        except Exception:
            pass

        # Table enseignants
        try:
            res = connection.execute(
                text("PRAGMA table_info(enseignants);")
            ).fetchall()
            cols = [row[1] for row in res]
            if "specialite" not in cols:
                connection.execute(
                    text("ALTER TABLE enseignants ADD COLUMN specialite TEXT;")
                )
                connection.commit()
        except Exception:
            pass

        # Table eleves (SÉCURISATION INDIVIDUELLE DES COLONNES)
        try:
            connection.execute(
                text("ALTER TABLE eleves ADD COLUMN telephone TEXT;")
            )
            connection.commit()
        except Exception:
            pass

        try:
            connection.execute(
                text(
                    "ALTER TABLE eleves ADD COLUMN montant_reduction FLOAT DEFAULT 0.0;"
                )
            )
            connection.commit()
        except Exception:
            pass

        try:
            connection.execute(text("ALTER TABLE eleves ADD COLUMN photo TEXT;"))
            connection.commit()
        except Exception:
            pass

        try:
            connection.execute(text("ALTER TABLE eleves ADD COLUMN parent_id INTEGER;"))
            connection.commit()
        except Exception:
            pass

        # Table programmes (Migration automatique de la colonne document_pdf)
        try:
            res = connection.execute(
                text("PRAGMA table_info(programmes);")
            ).fetchall()
            cols = [row[1] for row in res]
            if "document_pdf" not in cols:
                connection.execute(
                    text("ALTER TABLE programmes ADD COLUMN document_pdf TEXT;")
                )
                connection.commit()
        except Exception:
            pass

        # Table echeances_paiement
        try:
            res = connection.execute(
                text("PRAGMA table_info(echeances_paiement);")
            ).fetchall()
            cols = [row[1] for row in res]
            if "eleve_id" not in cols:
                connection.execute(
                    text("ALTER TABLE echeances_paiement ADD COLUMN eleve_id INTEGER;")
                )
            if "libelle" not in cols:
                connection.execute(
                    text(
                        "ALTER TABLE echeances_paiement ADD COLUMN libelle TEXT DEFAULT 'Scolarité';"
                    )
                )
            if "montant" not in cols:
                connection.execute(
                    text(
                        "ALTER TABLE echeances_paiement ADD COLUMN montant FLOAT DEFAULT 0.0;"
                    )
                )
            if "montant_total" not in cols:
                connection.execute(
                    text(
                        "ALTER TABLE echeances_paiement ADD COLUMN montant_total FLOAT DEFAULT 0.0;"
                    )
                )
            if "montant_paye" not in cols:
                connection.execute(
                    text(
                        "ALTER TABLE echeances_paiement ADD COLUMN montant_paye FLOAT DEFAULT 0.0;"
                    )
                )
            connection.commit()
        except Exception:
            pass

        # Table paiements_details
        try:
            res = connection.execute(
                text("PRAGMA table_info(paiements_details);")
            ).fetchall()
            cols = [row[1] for row in res]
            if "echeance_id" not in cols:
                connection.execute(
                    text(
                        "ALTER TABLE paiements_details ADD COLUMN echeance_id INTEGER;"
                    )
                )
            if "eleve_id" not in cols:
                connection.execute(
                    text(
                        "ALTER TABLE paiements_details ADD COLUMN eleve_id INTEGER;"
                    )
                )
            if "montant" not in cols:
                connection.execute(
                    text(
                        "ALTER TABLE paiements_details ADD COLUMN montant FLOAT DEFAULT 0.0;"
                    )
                )
            if "date" not in cols:
                connection.execute(
                    text("ALTER TABLE paiements_details ADD COLUMN date TEXT;")
                )
            if "mode" not in cols:
                connection.execute(
                    text("ALTER TABLE paiements_details ADD COLUMN mode TEXT;")
                )
            connection.commit()
        except Exception:
            pass

# ==========================================
# CONFIGURATION DE LA PAGE AVEC LOGO
# ==========================================
try:
    icone_ecole = Image.open("Logo CSP-RAHMAT-FH.png")
except Exception:
    icone_ecole = "🏫"  # Icône par défaut si l'image n'est pas trouvée

st.set_page_config(
    page_title="CSP RAHMAT-FH - Gestion d'Élite",
    page_icon=icone_ecole,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# BLOC DE SÉCURITÉ
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = "admin"
    st.session_state["user_entity_id"] = None

if not st.session_state["authenticated"]:
    afficher_login()
    st.stop()

# ==========================================
# IMPORTATION DES VUES
# ==========================================
from views.accueil import afficher_accueil
from views.annee_scolaire import afficher_annee_scolaire
from views.backup import afficher_backup
from views.bulletins import afficher_bulletins
from views.cahier_texte import afficher_cahier_texte
from views.cartes_scolaires import afficher_cartes_scolaires
from views.classes import afficher_classes
from views.conseil_classe import afficher_conseil_classe
from views.consultation_notes import afficher_consultation_notes
from views.depenses import afficher_depenses
from views.eleves import afficher_eleves
from views.emploi_du_temps import afficher_emploi_du_temps
from views.enseignants import afficher_enseignants
from views.finances import afficher_finances
from views.gestion_utilisateurs import afficher_gestion_utilisateurs
from views.journal_activite import afficher_journal_activite
from views.matieres import afficher_matieres
from views.messages import afficher_messages
from views.notes import afficher_notes
from views.parent_space import afficher_espace_parent
from views.personnels_roles import afficher_personnels
from views.photos_masse import afficher_import_photos_masse
from views.planification import afficher_planification
from views.presence import afficher_presence
from views.rapports import afficher_rapports
from views.stats_encaissements import afficher_stats_encaissements
from views.supervision_cahier import afficher_supervision_cahier
from views.supervision_progression import afficher_supervision_progression
from views.tableau_finances import afficher_tableau_finances
from views.upload_programmes import afficher_upload_programmes


def main():
    db = SessionLocal()
    annee = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
    annee_libelle = annee.libelle if annee else "Non configurée"
    role = st.session_state.get("user_role", "admin")

    # --- BARRE LATÉRALE : MENU INTÉGRAL ---
    with st.sidebar:
        # Badge de Session
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px 0;">
                <h2 style='color: #FFFFFF; font-size: 1.35rem; font-weight: 700; margin-bottom: 8px;'>🏫 RAHMAT-FH</h2>
                <div style="display: inline-block; background-color: #D97706; color: #FFFFFF; padding: 4px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    SESSION : {role.upper()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Affichage de la date et l'heure en français
        jours = [
            "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche",
        ]
        mois = [
            "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", 
            "Août", "Septembre", "Octobre", "Novembre", "Décembre",
        ]
        now = datetime.now()
        date_str = f"{jours[now.weekday()]} {now.day} {mois[now.month]} {now.year}"
        heure_str = now.strftime("%H:%M")

        st.markdown(
            f"""
            <div style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); padding: 10px; border-radius: 10px; text-align: center; margin: 15px 0;">
                <div style="font-size: 0.85rem; color: #CBD5E1; font-weight: 600;">📅 {date_str}</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #FBBF24; margin-top: 4px; letter-spacing: 1px;">⏰ {heure_str}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        if role == "admin":
            page = option_menu(
                "NAVIGATION",
                [
                    "Accueil", "Année scolaire", "Classes & Tarifs", "Matières & Coeffs", "Enseignants", 
                    "Personnels et rôles", "Gestion Comptes", "Inscription Élèves", 
                    "Import Photos en Masse", "Cartes Scolaires", "Espace Profs", 
                    "Consultations des notes", "Conseil de classe", "Bulletins", 
                    "Supervision cahier", "Import Programmes PDF", "Suivi des Programmes", 
                    "Emploi du temps", "Planification des évaluations", "Encaissement", 
                    "Stats Encaissements", "Soldes & Impayés", "Tableau Finances", "Dépenses", "Rapports", 
                    "Journal d'activité", "Messages", "Espace Parent", "Tableau de bord",
                ],
                icons=[
                    "house", "calendar-event", "building", "book", "person-badge", "shield-lock", "people-fill",
                    "people", "folder-plus", "card-list", "book-half", "journal-text", "people-fill", 
                    "file-earmark-text", "eye", "file-earmark-pdf", "graph-up-arrow", "calendar3", 
                    "calendar-check", "cash-coin", "graph-up", "wallet2", "graph-up", "receipt", "file-bar-graph", 
                    "clock-history", "chat-dots", "person-badge", "speedometer",
                ],
                menu_icon="cast", default_index=0,
                styles={
                    "container": {"padding": "5px", "background-color": "#0F172A"},
                    "icon": {"color": "#D97706", "font-size": "16px"},
                    "nav-link": {
                        "font-size": "13px", "text-align": "left", "margin": "3px 0px", 
                        "color": "#E2E8F0", "--hover-color": "#1E293B",
                    },
                    "nav-link-selected": {"background-color": "#D97706"},
                },
            )
        elif role == "parent":
            page = option_menu(
                "ESPACE PARENT", ["Mon Enfant"], icons=["person-badge"], 
                menu_icon="shield-lock", default_index=0,
                styles={
                    "container": {"padding": "5px", "background-color": "#0F172A"},
                    "icon": {"color": "#10B981", "font-size": "16px"},
                    "nav-link": {
                        "font-size": "13px", "text-align": "left", "margin": "3px 0px", 
                        "color": "#E2E8F0", "--hover-color": "#1E293B",
                    },
                    "nav-link-selected": {"background-color": "#10B981"},
                },
            )
        elif role == "prof":
            page = option_menu(
                "ESPACE PROF", ["Saisie de notes", "Présence", "Cahier de texte"], 
                icons=["pencil-square", "calendar-check", "journal-bookmark"], 
                menu_icon="book-half", default_index=0,
                styles={
                    "container": {"padding": "5px", "background-color": "#0F172A"},
                    "icon": {"color": "#F59E0B", "font-size": "16px"},
                    "nav-link": {
                        "font-size": "13px", "text-align": "left", "margin": "3px 0px", 
                        "color": "#E2E8F0", "--hover-color": "#1E293B",
                    },
                    "nav-link-selected": {"background-color": "#F59E0B"},
                },
            )
        else:
            page = "Accueil"

        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- EN-TÊTE SUPÉRIEUR ÉLÉGANT ---
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 1.2rem 1.8rem; border-radius: 12px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 1.5rem;">
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">🏫 COMPLEXE SCOLAIRE PRIVÉ RAHMAT-FH</h3>
                <p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">Plateforme de Gestion Administrative & Académique</p>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <span style="background: rgba(217, 119, 6, 0.2); color: #FBBF24; padding: 0.4rem 0.8rem; border-radius: 8px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(217, 119, 6, 0.3);">📅 {annee_libelle}</span>
                <span style="background: rgba(59, 130, 246, 0.2); color: #60A5FA; padding: 0.4rem 0.8rem; border-radius: 8px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(59, 130, 246, 0.3);">👤 {role.upper()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    niveau_actif = st.selectbox(
        "🎯 Cycle Actif :", ["Primaire", "Collège", "Lycée"], index=1
    )
    if role == "admin":
        st.markdown("---")

    # --- ROUTAGE ---
    if role == "admin":
        if page == "Accueil":
            afficher_accueil()
        elif page == "Année scolaire":
            afficher_annee_scolaire()
        elif page == "Classes & Tarifs":
            afficher_classes()
        elif page == "Matières & Coeffs":
            afficher_matieres()
        elif page == "Enseignants":
            afficher_enseignants()
        elif page == "Personnels et rôles":
            afficher_personnels(niveau_actif)
        elif page == "Gestion Comptes":
            afficher_gestion_utilisateurs()
        elif page == "Inscription Élèves":
            afficher_eleves(niveau_actif)
        elif page == "Import Photos en Masse":
            afficher_import_photos_masse(niveau_actif)
        elif page == "Cartes Scolaires":
            afficher_cartes_scolaires(niveau_actif)
        elif page == "Espace Profs":
            st.subheader("👨‍🏫 Espace Enseignants (Supervision Admin)")
            tab_p1, tab_p2, tab_p3 = st.tabs(["Saisie de notes", "Présence", "Cahier de texte"])
            with tab_p1:
                afficher_notes(niveau_actif)
            with tab_p2:
                afficher_presence()
            with tab_p3:
                afficher_cahier_texte(niveau_actif)
        elif page == "Consultations des notes":
            afficher_consultation_notes(niveau_actif)
        elif page == "Conseil de classe":
            afficher_conseil_classe(niveau_actif)
        elif page == "Bulletins":
            afficher_bulletins(niveau_actif)
        elif page == "Supervision cahier":
            afficher_supervision_cahier(niveau_actif)
        elif page == "Import Programmes PDF":
            afficher_upload_programmes(niveau_actif)
        elif page == "Suivi des Programmes":
            afficher_supervision_progression(niveau_actif)
        elif page == "Emploi du temps":
            afficher_emploi_du_temps(niveau_actif)
        elif page == "Planification des évaluations":
            afficher_planification(niveau_actif)
        elif page == "Encaissement":
            afficher_finances(niveau_actif)
        elif page == "Stats Encaissements":
            afficher_stats_encaissements(niveau_actif)
        elif page == "Soldes & Impayés":
            afficher_soldes_impayes(niveau_actif) if "afficher_soldes_impayes" in globals() else st.info("Module en cours")
        elif page == "Tableau Finances":
            afficher_tableau_finances(niveau_actif)
        elif page == "Dépenses":
            afficher_depenses(niveau_actif)
        elif page == "Rapports":
            afficher_rapports(niveau_actif)
        elif page == "Journal d'activité":
            afficher_journal_activite(niveau_actif)
        elif page == "Messages":
            afficher_messages(niveau_actif)
        elif page == "Espace Parent":
            afficher_espace_parent()
        elif page == "Tableau de bord":
            afficher_backup()

    elif role == "parent":
        if page == "Mon Enfant":
            afficher_espace_parent()

    elif role == "prof":
        if page == "Saisie de notes":
            afficher_notes(niveau_actif)
        elif page == "Présence":
            afficher_presence()
        elif page == "Cahier de texte":
            afficher_cahier_texte(niveau_actif)

    db.close()


if __name__ == "__main__":
    main()