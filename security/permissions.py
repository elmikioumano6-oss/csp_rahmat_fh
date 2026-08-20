import streamlit as st

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
    """Vérifie silencieusement si l'utilisateur possède l'accès"""
    user_role = get_user_role()
    if not user_role:
        return False
    return user_role in ACCESS_MATRIX.get(module_name, [])

def require_access(module_name: str):
    """Bloque fermement l'exécution de la page si l'accès est refusé"""
    if not has_access(module_name):
        st.error(f"⛔ ACCÈS REFUSÉ : Votre rôle '{get_user_role()}' ne vous autorise pas à accéder au module '{module_name}'.")
        st.stop()
