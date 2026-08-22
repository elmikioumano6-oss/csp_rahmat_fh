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
# MIGRATIONS AUTOMATIQUES RAPIDES
# ==========================================
@st.cache_resource
def executer_migrations():
    if "sqlite" in str(engine.url):
        with engine.connect() as connection:
            try:
                res = connection.execute(text("PRAGMA table_info(notes);")).fetchall()
                cols = [row[1] for row in res]
                if "semestre" not in cols:
                    connection.execute(text("ALTER TABLE notes ADD COLUMN semestre INTEGER DEFAULT 1;"))
                    connection.commit()
            except Exception: pass
            
            try:
                res = connection.execute(text("PRAGMA table_info(classes);")).fetchall()
                cols = [row[1] for row in res]
                if "cycle" not in cols:
                    connection.execute(text("ALTER TABLE classes ADD COLUMN cycle TEXT;"))
                if "tarif_scolarite" not in cols:
                    connection.execute(text("ALTER TABLE classes ADD COLUMN tarif_scolarite FLOAT DEFAULT 0.0;"))
                connection.commit()
            except Exception: pass
    return True

executer_migrations()

# ==========================================
# CONFIGURATION DE LA PAGE AVEC LOGO
# ==========================================
try:
    icone_ecole = Image.open("Logo CSP-RAHMAT-FH.png")
except Exception:
    icone_ecole = "🏫"

