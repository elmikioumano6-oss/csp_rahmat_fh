import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. On cherche l'URL de la base distante (depuis Streamlit Secrets ou l'environnement)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Si aucune URL n'est trouvée, on bascule sur SQLite en local (pour le développement)
if not SQLALCHEMY_DATABASE_URL:
    DOSSIER_DB = "database"
    os.makedirs(DOSSIER_DB, exist_ok=True)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DOSSIER_DB}/scolarite.db"

# 3. Configuration du moteur (les arguments diffèrent entre SQLite et PostgreSQL)
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Pour PostgreSQL (Supabase), pas besoin de check_same_thread
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()