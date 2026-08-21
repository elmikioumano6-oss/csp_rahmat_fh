import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Depense, LogActivite

def afficher_depenses(niveau_actif=None):
    st.subheader(f"💸 Gestion des Dépenses - {niveau_actif}")
    
    db = SessionLocal()
    
    # --- FORMULAIRE DE SAISIE ---
    with st.form("form_depense"):
        st.write("### Enregistrer une nouvelle dépense")
        libelle = st.text_input("Libellé de la dépense")
        montant = st.number_input("Montant (FCFA)", min_value=0.0, step=100.0)
        date_depense = st.date_input("Date de la dépense", value=datetime.today())
        categorie = st.selectbox("Catégorie", ["Fonctionnement", "Maintenance", "Fournitures", "Salaires", "Autre"])
        beneficiaire = st.text_input("Bénéficiaire (Optionnel)")
        
        submitted = st.form_submit_button("Enregistrer la dépense")
        if submitted:
            if libelle.strip() and montant > 0:
                nouvelle_depense = Depense(
                    libelle=libelle,
                    montant=montant,
                    date=date_depense.strftime("%Y-%m-%d"),
                    categorie=categorie,
                    beneficiaire=beneficiaire
                )
                db.add(nouvelle_depense)
                
                # Traçabilité dans le journal d'activité
                db.add(LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get('user_role', 'Admin'),
                    action="SAISIE DÉPENSE",
                    details=f"Ajout dépense '{libelle}' de {montant:,.0f} FCFA"
                ))
                
                db.commit()
                st.success("✅ Dépense enregistrée avec succès !")
                st.rerun()
            else:
                st.warning("⚠️ Veuillez remplir le libellé et indiquer un montant valide.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION SÉCURISÉE ---
    with st.expander("🛠️ Corriger ou supprimer une dépense erronée"):
        depenses = db.query(Depense).order_by(Depense.id.desc()).all()
        if depenses:
            options_d = {f"ID {d.id} - {d.libelle} ({d.montant:,.0f} FCFA du {d.date})": d.id for d in depenses}
            choix_d = st.selectbox("Sélectionner la dépense à supprimer", list(options_d.keys()))
            
            if st.button("🗑️ Supprimer définitivement cette dépense", type="primary"):
                d_id = options_d[choix_d]
                d_obj = db.query(Depense).filter(Depense.id == d_id).first()
                if d_obj:
                    # Enregistrement de l'annulation dans le journal
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION DÉPENSE",
                        details=f"Suppression de la dépense ID {d_obj.id} ({d_obj.libelle} - {d_obj.montant} FCFA)"
                    ))
                    db.delete(d_obj)
                    db.commit()
                    st.success("✅ Dépense supprimée et action tracée avec succès !")
                    st.rerun()
        else:
            st.info("Aucune dépense enregistrée à corriger.")

    st.markdown("---")
    
    # --- HISTORIQUE DES DÉPENSES ---
    st.write("### 📋 Historique des dépenses")
    toutes_depenses = db.query(Depense).order_by(Depense.id.desc()).all()
    if toutes_depenses:
        data = [{
            "ID": d.id,
            "Date": d.date,
            "Libellé": d.libelle,
            "Catégorie": d.categorie,
            "Montant (FCFA)": f"{d.montant:,.0f}".replace(",", " "),
            "Bénéficiaire": d.beneficiaire or "N/A"
        } for d in toutes_depenses]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucune dépense enregistrée pour le moment.")
        
    db.close()