import streamlit as st
import pandas as pd
import random
from database.db_config import SessionLocal
from database.models import Classe, Eleve, AnneeScolaire

def afficher_examens(niveau_actif):
    st.subheader(f"📅 Planification des Évaluations et Examens - {niveau_actif}")
    db = SessionLocal()

    # 1. Filtrer les classes en fonction du niveau actif (Primaire, Collège, Lycée)
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()

    if not classes:
        st.warning(f"⚠️ Aucune classe configurée pour le {niveau_actif}.")
        db.close()
        return

    # --- PLANIFICATION ET ANONYMAT ---
    st.markdown("### 📝 Préparation des listes de candidats (Examens blancs / Compositions)")
    
    classe_noms = [c.nom for c in classes]
    classes_selectionnees = st.multiselect(
        "Sélectionner les classes qui participent à l'examen :", 
        classe_noms
    )

    if classes_selectionnees:
        if st.button("Générer la liste et les codes d'anonymat", type="primary"):
            # Récupération des élèves des classes sélectionnées
            classes_ids = [c.id for c in classes if c.nom in classes_selectionnees]
            eleves_candidats = db.query(Eleve).filter(Eleve.classe_id.in_(classes_ids)).all()
            
            if eleves_candidats:
                st.success(f"✅ {len(eleves_candidats)} candidats trouvés pour cet examen.")
                
                donnees = []
                # Génération des données pour le placement et l'anonymat
                for e in eleves_candidats:
                    # Génération d'un code secret d'anonymat unique pour la copie
                    code_anonymat = f"AN-{random.randint(1000, 9999)}"
                    
                    donnees.append({
                        "Matricule": e.matricule,
                        "Nom": e.nom,
                        "Prénom": e.prenom,
                        "Classe": e.classe.nom if e.classe else "N/A",
                        "Code Secret": code_anonymat,
                        "Salle / Place": "" # Espace laissé vide pour être rempli après impression
                    })
                    
                df = pd.DataFrame(donnees)
                
                # Affichage du tableau interactif
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.info("💡 Vous pouvez cliquer sur l'icône de téléchargement en haut à droite du tableau pour exporter cette liste au format CSV, l'imprimer, et organiser vos salles et numéros de table.")
            else:
                st.warning("Aucun élève n'a été trouvé dans les classes sélectionnées.")
                
    db.close()