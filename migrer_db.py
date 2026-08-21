import os
import sqlite3

# Recherche du fichier de base de données SQLite
db_file = None
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".db"):
            db_file = os.path.join(root, file)
            break

if not db_file:
    print("❌ Aucune base de données .db trouvée.")
else:
    print(f"📁 Base trouvée : {db_file}")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Ajout de la colonne parent_id à la table eleves
        cursor.execute("ALTER TABLE eleves ADD COLUMN parent_id INTEGER;")
        conn.commit()
        print(
            "✅ La colonne 'parent_id' a été ajoutée avec succès à la table 'eleves' !"
        )
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ La colonne 'parent_id' existe déjà.")
        else:
            print(f"⚠️ Erreur : {e}")
    finally:
        conn.close()