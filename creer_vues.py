import os

bureau = os.path.join(os.path.expanduser("~"), "Desktop")
dossier_projet = os.path.join(bureau, "csp_rahmat_fh")
dossier_views = os.path.join(dossier_projet, "views")

os.makedirs(dossier_views, exist_ok=True)
open(os.path.join(dossier_views, "__init__.py"), 'a').close() # Fichier init pour Python

# ==========================================
# 1. VUE PARAMÈTRES (Années, Classes, Users)
# ==========================================
parametres_content = """import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import AnneeScolaire, Classe, Utilisateur, hash_password
from config import Config

def afficher_parametres():
    st.markdown("<div class='page-title-orange'>Paramètres de l'Établissement</div>", unsafe_allow_html=True)
    tab_annees, tab_classes, tab_users = st.tabs(["📅 Années Scolaires", "🏫 Classes", "🛡️ Utilisateurs"])
    
    db = SessionLocal()
    try:
        # --- ONGLET ANNÉES SCOLAIRES ---
        with tab_annees:
            st.subheader("Gestion des Années Scolaires")
            with st.form("form_annee", clear_on_submit=True):
                col1, col2 = st.columns(2)
                libelle = col1.text_input("Libellé (ex: 2026-2027)")
                active = col2.checkbox("Définir comme année active")
                if st.form_submit_button("Ajouter l'année"):
                    if libelle:
                        if active:
                            db.query(AnneeScolaire).update({"active": False}) # Désactive les autres
                        nouvelle_annee = AnneeScolaire(libelle=libelle, active=active)
                        db.add(nouvelle_annee)
                        db.commit()
                        st.success(f"Année {libelle} ajoutée !")
                        st.rerun()
            
            annees = db.query(AnneeScolaire).all()
            if annees:
                df_a = pd.DataFrame([{"ID": a.id, "Année": a.libelle, "Statut": "🟢 ACTIVE" if a.active else "⚫ Clôturée"} for a in annees])
                st.dataframe(df_a, use_container_width=True, hide_index=True)

        # --- ONGLET CLASSES ---
        with tab_classes:
            st.subheader("Gestion des Classes")
            with st.form("form_classe", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                lib_classe = col1.text_input("Nom (ex: 6ème A)")
                cycle = col2.selectbox("Cycle", ["Primaire", "Collège", "Lycée"])
                frais = col3.number_input("Frais Scolarité", min_value=0, step=5000)
                if st.form_submit_button("Créer la classe"):
                    if lib_classe:
                        cls = Classe(libelle=lib_classe, cycle=cycle, frais_scolarite=frais)
                        db.add(cls)
                        db.commit()
                        st.success(f"Classe {lib_classe} créée !")
                        st.rerun()
            
            classes = db.query(Classe).all()
            if classes:
                df_c = pd.DataFrame([{"Classe": c.libelle, "Cycle": c.cycle, "Frais (FCFA)": c.frais_scolarite} for c in classes])
                st.dataframe(df_c, use_container_width=True, hide_index=True)
                
        # --- ONGLET UTILISATEURS ---
        with tab_users:
            st.subheader("Comptes d'accès")
            users = db.query(Utilisateur).all()
            df_u = pd.DataFrame([{"Identifiant": u.username, "Nom": u.nom_complet, "Rôle": u.role, "Actif": u.actif} for u in users])
            st.dataframe(df_u, use_container_width=True, hide_index=True)
            
    finally:
        db.close()
"""

