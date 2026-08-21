import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Eleve, Classe, EcheancePaiement, Depense

def afficher_rapports(niveau_actif=None):
    st.subheader(f"📊 Rapports et Synthèse Globale - {niveau_actif}")
    
    db = SessionLocal()
    
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    classe_ids = [c.id for c in classes]
    
    if not classe_ids:
        st.warning(f"⚠️ Aucune classe configurée pour le cycle {niveau_actif}.")
        db.close()
        return
        
    eleves = db.query(Eleve).filter(Eleve.classe_id.in_(classe_ids)).all()
    eleve_ids = [e.id for e in eleves]
    
    # 1. Statistiques des effectifs (Logique explicite et sécurisée)
    total_eleves = len(eleves)
    filles = 0
    garcons = 0
    
    for e in eleves:
        val_sexe = str(getattr(e, 'sexe', '') or '').strip().lower()
        
        if val_sexe in ['fille', 'féminin', 'feminin', 'f', 'femme']:
            filles += 1
        elif val_sexe in ['garçon', 'garcon', 'masculin', 'm', 'garc']:
            garcons += 1
        else:
            # Par défaut, si le champ est vide ou non reconnu, on le traite comme un garçon
            garcons += 1
            
    st.write("### 👥 Synthèse des Effectifs")
    col1, col2, col3 = st.columns(3)
    col1.metric("Effectif Total", total_eleves)
    col2.metric("Garçons", garcons)
    col3.metric("Filles", filles)
    
    # Optionnel : Afficher un aperçu des données brutes pour diagnostic si besoin
    with st.expander("🔍 Diagnostic des genres enregistrés en base"):
        diag_data = [{"Nom": f"{e.nom} {e.prenom}", "Valeur Sexe en BD": repr(e.sexe)} for e in eleves]
        st.dataframe(pd.DataFrame(diag_data), use_container_width=True)
    
    st.markdown("---")
    
    # 2. Synthèse financière du cycle
    echeances = db.query(EcheancePaiement).filter(EcheancePaiement.eleve_id.in_(eleve_ids)).all() if eleve_ids else []
    total_attendu = sum(e.montant_total or 0.0 for e in echeances)
    total_encaisse = sum(e.montant_paye or 0.0 for e in echeances)
    total_reste = total_attendu - total_encaisse
    
    st.write("### 💰 Synthèse Financière")
    fcol1, fcol2, fcol3 = st.columns(3)
    fcol1.metric("Total Attendu", f"{total_attendu:,.0f} FCFA".replace(",", " "))
    fcol2.metric("Total Encaissé", f"{total_encaisse:,.0f} FCFA".replace(",", " "))
    fcol3.metric("Reste à Recouvrer", f"{total_reste:,.0f} FCFA".replace(",", " "), delta_color="inverse")
    
    st.markdown("---")
    
    # 3. Synthèse des dépenses globales et trésorerie
    depenses = db.query(Depense).all()
    total_depenses = sum(d.montant or 0.0 for d in depenses)
    st.write("### 💸 Trésorerie & Dépenses")
    dcol1, dcol2 = st.columns(2)
    dcol1.metric("Total Dépenses Globales", f"{total_depenses:,.0f} FCFA".replace(",", " "))
    solde_net = total_encaisse - total_depenses
    dcol2.metric("Solde Net (Encaissements - Dépenses)", f"{solde_net:,.0f} FCFA".replace(",", " "), delta_color="normal")
    
    st.markdown("---")
    
    # 4. Tableau récapitulatif par classe et export
    st.write("### 📋 Tableau Récapitulatif par Classe")
    data_recap = []
    for c in classes:
        c_eleves = [e for e in eleves if e.classe_id == c.id]
        c_ids = [e.id for e in c_eleves]
        c_ech = [e for e in echeances if e.eleve_id in c_ids]
        c_att = sum(e.montant_total or 0.0 for e in c_ech)
        c_pay = sum(e.montant_paye or 0.0 for e in c_ech)
        
        data_recap.append({
            "Classe": c.nom,
            "Effectif": len(c_eleves),
            "Tarif (FCFA)": f"{c.tarif_scolarite:,.0f}".replace(",", " "),
            "Attendu (FCFA)": f"{c_att:,.0f}".replace(",", " "),
            "Encaissé (FCFA)": f"{c_pay:,.0f}".replace(",", " "),
            "Impayé (FCFA)": f"{max(0.0, c_att - c_pay):,.0f}".replace(",", " ")
        })
        
    if data_recap:
        df_recap = pd.DataFrame(data_recap)
        st.dataframe(df_recap, use_container_width=True)
        
        csv = df_recap.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger le rapport global en CSV",
            data=csv,
            file_name=f"rapport_synthese_{niveau_actif.lower()}.csv",
            mime="text/csv",
        )
    else:
        st.info("Aucune donnée de classe disponible pour l'export.")
        
    db.close()