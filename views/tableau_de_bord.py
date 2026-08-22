import streamlit as st
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Eleve, PaiementDetail, Classe, Presence
from sqlalchemy import func

@st.cache_data(ttl=300)
def charger_donnees_tableau_bord(niveau_actif):
    db = SessionLocal()
    try:
        total_eleves = db.query(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).count()
        total_encaisse = db.query(func.sum(PaiementDetail.montant)).scalar() or 0
        
        # Filtrer les absents du jour exact
        date_jour = datetime.today().strftime("%Y-%m-%d")
        absents = db.query(Presence).join(Eleve).join(Classe).filter(
            Classe.cycle == niveau_actif,
            Presence.statut == "Absent",
            Presence.date == date_jour
        ).count()
        
        nb_classes = db.query(Classe).filter(Classe.cycle == niveau_actif).count()
        
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
        data = {c.nom: len(c.eleves) for c in classes}
        
        return {
            "total_eleves": total_eleves,
            "total_encaisse": total_encaisse,
            "absents": absents,
            "nb_classes": nb_classes,
            "data": data
        }
    finally:
        db.close()

def afficher_tableau_bord(niveau_actif):
    st.subheader(f"📊 Tableau de Bord - {niveau_actif}")
    
    # Récupération rapide depuis le cache
    stats = charger_donnees_tableau_bord(niveau_actif)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Élèves", stats["total_eleves"])
    col2.metric("Total Recettes", f"{stats['total_encaisse']:,.0f} FCFA")
    col3.metric("Absents du jour", stats["absents"])
    col4.metric("Classes", stats["nb_classes"])

    st.markdown("---")
    st.markdown("### Répartition des effectifs")
    
    data = stats["data"]
    if data:
        st.bar_chart(data)
    else:
        st.info("Aucune classe enregistrée pour ce cycle.")