import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Détecter si l'application tourne sur Streamlit Cloud
is_cloud = os.path.exists("/mount/src")

if is_cloud:
    # Sur Streamlit Cloud, le système de fichiers est en lecture seule. On utilise /tmp/
    DOSSIER_DB = "/tmp"
else:
    # En local sur votre PC, on utilise le dossier 'database' classique
    DOSSIER_DB = "database"
    os.makedirs(DOSSIER_DB, exist_ok=True)

# Chemin vers le fichier de base de données SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DOSSIER_DB}/scolarite.db"

# Création du moteur SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()