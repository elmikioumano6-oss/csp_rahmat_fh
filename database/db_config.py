import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# On force l'utilisation de SQLite pour garantir la stabilité immédiate partout
is_cloud = False

if is_cloud:
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:Rahmatfh2026@db.djwhxbencnyussvhejrx.supabase.co:5432/postgres"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    DOSSIER_DB = "database"
    os.makedirs(DOSSIER_DB, exist_ok=True)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DOSSIER_DB}/scolarite.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()