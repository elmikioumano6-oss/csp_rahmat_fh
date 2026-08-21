import os

# Définition du chemin vers le projet csp_rahmat_fh
bureau = os.path.join(os.path.expanduser("~"), "Desktop")
dossier_projet = os.path.join(bureau, "csp_rahmat_fh")
dossier_sec = os.path.join(dossier_projet, "security")

# Création du sous-dossier security
os.makedirs(dossier_sec, exist_ok=True)
print(f"📁 Dossier 'security' vérifié/créé dans : {dossier_projet}")

# --- CONTENU DE auth.py ---
auth_content = """import hashlib
import secrets
import streamlit as st
from datetime import datetime
from database.models import Utilisateur, LogActivite

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}${pwd_hash}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    if '$' not in stored_password:
        return stored_password == provided_password # Rétrocompatibilité
    salt, pwd_hash = stored_password.split('$', 1)
    verify_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return pwd_hash == verify_hash

def authenticate_user(db_session, username, password):
    user = db_session.query(Utilisateur).filter(Utilisateur.username == username, Utilisateur.actif == True).first()
    if user and verify_password(user.password_hash, password):
        # Enregistrement du log de connexion
        log = LogActivite(utilisateur_id=user.id, action="Connexion réussie", module="Authentification")
        db_session.add(log)
        db_session.commit()
        return user
    return None

def login_user(user):
    st.session_state.authenticated = True
    st.session_state.user_id = user.id
    st.session_state.username = user.username
    st.session_state.role = user.role
    st.session_state.nom_complet = user.nom_complet

def logout_user():
    for key in ['authenticated', 'user_id', 'username', 'role', 'nom_complet', 'active_rail', 'nav_module']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.authenticated = False
"""

# --- CONTENU DE permissions.py ---
permissions_content = """import streamlit as st

# Constantes des rôles
ROLE_DIRECTEUR = "Directeur"
ROLE_CENSEUR = "Censeur"
ROLE_CAISSIER = "Caissier"
ROLE_PROFESSEUR = "Professeur"

# MATRICE D'ACCÈS RBAC (Role-Based Access Control)
ACCESS_MATRIX = {
    # Administration
    "Paramètres de l'école": [ROLE_DIRECTEUR],
    "Utilisateurs": [ROLE_DIRECTEUR],
    "Journal d'activité": [ROLE_DIRECTEUR],
    
    # Scolarité
    "Élèves": [ROLE_DIRECTEUR, ROLE_CENSEUR],
    "Classes": [ROLE_DIRECTEUR, ROLE_CENSEUR],
    
    # Pédagogie
    "Notes & Bulletins": [ROLE_DIRECTEUR, ROLE_CENSEUR, ROLE_PROFESSEUR],
    "Enseignants": [ROLE_DIRECTEUR, ROLE_CENSEUR],
    "Suivi Progressions": [ROLE_DIRECTEUR, ROLE_CENSEUR, ROLE_PROFESSEUR],
    
    # Examens
    "Examens & Anonymat": [ROLE_DIRECTEUR, ROLE_CENSEUR],
    
    # Finances
    "Encaissements": [ROLE_DIRECTEUR, ROLE_CAISSIER],
    "Soldes & impayés": [ROLE_DIRECTEUR, ROLE_CAISSIER],
    "Dépenses": [ROLE_DIRECTEUR, ROLE_CAISSIER],
    "Rapports Financiers": [ROLE_DIRECTEUR, ROLE_CAISSIER],
    
    # Transverse
    "Tableau de bord": [ROLE_DIRECTEUR, ROLE_CENSEUR, ROLE_CAISSIER],
    "Mon Profil": [ROLE_DIRECTEUR, ROLE_CENSEUR, ROLE_CAISSIER, ROLE_PROFESSEUR]
}

def get_user_role():
    return st.session_state.get("role", None)

def has_access(module_name: str) -> bool:
    \"\"\"Vérifie silencieusement si l'utilisateur possède l'accès\"\"\"
    user_role = get_user_role()
    if not user_role:
        return False
    return user_role in ACCESS_MATRIX.get(module_name, [])

def require_access(module_name: str):
    \"\"\"Bloque fermement l'exécution de la page si l'accès est refusé\"\"\"
    if not has_access(module_name):
        st.error(f"⛔ ACCÈS REFUSÉ : Votre rôle '{get_user_role()}' ne vous autorise pas à accéder au module '{module_name}'.")
        st.stop()
"""

# Écriture des fichiers
with open(os.path.join(dossier_sec, "auth.py"), "w", encoding="utf-8") as f:
    f.write(auth_content)
    
with open(os.path.join(dossier_sec, "permissions.py"), "w", encoding="utf-8") as f:
    f.write(permissions_content)

print("✅ Les modules de sécurité (auth.py et permissions.py) ont été créés avec succès !")