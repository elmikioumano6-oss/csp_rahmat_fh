import streamlit as st
import pandas as pd
from sqlalchemy import text, inspect
from streamlit_option_menu import option_menu
from database.db_config import engine, SessionLocal
from database.models import Base, AnneeScolaire, Classe, Eleve, EcheancePaiement, User
from views.login import afficher_login

# Configuration de la page
st.set_page_config(page_title="CSP RAHMAT-FH - Gestion Scolaire", page_icon="Logo CSP-RAHMAT-FH.png", layout="wide")

# ==========================================
# 1. INITIALISATION ET MIGRATIONS (L'ORDRE EST CRUCIAL)
# ==========================================
Base.metadata.create_all(bind=engine)

def run_migrations():
    with engine.connect() as connection:
        # Migration Users
        try:
            res = connection.execute(text("PRAGMA table_info(users);")).fetchall()
            if "entite_id" not in [row[1] for row in res]:
                connection.execute(text("ALTER TABLE users ADD COLUMN entite_id INTEGER;"))
                connection.commit()
        except: pass
        
        # Migration Notes
        try:
            res = connection.execute(text("PRAGMA table_info(notes);")).fetchall()
            if "semestre" not in [row[1] for row in res]:
                connection.execute(text("ALTER TABLE notes ADD COLUMN semestre INTEGER DEFAULT 1;"))
                connection.commit()
        except: pass
        
        # ... (Gardez vos autres migrations ici)
        connection.commit()

run_migrations()

# ==========================================
# 2. CRÉATION DES COMPTES PAR DÉFAUT
# ==========================================
def init_comptes():
    db = SessionLocal()
    comptes = [
        {"username": "admin", "password": "Rahmatfh2026", "role": "admin", "entite_id": None},
        {"username": "prof", "password": "prof2026", "role": "prof", "entite_id": 1},
        {"username": "parent", "password": "parent2026", "role": "parent", "entite_id": 1}
    ]
    for data in comptes:
        user = db.query(User).filter(User.username == data["username"]).first()
        if not user:
            db.add(User(**data))
        else:
            user.password = data["password"]
            user.role = data["role"]
            user.entite_id = data["entite_id"]
    db.commit()
    db.close()

init_comptes()

# ==========================================
# 3. SÉCURITÉ ET VUES
# ==========================================
# (Votre code CSS et imports de views reste identique à avant)
# [...] 
# (Remettez ici le code CSS et les imports des views comme dans votre fichier précédent)

# Le reste de votre main() reste identique à votre version précédente
