import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Personnel, LogActivite

def afficher_personnels(niveau_actif=None):
    st.subheader(f"👥 Gestion des Personnels - {niveau_actif}")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'ENREGISTREMENT ---
    with st.form("form_personnel"):
        st.write("### Enregistrer un membre du personnel")
        
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        fonction = st.text_input("Fonction (ex: Surveillant, Secrétaire, Comptable)")
        telephone = st.text_input("Téléphone")
        
        submitted = st.form_submit_button("Enregistrer le personnel")
        if submitted:
            if nom.strip() and prenom.strip() and fonction.strip():
                nouveau_perso = Personnel(
                    nom=nom,
                    prenom=prenom,
                    fonction=fonction,
                    telephone=telephone
                )
                db.add(nouveau_perso)
                
                # Traçabilité dans le journal d'activité
                db.add(LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get('user_role', 'Admin'),
                    action="ENREGISTREMENT PERSONNEL",
                    details=f"Ajout du personnel {nom} {prenom} (Fonction: {fonction})"
                ))
                
                db.commit()
                st.success("✅ Personnel enregistré avec succès !")
                st.rerun()
            else:
                st.warning("⚠️ Veuillez remplir le nom, le prénom et la fonction.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION DES PERSONNELS ---
    with st.expander("🛠️ Supprimer ou corriger un membre du personnel enregistré par erreur"):
        personnels = db.query(Personnel).order_by(Personnel.nom).all()
        if personnels:
            options_p = {f"ID {p.id} - {p.nom} {p.prenom} ({p.fonction})": p.id for p in personnels}
            choix_p = st.selectbox("Sélectionner le membre du personnel à supprimer", list(options_p.keys()))
            
            if st.button("🗑️ Supprimer définitivement ce personnel", type="primary"):
                p_id = options_p[choix_p]
                p_obj = db.query(Personnel).filter(Personnel.id == p_id).first()
                if p_obj:
                    nom_complet = f"{p_obj.nom} {p_obj.prenom}"
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION PERSONNEL",
                        details=f"Suppression du personnel ID {p_obj.id} ({nom_complet})"
                    ))
                    db.delete(p_obj)
                    db.commit()
                    st.success(f"✅ Le personnel {nom_complet} a été supprimé avec succès.")
                    st.rerun()
        else:
            st.info("Aucun membre du personnel enregistré à corriger.")

    st.markdown("---")
    
    # --- LISTE DU PERSONNEL ---
    st.write("### 📋 Liste du personnel")
    tous_perso = db.query(Personnel).order_by(Personnel.nom).all()
    if tous_perso:
        data = [{
            "ID": p.id,
            "Nom": p.nom,
            "Prénom": p.prenom,
            "Fonction": p.fonction,
            "Téléphone": p.telephone or "N/A"
        } for p in tous_perso]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun membre du personnel enregistré pour le moment.")
        
    db.close()