# ==========================================
# 2. VUE SCOLARITÉ (Élèves & Inscriptions)
# ==========================================
scolarite_content = """import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Eleve, Inscription, Classe, AnneeScolaire

def afficher_scolarite(cycle_actif):
    st.markdown(f"<div class='page-title-orange'>Scolarité - {cycle_actif}</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        # Vérification de l'année active
        annee_active = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
        if not annee_active:
            st.error("⛔ Aucune année scolaire n'est définie comme active. Allez dans Administration > Paramètres.")
            return

        st.info(f"📅 Année scolaire en cours : **{annee_active.libelle}**")
        tab_liste, tab_insc = st.tabs(["📋 Élèves Inscrits", "➕ Nouvelle Inscription"])

        # --- ONGLET LISTE ---
        with tab_liste:
            # Jointure ORM stricte : Inscription -> Eleve & Classe
            inscriptions = db.query(Inscription, Eleve, Classe).join(Eleve).join(Classe).filter(
                Inscription.annee_id == annee_active.id,
                Classe.cycle == cycle_actif
            ).all()
            
            if inscriptions:
                data = []
                for insc, elv, cls in inscriptions:
                    data.append({
                        "Matricule": elv.matricule,
                        "Nom & Prénom": f"{elv.nom} {elv.prenom}",
                        "Sexe": elv.sexe,
                        "Classe": cls.libelle,
                        "Statut": insc.statut
                    })
                df = pd.DataFrame(data)
                
                recherche = st.text_input("🔍 Rechercher un élève...")
                if recherche:
                    mask = df.apply(lambda row: row.astype(str).str.contains(recherche, case=False).any(), axis=1)
                    st.dataframe(df[mask], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun élève inscrit dans ce cycle pour l'année en cours.")

        # --- ONGLET INSCRIPTION ---
        with tab_insc:
            classes_dispo = db.query(Classe).filter(Classe.cycle == cycle_actif).all()
            if not classes_dispo:
                st.warning("⚠️ Créez d'abord des classes pour ce cycle dans les paramètres.")
            else:
                dict_classes = {c.libelle: c.id for c in classes_dispo}
                with st.form("form_nouvel_eleve", clear_on_submit=True):
                    st.subheader("Dossier de l'élève")
                    c1, c2, c3 = st.columns(3)
                    matricule = c1.text_input("Matricule*")
                    nom = c2.text_input("Nom*")
                    prenom = c3.text_input("Prénom*")
                    
                    c4, c5, c6 = st.columns(3)
                    sexe = c4.radio("Sexe*", ["G", "F"], horizontal=True)
                    contact = c5.text_input("Contact Parent")
                    classe_sel = c6.selectbox("Classe d'affectation*", list(dict_classes.keys()))
                    
                    if st.form_submit_button("✅ Enregistrer l'inscription"):
                        if matricule and nom and prenom:
                            try:
                                # 1. Création de l'Élève physique
                                nouvel_eleve = Eleve(matricule=matricule, nom=nom, prenom=prenom, sexe=sexe, contact_parent=contact)
                                db.add(nouvel_eleve)
                                db.flush() # Récupère l'ID de l'élève avant le commit final
                                
                                # 2. Création de l'Inscription pour l'année active
                                nouvelle_insc = Inscription(
                                    eleve_id=nouvel_eleve.id,
                                    annee_id=annee_active.id,
                                    classe_id=dict_classes[classe_sel],
                                    statut="Actif"
                                )
                                db.add(nouvelle_insc)
                                db.commit()
                                st.success(f"Succès : {nom} {prenom} inscrit(e) en {classe_sel} !")
                                st.rerun()
                            except Exception as e:
                                db.rollback()
                                st.error("Erreur : Ce matricule existe peut-être déjà.")
                        else:
                            st.error("Veuillez remplir les champs obligatoires (*)")
    finally:
        db.close()
"""

