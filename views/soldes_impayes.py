import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Eleve, Classe, EcheancePaiement, PaiementDetail

def afficher_soldes_impayes(niveau_actif):
    st.subheader(f"⚠️ Soldes & Impayés - {niveau_actif}")
    db = SessionLocal()

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
                "Classe": eleve.classe.nom,
                "Total Dû (FCFA)": total_du,
                "Déjà Payé (FCFA)": total_paye,
                "Reste à Payer (FCFA)": reste_a_payer
            })

    if not data_impayes:
        st.success("Aucun impayé détecté pour ce cycle !")
    else:
        df = pd.DataFrame(data_impayes)
        st.dataframe(df, use_container_width=True)
        
        total_global_impaye = df["Reste à Payer (FCFA)"].sum()
        st.metric("Total des Impayés du cycle", f"{total_global_impaye:,.0f} FCFA")

    db.close()