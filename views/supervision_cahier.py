import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import CahierTexte, Classe

def afficher_supervision_cahier(niveau_actif):
    st.subheader(f"👁️ Supervision des Cahiers de Texte - {niveau_actif}")
    db = SessionLocal()

    # --- FILTRES DE SUPERVISION ---
    st.sidebar.markdown("### 🔍 Filtres de recherche")
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    options_classes = {c.nom: c.id for c in classes}
    
    choix_classe = st.sidebar.multiselect("Filtrer par classe(s) :", list(options_classes.keys()), default=list(options_classes.keys()))
    classe_ids = [options_classes[c] for c in choix_classe]
    
    # --- REQUÊTE ---
    query = db.query(CahierTexte).join(CahierTexte.classe).filter(Classe.cycle == niveau_actif)
    
    if classe_ids:
        query = query.filter(CahierTexte.classe_id.in_(classe_ids))
        
    entrees = query.order_by(CahierTexte.date.desc()).all()

    if not entrees:
        st.info(f"Aucune entrée de cahier de texte trouvée pour les critères sélectionnés.")
        db.close()
        return

    # --- AFFICHAGE ---
    data = []
    for e in entrees:
        data.append({
            "Date": e.date,
            "Classe": e.classe.nom if e.classe else "N/A",
            "Matière": e.matiere.nom if e.matiere else "N/A",
            "Enseignant": f"{e.enseignant.nom} {e.enseignant.prenom}" if e.enseignant else "N/A",
            "Contenu": e.contenu
        })

    df = pd.DataFrame(data)
    
    # Affichage du DataFrame
    st.dataframe(df, use_container_width=True)

    # Export CSV pour rapports
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exporter ce rapport (CSV)",
        data=csv,
        file_name=f"Rapport_Cahier_Texte_{niveau_actif}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    db.close()