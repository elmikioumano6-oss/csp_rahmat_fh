import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import PaiementDetail, Eleve, Classe

def afficher_stats_encaissements(niveau_actif):
    st.subheader(f"📊 Statistiques des Encaissements - {niveau_actif}")
    db = SessionLocal()

    # Récupération des paiements joints aux élèves et classes
    data = db.query(PaiementDetail, Eleve, Classe).\
        join(Eleve, PaiementDetail.eleve_id == Eleve.id).\
        join(Classe, Eleve.classe_id == Classe.id).\
        filter(Classe.cycle == niveau_actif).all()

    if not data:
        st.warning("Aucune donnée de paiement disponible pour ce cycle.")
        db.close()
        return

    # Conversion en DataFrame
    records = []
    for p, e, c in data:
        records.append({
            "Date": p.date,
            "Élève": f"{e.nom} {e.prenom}",
            "Classe": c.libelle,
            "Montant": p.montant,
            "Mode": p.mode
        })
    df = pd.DataFrame(records)
    df['Date'] = pd.to_datetime(df['Date'])

    # Métriques globales
    total_encaisse = df['Montant'].sum()
    st.metric("Total Encaissé", f"{total_encaisse:,.0f} FCFA")

    # Graphique par mode de paiement
    col1, col2 = st.columns(2)
    with col1:
        st.write("Répartition par mode de paiement")
        mode_stats = df.groupby('Mode')['Montant'].sum()
        st.bar_chart(mode_stats)
    
    with col2:
        st.write("Évolution mensuelle")
        mensuel = df.groupby(df['Date'].dt.to_period('M'))['Montant'].sum()
        st.line_chart(mensuel)

    # Tableau détaillé
    st.write("Détails des transactions")
    st.dataframe(df.sort_values(by="Date", ascending=False))

    db.close()