import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Eleve, Classe, EcheancePaiement, PaiementDetail, LogActivite

def afficher_finances(niveau_actif=None):
    st.subheader(f"💰 Gestion des Encaissements et Scolarité - {niveau_actif}")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'ENCAISSEMENT ---
    with st.form("form_encaissement"):
        st.write("### Enregistrer un paiement")
        
        # Récupérer les élèves du cycle actif
        eleves = db.query(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).all()
        if not eleves:
            st.warning(f"⚠️ Aucun élève trouvé pour le cycle {niveau_actif}.")
            db.close()
            return
            
        options_eleves = {f"{e.matricule} - {e.nom} {e.prenom} ({e.classe.nom if e.classe else 'Sans classe'})": e.id for e in eleves}
        choix_eleve_label = st.selectbox("Sélectionner l'élève", list(options_eleves.keys()))
        
        montant_verse = st.number_input("Montant versé (FCFA)", min_value=0.0, step=1000.0)
        mode_paiement = st.selectbox("Mode de paiement", ["Espèces", "Virement", "Orange Money / Moov Money", "Chèque"])
        date_paiement = st.date_input("Date du paiement", value=datetime.today())
        
        submitted = st.form_submit_button("Valider l'encaissement")
        
        if submitted:
            if montant_verse > 0:
                eleve_id = options_eleves[choix_eleve_label]
                eleve_obj = db.query(Eleve).filter(Eleve.id == eleve_id).first()
                
                # Vérifier ou créer l'échéance de scolarité pour l'élève
                echeance = db.query(EcheancePaiement).filter(EcheancePaiement.eleve_id == eleve_id).first()
                if not echeance and eleve_obj.classe:
                    tarif = eleve_obj.classe.tarif_scolarite or 0.0
                    reduction = eleve_obj.montant_reduction or 0.0
                    net = max(0.0, tarif - reduction)
                    echeance = EcheancePaiement(
                        eleve_id=eleve_id,
                        libelle="Scolarité",
                        montant=net,
                        montant_total=net,
                        montant_paye=0.0
                    )
                    db.add(echeance)
                    db.commit()
                
                if echeance:
                    echeance.montant_paye = (echeance.montant_paye or 0.0) + montant_verse
                
                # Enregistrer le détail du paiement
                nouveau_paiement = PaiementDetail(
                    echeance_id=echeance.id if echeance else None,
                    eleve_id=eleve_id,
                    montant=montant_verse,
                    date=date_paiement.strftime("%Y-%m-%d"),
                    mode=mode_paiement
                )
                db.add(nouveau_paiement)
                
                # Traçabilité dans le journal d'activité
                db.add(LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get('user_role', 'Admin'),
                    action="ENCAISSEMENT",
                    details=f"Encaissement de {montant_verse:,.0f} FCFA pour l'élève ID {eleve_id} ({mode_paiement})"
                ))
                
                db.commit()
                st.success("✅ Paiement enregistré avec succès !")
                st.rerun()
            else:
                st.warning("⚠️ Veuillez indiquer un montant valide.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / ANNULATION DES PAIEMENTS ---
    with st.expander("🛠️ Annuler un encaissement erroné"):
        paiements = db.query(PaiementDetail).join(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).order_by(PaiementDetail.id.desc()).all()
        if paiements:
            options_p = {f"Reçu ID {p.id} - {p.eleve.nom} {p.eleve.prenom} | Montant: {p.montant:,.0f} FCFA ({p.date})": p.id for p in paiements}
            choix_p = st.selectbox("Sélectionner le reçu à annuler", list(options_p.keys()))
            
            if st.button("🗑️ Annuler ce paiement et réajuster le solde", type="primary"):
                p_id = options_p[choix_p]
                p_obj = db.query(PaiementDetail).filter(PaiementDetail.id == p_id).first()
                if p_obj:
                    # Réajuster l'échéance
                    if p_obj.echeance_id:
                        ech = db.query(EcheancePaiement).filter(EcheancePaiement.id == p_obj.echeance_id).first()
                        if ech:
                            ech.montant_paye = max(0.0, (ech.montant_paye or 0.0) - p_obj.montant)
                    
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="ANNULATION PAIEMENT",
                        details=f"Annulation du reçu ID {p_obj.id} ({p_obj.montant} FCFA) - Élève ID {p_obj.eleve_id}"
                    ))
                    
                    db.delete(p_obj)
                    db.commit()
                    st.success("✅ Paiement annulé, solde réajusté et action tracée avec succès !")
                    st.rerun()
        else:
            st.info("Aucun encaissement à annuler pour ce cycle.")

    st.markdown("---")
    
    # --- HISTORIQUE DES ENCAISSEMENTS ---
    st.write(f"### 📋 Historique des encaissements - {niveau_actif}")
    if paiements:
        data = [{
            "Reçu ID": p.id,
            "Date": p.date,
            "Matricule": p.eleve.matricule if p.eleve else "N/A",
            "Élève": f"{p.eleve.nom} {p.eleve.prenom}" if p.eleve else "N/A",
            "Montant (FCFA)": f"{p.montant:,.0f}".replace(",", " "),
            "Mode": p.mode or "Espèces"
        } for p in paiements]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun encaissement enregistré pour ce cycle.")
        
    db.close()