import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Utilisation directe de votre base PostgreSQL Supabase
DATABASE_URL = "postgresql://postgres.fdexnwjlobxzodxsdysq:Rahmatfh2026@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

# Création du moteur PostgreSQL optimisé
engine = create_engine(
    DATABASE_URL, 
    pool_size=10, 
    max_overflow=20,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()