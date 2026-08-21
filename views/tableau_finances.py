import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Eleve, Classe, EcheancePaiement, PaiementDetail

def afficher_tableau_finances(niveau_actif=None):
    st.subheader(f"📈 Tableau de Bord Financier - {niveau_actif}")
    
    db = SessionLocal()
    
    # Récupérer les classes du cycle actif
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    classe_ids = [c.id for c in classes]
    
    if not classe_ids:
        st.warning(f"⚠️ Aucune classe trouvée pour le cycle {niveau_actif}.")
        db.close()
        return
        
    eleves = db.query(Eleve).filter(Eleve.classe_id.in_(classe_ids)).all()
    eleve_ids = [e.id for e in eleves]
    
    if not eleve_ids:
        st.info(f"Aucun élève inscrit dans le cycle **{niveau_actif}**.")
        db.close()
        return
        
    echeances = db.query(EcheancePaiement).filter(EcheancePaiement.eleve_id.in_(eleve_ids)).all()
    
    # Synchronisation intelligente : si le montant attendu est à 0, on récupère le tarif de la classe
    for e in echeances:
        if (e.montant_total or 0.0) == 0.0 and e.eleve and e.eleve.classe:
            tarif = e.eleve.classe.tarif_scolarite or 0.0
            reduction = e.eleve.montant_reduction or 0.0
            e.montant_total = max(0.0, tarif - reduction)
            db.commit()

    paiements = db.query(PaiementDetail).filter(PaiementDetail.eleve_id.in_(eleve_ids)).all()
    
    total_attendu = sum(e.montant_total or 0.0 for e in echeances)
    total_encaisse = sum(e.montant_paye or 0.0 for e in echeances)
    total_reste = total_attendu - total_encaisse
    
    # Indicateurs clés de performance (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Effectif Suivi", len(eleves))
    col2.metric("Montant Total Attendu", f"{total_attendu:,.0f} FCFA".replace(",", " "))
    col3.metric("Total Encaissé", f"{total_encaisse:,.0f} FCFA".replace(",", " "), delta=f"{round((total_encaisse/total_attendu)*100, 1)}% recouvrés" if total_attendu > 0 else "0%")
    col4.metric("Reste à Recouvrer", f"{total_reste:,.0f} FCFA".replace(",", " "), delta_color="inverse")
    
    st.markdown("---")
    st.write("### 📊 Répartition Financière par Classe")
    
    data_classes = []
    for c in classes:
        c_eleves = [e for e in eleves if e.classe_id == c.id]
        c_eleve_ids = [e.id for e in c_eleves]
        c_ech = [e for e in echeances if e.eleve_id in c_eleve_ids]
        
        c_attendu = sum(e.montant_total or 0.0 for e in c_ech)
        c_paye = sum(e.montant_paye or 0.0 for e in c_ech)
        c_solde = c_attendu - c_paye
        
        data_classes.append({
            "Classe": c.nom,
            "Effectif": len(c_eleves),
            "Tarif Unitaire (FCFA)": f"{c.tarif_scolarite:,.0f}".replace(",", " "),
            "Attendu (FCFA)": f"{c_attendu:,.0f}".replace(",", " "),
            "Encaissé (FCFA)": f"{c_paye:,.0f}".replace(",", " "),
            "Reste Dû (FCFA)": f"{c_solde:,.0f}".replace(",", " ")
        })
        
    if data_classes:
        st.dataframe(pd.DataFrame(data_classes), use_container_width=True)
        
    st.markdown("---")
    st.write("### 🕒 Historique des Encaissements du Cycle")
    if paiements:
        data_p = []
        for p in paiements:
            el = db.query(Eleve).filter(Eleve.id == p.eleve_id).first()
            data_p.append({
                "Date": p.date or "N/A",
                "Élève": f"{el.nom} {el.prenom}" if el else "Inconnu",
                "Matricule": el.matricule if el else "N/A",
                "Montant versé (FCFA)": f"{p.montant:,.0f}".replace(",", " "),
                "Mode de paiement": p.mode or "Espèces"
            })
        st.dataframe(pd.DataFrame(data_p), use_container_width=True)
    else:
        st.info("Aucun détail de paiement enregistré pour le moment sur ce cycle.")
        
    db.close()