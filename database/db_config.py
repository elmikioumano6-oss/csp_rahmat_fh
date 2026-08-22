import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Priorité aux secrets Streamlit (Cloud)
# 2. Sinon, utilisation de la variable d'environnement (Local)
# 3. Sinon, utilisation du hardcoded pour dépannage (Déconseillé en production)
DATABASE_URL = (
    st.secrets.get("DATABASE_URL") or 
    os.getenv("DATABASE_URL") or 
    "postgresql://postgres.fdexnwjlobxzodxsdysq:Rahmatfh2026@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
)

# Création du moteur PostgreSQL avec gestion de pool pour éviter les timeout de connexion
engine = create_engine(
    DATABASE_URL, 
    pool_size=10, 
    max_overflow=20,
    pool_pre_ping=True  # Très important pour PostgreSQL sur le Cloud : vérifie la connexion avant chaque requête
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()