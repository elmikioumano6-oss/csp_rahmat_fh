import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Classe, Matiere, Programme

def afficher_upload_programmes(niveau_actif):
    st.subheader(f"🚀 Importation Massive des Programmes - {niveau_actif}")
    db = SessionLocal()

    # --- 1. GÉNÉRATION DU MODÈLE EXCEL ---
    st.markdown("### 📥 Étape 1 : Télécharger le modèle")
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    matieres = db.query(Matiere).all()

    if not classes or not matieres:
        st.warning("⚠️ Configurez d'abord vos classes et matières.")
        db.close()
        return

    # Création d'un dataframe vide pour le modèle
    df_template = pd.DataFrame(columns=["Classe", "Matière", "Semestre", "Volume Horaire"])
    # Pré-remplissage pour aider l'utilisateur
    data_exemple = []
    for c in classes:
        for m in matieres:
            data_exemple.append([c.nom, m.nom, 1, 30])
    df_template = pd.DataFrame(data_exemple, columns=["Classe", "Matière", "Semestre", "Volume Horaire"])

    st.download_button(
        label="📥 Télécharger le modèle Excel (à remplir)",
        data=df_template.to_csv(index=False).encode('utf-8'),
        file_name="modele_programmes.csv",
        mime="text/csv"
    )

    # --- 2. UPLOAD ET TRAITEMENT MASSATIF ---
    st.markdown("---")
    st.markdown("### 📤 Étape 2 : Importer votre fichier rempli")
    fichier_upload = st.file_uploader("Importer le fichier CSV rempli", type=["csv"])

    if fichier_upload:
        df_import = pd.read_csv(fichier_upload)
        if st.button("Valider et Enregistrer l'Importation"):
            count = 0
            for _, row in df_import.iterrows():
                # Trouver les IDs correspondants
                c = db.query(Classe).filter(Classe.nom == row['Classe']).first()
                m = db.query(Matiere).filter(Matiere.nom == row['Matière']).first()
                
                if c and m:
                    # Enregistrer ou mettre à jour
                    prog = db.query(Programme).filter(
                        Programme.classe_id == c.id,
                        Programme.matiere_id == m.id,
                        Programme.semestre == row['Semestre']
                    ).first()
                    
                    if prog:
                        prog.volume_horaire_prevu = row['Volume Horaire']
                    else:
                        db.add(Programme(
                            classe_id=c.id, matiere_id=m.id, 
                            volume_horaire_prevu=row['Volume Horaire'], 
                            semestre=row['Semestre']
                        ))
                    count += 1
            db.commit()
            st.success(f"✅ {count} entrées de programmes importées avec succès !")

    db.close()