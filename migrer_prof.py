import os
import sqlite3

db_file = None
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".db"):
            db_file = os.path.join(root, file)
            break

if db_file:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 1. Ajout de la liaison User -> Enseignant
    try:
        cursor.execute("ALTER TABLE enseignants ADD COLUMN user_id INTEGER;")
        print("✅ Colonne 'user_id' ajoutée aux enseignants.")
    except Exception as e:
        print("ℹ️ Colonne 'user_id' déjà existante.")

    # 2. Création de la table des affectations
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS affectations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enseignant_id INTEGER,
            classe_id INTEGER,
            matiere_id INTEGER,
            FOREIGN KEY(enseignant_id) REFERENCES enseignants(id),
            FOREIGN KEY(classe_id) REFERENCES classes(id),
            FOREIGN KEY(matiere_id) REFERENCES matieres(id)
        );
        """)
        print("✅ Table 'affectations' prête.")
    except Exception as e:
        print(f"⚠️ Erreur : {e}")
        
    conn.commit()
    conn.close()