# ==========================================
# 3. LE NOUVEAU MAIN.PY (Allégé)
# ==========================================
main_content = """import streamlit as st
from config import Config
from database.db_config import SessionLocal
from security.auth import authenticate_user, login_user, logout_user
from security.permissions import has_access, require_access

# Importation des Vues modulaires
from views.parametres import afficher_parametres
from views.scolarite import afficher_scolarite

st.set_page_config(page_title=Config.APP_NAME, page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown(\"\"\"
<style>
    .stApp { background-color: #F4F7F6; }
    [data-testid="stSidebar"] { background-color: #1e293b !important; }
    .page-title-orange { border-left: 4px solid #f97316; padding-left: 12px; color: #17253b; font-size: 24px; font-weight: 800; margin-bottom: 25px; }
    .login-container { max-width: 400px; margin: 80px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; border-top: 5px solid #f97316;}
</style>
\"\"\", unsafe_allow_html=True)

# --- AUTHENTIFICATION ---
if not st.session_state.get('authenticated', False) or 'role' not in st.session_state:
    st.session_state.authenticated = False 
    st.markdown(f'<div class="login-container"><div style="font-size:40px;">🎓</div><div style="font-size:24px; font-weight:bold; color:#1e293b;">{Config.APP_NAME}</div></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            user_input = st.text_input("Identifiant")
            pwd_input = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Connexion sécurisée", use_container_width=True):
                db = SessionLocal()
                try:
                    user = authenticate_user(db, user_input, pwd_input)
                    if user:
                        login_user(user)
                        st.rerun()
                    else: st.error("Identifiants incorrects.")
                finally: db.close()
    st.stop()

# --- MENU DYNAMIQUE ---
nom_user = st.session_state.get('nom_complet', '')
with st.sidebar:
    st.markdown(f"<div style='color:white; font-size:20px; font-weight:800; text-align:center;'>🎓 {Config.APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:rgba(255,255,255,0.1); color:#fff; padding:5px; border-radius:6px; font-size:12px; text-align:center; margin: 10px 0;'>👤 {nom_user}</div>", unsafe_allow_html=True)
    
    options_disponibles = []
    st.markdown("### 📚 SCOLARITÉ & PÉDAGOGIE")
    for opt in ["Élèves", "Classes", "Enseignants", "Notes & Bulletins", "Suivi Progressions"]:
        if has_access(opt): options_disponibles.append(opt)
    
    st.markdown("### ⚙️ ADMINISTRATION")
    for opt in ["Paramètres de l'école", "Utilisateurs"]:
        if has_access(opt): options_disponibles.append(opt)
        
    options_disponibles.append("Mon Profil")
    
    if "nav_module" not in st.session_state or st.session_state.nav_module not in options_disponibles:
        st.session_state.nav_module = options_disponibles[0] if options_disponibles else "Mon Profil"

    selection = st.radio("Navigation", options_disponibles, index=options_disponibles.index(st.session_state.nav_module), label_visibility="collapsed")
    st.session_state.nav_module = selection
    if st.button("🚪 Déconnexion", use_container_width=True): 
        logout_user()
        st.rerun()

# --- EN-TÊTE ---
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1: st.markdown(f"**<span style='color: #d97706;'>▌</span> {Config.ECOLE_NOM}**", unsafe_allow_html=True)
with c2: st.session_state.semestre_actif = st.selectbox("Semestre", ["1er Semestre", "2ème Semestre"], label_visibility="collapsed")
with c3: cycle_choisi = st.selectbox("Cycle", ["🏫 Collège", "🎒 Primaire", "🎓 Lycée"], label_visibility="collapsed")
st.markdown("---")

module_actif = st.session_state.nav_module
cycle_str = cycle_choisi.replace("🏫 ", "").replace("🎒 ", "").replace("🎓 ", "").strip()

# --- ROUTEUR DE VUES ---
if module_actif == "Paramètres de l'école":
    require_access("Paramètres de l'école")
    afficher_parametres()
    
elif module_actif == "Élèves":
    require_access("Élèves")
    afficher_scolarite(cycle_str)

elif module_actif == "Mon Profil":
    st.markdown("<div class='page-title-orange'>Mon profil</div>", unsafe_allow_html=True)
    st.write(f"Rôle : **{st.session_state.get('role')}**")
    
else:
    st.info(f"Le module **{module_actif}** est en cours d'intégration dans la nouvelle architecture MVC.")
"""

# Écriture des fichiers
with open(os.path.join(dossier_views, "parametres.py"), "w", encoding="utf-8") as f: f.write(parametres_content)
with open(os.path.join(dossier_views, "scolarite.py"), "w", encoding="utf-8") as f: f.write(scolarite_content)
with open(os.path.join(dossier_projet, "main.py"), "w", encoding="utf-8") as f: f.write(main_content)

print("✅ Les vues (parametres.py, scolarite.py) et le nouveau main.py ont été générés !")