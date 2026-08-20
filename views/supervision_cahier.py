import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import CahierTexte, Classe, Enseignant, Matiere

def afficher_supervision_cahier(niveau_actif):
    st.subheader(f"👁️ Supervision des Cahiers de Texte - {niveau_actif}")
    db = SessionLocal()

    # Correction du filtre SQLAlchemy : on utilise Classe.cycle
    entrees = db.query(CahierTexte).join(CahierTexte.classe).filter(Classe.cycle == niveau_actif).all()

    if not entrees:
        st.info(f"Aucune entrée de cahier de texte trouvée pour le cycle **{niveau_actif}**.")
        db.close()
        return

    data = []
    for e in entrees:
        classe_nom = e.classe.nom if e.classe else "N/A"
        matiere_nom = e.matiere.nom if e.matiere else "N/A"
        enseignant_nom = f"{e.enseignant.nom} {e.enseignant.prenom}" if e.enseignant else "N/A"
        
        data.append({
            "Date": e.date,
            "Classe": classe_nom,
            "Matière": matiere_nom,
            "Enseignant": enseignant_nom,
            "Contenu": e.contenu
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    db.close()