st.set_page_config(
    page_title="CSP RAHMAT-FH - Gestion d'Élite",
    page_icon=icone_ecole,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# BLOC DE SÉCURITÉ PERSISTANT
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = "admin"
    st.session_state["user_entity_id"] = None

if st.query_params.get("logged_in") == "true":
    st.session_state["authenticated"] = True

if not st.session_state["authenticated"]:
    afficher_login()
    st.stop()


def main():
    db = SessionLocal()
    annee = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
    annee_libelle = annee.libelle if annee else "Non configurée"
    role = st.session_state.get("user_role", "admin")

    # Initialisation de la page active dans la session pour éviter les pertes de focus
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Accueil"

    # --- BARRE LATÉRALE : MENU NATIF ULTRA-STABLE ---
    with st.sidebar:
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

        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        mois = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
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
            st.markdown("<p style='color: #94A3B8; font-weight: bold; font-size: 0.85rem;'>NAVIGATION</p>", unsafe_allow_html=True)
            pages_admin = [
                "Accueil", "Année scolaire", "Classes & Tarifs", "Matières & Coeffs", "Enseignants", 
                "Personnels et rôles", "Gestion Comptes", "Inscription Élèves", 
                "Import Photos en Masse", "Cartes Scolaires", "Espace Profs", 
                "Consultations des notes", "Conseil de classe", "Bulletins", 
                "Supervision cahier", "Import Programmes PDF", "Suivi des Programmes", 
                "Emploi du temps", "Planification des évaluations", "Encaissement", 
                "Stats Encaissements", "Soldes & Impayés", "Tableau Finances", "Dépenses", "Rapports", 
                "Journal d'activité", "Messages", "Espace Parent", "Tableau de bord", "Alerte Pédagogique", "Sauvegarde & BD"
            ]
            
            # Menu déroulant natif ultra-rapide et indéfectible dans la sidebar
            page = st.selectbox("Sélectionner une rubrique", pages_admin, key="selectbox_admin_nav", label_visibility="collapsed")
            st.session_state["current_page"] = page

        elif role == "parent":
            st.markdown("<p style='color: #10B981; font-weight: bold; font-size: 0.85rem;'>ESPACE PARENT</p>", unsafe_allow_html=True)
            page = st.selectbox("Menu Parent", ["Mon Enfant"], key="selectbox_parent_nav", label_visibility="collapsed")
            st.session_state["current_page"] = page

        elif role == "prof":
            st.markdown("<p style='color: #F59E0B; font-weight: bold; font-size: 0.85rem;'>ESPACE PROF</p>", unsafe_allow_html=True)
            page = st.selectbox("Menu Prof", ["Saisie de notes", "Présence", "Cahier de texte"], key="selectbox_prof_nav", label_visibility="collapsed")
            st.session_state["current_page"] = page
        else:
            page = "Accueil"

        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state["authenticated"] = False
            st.query_params.clear() 
            st.rerun()

    page = st.session_state["current_page"]

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

    niveau_actif = st.selectbox("🎯 Cycle Actif :", ["Primaire", "Collège", "Lycée"], index=1)
    if role == "admin":
        st.markdown("---")

    # --- ROUTAGE DES VUES ---
    if role == "admin":
        if page == "Accueil":
            from views.accueil import afficher_accueil
            afficher_accueil()
        elif page == "Année scolaire":
            from views.annee_scolaire import afficher_annee_scolaire
            afficher_annee_scolaire()
        elif page == "Classes & Tarifs":
            from views.classes import afficher_classes
            afficher_classes(niveau_actif)
        elif page == "Matières & Coeffs":
            from views.matieres import afficher_matieres
            afficher_matieres()
        elif page == "Enseignants":
            from views.enseignants import afficher_enseignants
            afficher_enseignants()
        elif page == "Personnels et rôles":
            from views.personnels_roles import afficher_personnels
            afficher_personnels(niveau_actif)
        elif page == "Gestion Comptes":
            from views.gestion_utilisateurs import afficher_gestion_utilisateurs
            afficher_gestion_utilisateurs()
        elif page == "Inscription Élèves":
            from views.eleves import afficher_eleves
            afficher_eleves(niveau_actif)
        elif page == "Import Photos en Masse":
            from views.photos_masse import afficher_import_photos_masse
            afficher_import_photos_masse(niveau_actif)
        elif page == "Cartes Scolaires":
            from views.cartes_scolaires import afficher_cartes_scolaires
            afficher_cartes_scolaires(niveau_actif)
        elif page == "Espace Profs":
            st.subheader("👨‍🏫 Espace Enseignants (Supervision Admin)")
            tab_p1, tab_p2, tab_p3 = st.tabs(["Saisie de notes", "Présence", "Cahier de texte"])
            with tab_p1:
                from views.notes import afficher_notes
                afficher_notes(niveau_actif)
            with tab_p2:
                from views.presence import afficher_presence
                afficher_presence()
            with tab_p3:
                from views.cahier_texte import afficher_cahier_texte
                afficher_cahier_texte(niveau_actif)
        elif page == "Consultations des notes":
            from views.consultation_notes import afficher_consultation_notes
            afficher_consultation_notes(niveau_actif)
        elif page == "Conseil de classe":
            from views.conseil_classe import afficher_conseil_classe
            afficher_conseil_classe(niveau_actif)
        elif page == "Bulletins":
            from views.bulletins import afficher_bulletins
            afficher_bulletins(niveau_actif)
        elif page == "Supervision cahier":
            from views.supervision_cahier import afficher_supervision_cahier
            afficher_supervision_cahier(niveau_actif)
        elif page == "Import Programmes PDF":
            from views.upload_programmes import afficher_upload_programmes
            afficher_upload_programmes(niveau_actif)
        elif page == "Suivi des Programmes":
            from views.supervision_progression import afficher_supervision_progression
            afficher_supervision_progression(niveau_actif)
        elif page == "Emploi du temps":
            from views.emploi_du_temps import afficher_emploi_du_temps
            afficher_emploi_du_temps(niveau_actif)
        elif page == "Planification des évaluations":
            from views.planification import afficher_planification
            afficher_planification(niveau_actif)
        elif page == "Encaissement":
            from views.finances import afficher_finances
            afficher_finances(niveau_actif)
        elif page == "Stats Encaissements":
            from views.stats_encaissements import afficher_stats_encaissements
            afficher_stats_encaissements(niveau_actif)
        elif page == "Soldes & Impayés":
            from views.soldes_impayes import afficher_soldes_impayes
            afficher_soldes_impayes(niveau_actif)
        elif page == "Tableau Finances":
            from views.tableau_finances import afficher_tableau_finances
            afficher_tableau_finances(niveau_actif)
        elif page == "Dépenses":
            from views.depenses import afficher_depenses
            afficher_depenses(niveau_actif)
        elif page == "Rapports":
            from views.rapports import afficher_rapports
            afficher_rapports(niveau_actif)
        elif page == "Journal d'activité":
            from views.journal_activite import afficher_journal_activite
            afficher_journal_activite(niveau_actif)
        elif page == "Messages":
            from views.messages import afficher_messages
            afficher_messages(niveau_actif)
        elif page == "Espace Parent":
            from views.parent_space import afficher_espace_parent
            afficher_espace_parent()
        elif page == "Tableau de bord":
            from views.tableau_de_bord import afficher_tableau_bord
            afficher_tableau_bord(niveau_actif)
        elif page == "Alerte Pédagogique":
            from views.alerte_performance import afficher_alerte_performance
            afficher_alerte_performance(niveau_actif)
        elif page == "Sauvegarde & BD":
            from views.backup import afficher_backup
            afficher_backup()

    elif role == "parent":
        if page == "Mon Enfant":
            from views.parent_space import afficher_espace_parent
            afficher_espace_parent()

    elif role == "prof":
        if page == "Saisie de notes":
            from views.notes import afficher_notes
            afficher_notes(niveau_actif)
        elif page == "Présence":
            from views.presence import afficher_presence
            afficher_presence()
        elif page == "Cahier de texte":
            from views.cahier_texte import afficher_cahier_texte
            afficher_cahier_texte(niveau_actif)

    db.close()


if __name__ == "__main__":
    main()