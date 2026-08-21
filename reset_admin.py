import bcrypt
from database.db_config import SessionLocal
from database.models import User

def reset_admin_securise():
    db = SessionLocal()
    
    # Supprimer l'ancien admin s'il existe
    ancien_admin = db.query(User).filter(User.username == "admin").first()
    if ancien_admin:
        db.delete(ancien_admin)
        db.commit()
    
    # Générer un hachage sécurisé du mot de passe "password123"
    password_en_clair = "password123"
    sel = bcrypt.gensalt()
    mot_de_passe_hache = bcrypt.hashpw(password_en_clair.encode('utf-8'), sel).decode('utf-8')
    
    # Créer l'utilisateur avec le mot de passe haché
    nouvel_admin = User(
        username="admin",
        password=mot_de_passe_hache,
        role="admin"
    )
    db.add(nouvel_admin)
    db.commit()
    print("Compte administrateur sécurisé (haché) créé avec succès !")
    db.close()

if __name__ == "__main__":
    reset_admin_securise()