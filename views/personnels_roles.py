import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Personnel, LogActivite

def afficher_personnels(niveau_actif=None):
    st.subheader(f"🛡️ Gestion du Personnel et des Rôles - {niveau_actif}")
    
    db = SessionLocal()
    try:
        # --- FORMULAIRE D'ENREGISTREMENT ---
        with st.form("form_personnel"):
            st.write("### Enregistrer un membre du personnel")
            
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            fonction = st.text_input("Fonction (ex: Surveillant, Secrétaire, Proviseur)")
            telephone = st.text_input("Téléphone")
            
            submitted = st.form_submit_button("Enregistrer le personnel")
            if submitted:
                if nom.strip() and prenom.strip():
                    try:
                        nouveau_personnel = Personnel(
                            nom=nom,
                            prenom=prenom,
                            fonction=fonction,
                            telephone=telephone
                        )
                        db.add(nouveau_personnel)
                        
                        # Traçabilité dans le journal d'activité
                        db.add(LogActivite(
                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            utilisateur=st.session_state.get('user_role', 'Admin'),
                            action="SAISIE PERSONNEL",
                            details=f"Ajout du personnel {nom} {prenom} ({fonction})"
                        ))
                        
                        db.commit()
                        st.success(f"✅ Le personnel '{nom} {prenom}' a été enregistré avec succès !")
                        db.close()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Erreur lors de l'enregistrement du personnel : {e}")
                else:
                    st.warning("⚠️ Veuillez renseigner au moins le nom et le prénom.")

        st.markdown("---")
        
        # --- LISTE ET SUPPRESSION DU PERSONNEL ---
        st.write("### 📋 Liste du Personnel enregistré")
        personnels = db.query(Personnel).order_by(Personnel.nom).all()
        
        if personnels:
            data = [{
                "ID": p.id,
                "Nom": p.nom,
                "Prénom": p.prenom,
                "Fonction": p.fonction or "Non spécifiée",
                "Téléphone": p.telephone or "Aucun"
            } for p in personnels]
            st.dataframe(pd.DataFrame(data), use_container_width=True)
            
            with st.expander("🛠️ Supprimer un membre du personnel"):
                options_p = {f"ID {p.id} - {p.nom} {p.prenom} ({p.fonction})": p.id for p in personnels}
                choix_p = st.selectbox("Sélectionner le personnel à supprimer", list(options_p.keys()))
                
                if st.button("🗑️ Supprimer ce membre", type="primary"):
                    try:
                        p_id = options_p[choix_p]
                        p_obj = db.query(Personnel).filter(Personnel.id == p_id).first()
                        if p_obj:
                            nom_p = f"{p_obj.nom} {p_obj.prenom}"
                            db.add(LogActivite(
                                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                utilisateur=st.session_state.get('user_role', 'Admin'),
                                action="SUPPRESSION PERSONNEL",
                                details=f"Suppression du personnel ID {p_obj.id} ({nom_p})"
                            ))
                            db.delete(p_obj)
                            db.commit()
                            st.success(f"✅ '{nom_p}' a été supprimé avec succès.")
                            db.close()
                            st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Erreur lors de la suppression : {e}")
        else:
            st.info("Aucun membre du personnel enregistré pour le moment.")
            
    finally:
        db.close()
