import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_config import engine, SessionLocal, Base
from database.models import Utilisateur, AnneeScolaire, ParametreFrais
import hashlib
import secrets
from datetime import date

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}${pwd_hash}"

print("Création des tables dans la base de données...")
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 1. Création de l'Administrateur
if not db.query(Utilisateur).filter(Utilisateur.username == "admin").first():
    print("Création de l'utilisateur admin...")
    admin_user = Utilisateur(
        username="admin",
        password_hash=hash_password("admin123"),
        role="Directeur",
        nom_complet="Directeur Général"
    )
    db.add(admin_user)

# 2. Création de l'Année Scolaire Active
if not db.query(AnneeScolaire).filter(AnneeScolaire.libelle == "2026-2027").first():
    print("Création de l'année scolaire 2026-2027...")
    annee = AnneeScolaire(
        libelle="2026-2027",
        active=True,
        date_debut=date(2026, 10, 1),
        date_fin=date(2027, 6, 30)
    )
    db.add(annee)

# 3. Paramètres par défaut
if not db.query(ParametreFrais).first():
    print("Injection des paramètres de frais...")
    db.add_all([
        ParametreFrais(cle="frais_inscription", valeur=15000),
        ParametreFrais(cle="frais_transport_mensuel", valeur=10000),
        ParametreFrais(cle="frais_cantine_mensuel", valeur=12000)
    ])

db.commit()
db.close()
print("✅ Base de données générée avec succès (csp_rahmat_v2.db) !")