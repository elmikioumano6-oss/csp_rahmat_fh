import streamlit as st
from database.db_config import SessionLocal
from database.models import Eleve, PaiementDetail, Classe, Presence
from sqlalchemy import func

def afficher_tableau_bord(niveau_actif):
    st.subheader(f"📊 Tableau de Bord - {niveau_actif}")
    db = SessionLocal()

    col1, col2, col3, col4 = st.columns(4)

    total_eleves = db.query(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).count()
    col1.metric("Total Élèves", total_eleves)

    total_encaisse = db.query(func.sum(PaiementDetail.montant)).scalar() or 0
    col2.metric("Total Recettes", f"{total_encaisse:,.0f} FCFA")

    absents = db.query(Presence).filter(Presence.statut == "Absent").count()
    col3.metric("Absents du jour", absents)
    
    nb_classes = db.query(Classe).filter(Classe.cycle == niveau_actif).count()
    col4.metric("Classes", nb_classes)

    st.markdown("---")
    st.markdown("### Répartition des effectifs")
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    data = {c.nom: len(c.eleves) for c in classes}
    if data:
        st.bar_chart(data)
    else:
        st.info("Aucune classe enregistrée pour ce cycle.")

    db.close()