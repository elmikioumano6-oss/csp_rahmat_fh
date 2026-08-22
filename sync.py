import shutil
import os
import time
from datetime import datetime

def effectuer_sauvegarde_locale(source_db="database/scolarite.db", dossier_backup="sauvegardes_locales"):
    # 1. Vérifier si la base existe
    if not os.path.exists(source_db):
        print(f"Erreur : La base de données {source_db} est introuvable.")
        return

    # 2. Créer le dossier de sauvegarde s'il n'existe pas
    if not os.path.exists(dossier_backup):
        os.makedirs(dossier_backup)
        print(f"Dossier {dossier_backup} créé.")

    # 3. Nommer le fichier avec la date
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nom_fichier = f"csp_rahmat_backup_{timestamp}.db"
    destination = os.path.join(dossier_backup, nom_fichier)

    # 4. Copie sécurisée
    try:
        shutil.copy2(source_db, destination)
        print(f"Succès : Sauvegarde effectuée dans {destination}")
    except Exception as e:
        print(f"Erreur lors de la copie : {e}")

    # 5. Nettoyage : Garder seulement les 10 plus récents
    fichiers = sorted([os.path.join(dossier_backup, f) for f in os.listdir(dossier_backup)], key=os.path.getctime)
    if len(fichiers) > 10:
        for f in fichiers[:-10]:
            os.remove(f)
            print(f"Ancienne sauvegarde supprimée : {f}")

if __name__ == "__main__":
    effectuer_sauvegarde_locale()