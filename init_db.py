from database.db_config import engine
from database.models import Base

def initialiser_base():
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    # Les migrations SQL (PRAGMA etc.) devraient idéalement être déplacées ici
    # dans une fonction qui ne s'exécute qu'une fois.