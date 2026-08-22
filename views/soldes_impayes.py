import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Eleve, Classe, EcheancePaiement

@st.cache_data(ttl=300)
def charger_donnees_impayes(niveau_actif):
    db = SessionLocal()
    try:
        # Récupérer les élèves du cycle avec leur classe et leurs paiements
        eleves = db.query(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).all()
        
        data_impayes = []
        
        for eleve in eleves:
            # Calculer le montant total dû pour l'élève (via ses échéances)
            echeances = db.query(EcheancePaiement).filter(EcheancePaiement.eleve_id == eleve.id).all()
            total_du = sum(e.montant_total for e in echeances)
            total_paye = sum(e.montant_paye for e in echeances)
            reste_a_payer = total_du - total_paye
            
            if reste_a_payer > 0:
                data_impayes.append({
                    "Matricule": eleve.matricule,
                    "Nom": eleve.nom,
                    "Prénom": eleve.prenom,
                    "Classe": eleve.classe.nom if eleve.classe else "N/A",
                    "Total Dû (FCFA)": total_du,
                    "Déjà Payé (FCFA)": total_paye,
                    "Reste à Payer (FCFA)": reste_a_payer
                })
        return data_impayes
    finally:
        db.close()

def afficher_soldes_impayes(niveau_actif):
    st.subheader(f"⚠️ Soldes & Impayés - {niveau_actif}")

    # Récupération via les données cachées pour une vitesse maximale
    data_impayes = charger_donnees_impayes(niveau_actif)

    if not data_impayes:
        st.success("✅ Aucun impayé détecté pour ce cycle !")
    else:
        df = pd.DataFrame(data_impayes)
        
        # Formatage pour l'affichage (ajout de séparateurs de milliers)
        df_display = df.copy()
        df_display["Total Dû (FCFA)"] = df_display["Total Dû (FCFA)"].apply(lambda x: f"{x:,.0f}")
        df_display["Déjà Payé (FCFA)"] = df_display["Déjà Payé (FCFA)"].apply(lambda x: f"{x:,.0f}")
        df_display["Reste à Payer (FCFA)"] = df_display["Reste à Payer (FCFA)"].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Calcul et affichage du total global
        total_global_impaye = df["Reste à Payer (FCFA)"].sum()
        st.metric("Total des Impayés du cycle", f"{total_global_impaye:,.0f} FCFA")
        
        # Option d'export CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exporter la liste des impayés (CSV)",
            data=csv,
            file_name=f"impayes_{niveau_actif}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )