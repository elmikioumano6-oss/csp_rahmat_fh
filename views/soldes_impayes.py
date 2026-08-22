import streamlit as st
import pandas as pd
from sqlalchemy import func
from database.db_config import SessionLocal
from database.models import Eleve, Classe, EcheancePaiement

@st.cache_data(ttl=300)
def charger_donnees_impayes(niveau_actif):
    db = SessionLocal()
    try:
        # 1. Récupérer les IDs des élèves du cycle
        eleves = db.query(Eleve.id, Eleve.matricule, Eleve.nom, Eleve.prenom, Classe.nom.label("classe_nom"))\
                   .join(Classe)\
                   .filter(Classe.cycle == niveau_actif).all()
        
        if not eleves:
            return []

        eleve_ids = [e.id for e in eleves]
        
        # 2. Récupérer toutes les échéances en une seule requête groupée
        echeances = db.query(
            EcheancePaiement.eleve_id,
            func.sum(EcheancePaiement.montant_total).label("total_dû"),
            func.sum(EcheancePaiement.montant_paye).label("total_payé")
        ).filter(EcheancePaiement.eleve_id.in_(eleve_ids)).group_by(EcheancePaiement.eleve_id).all()
        
        # Créer un dictionnaire pour accès rapide
        dict_paiements = {e.eleve_id: {"du": e.total_dû or 0, "paye": e.total_payé or 0} for e in echeances}
        
        data_impayes = []
        for e in eleves:
            paiements = dict_paiements.get(e.id, {"du": 0, "paye": 0})
            reste = paiements["du"] - paiements["paye"]
            
            if reste > 0:
                data_impayes.append({
                    "Matricule": e.matricule,
                    "Nom": e.nom,
                    "Prénom": e.prenom,
                    "Classe": e.classe_nom,
                    "Total Dû (FCFA)": paiements["du"],
                    "Déjà Payé (FCFA)": paiements["paye"],
                    "Reste à Payer (FCFA)": reste
                })
        return data_impayes
    finally:
        db.close()

def afficher_soldes_impayes(niveau_actif):
    st.subheader(f"⚠️ Soldes & Impayés - {niveau_actif}")
    data_impayes = charger_donnees_impayes(niveau_actif)

    if not data_impayes:
        st.success("✅ Aucun impayé détecté pour ce cycle !")
    else:
        df = pd.DataFrame(data_impayes)
        
        # Formatage pour l'affichage
        df_display = df.copy()
        for col in ["Total Dû (FCFA)", "Déjà Payé (FCFA)", "Reste à Payer (FCFA)"]:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        total_global_impaye = df["Reste à Payer (FCFA)"].sum()
        st.metric("Total des Impayés du cycle", f"{total_global_impaye:,.0f} FCFA")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exporter la liste des impayés (CSV)",
            data=csv,
            file_name=f"impayes_{niveau_actif}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )