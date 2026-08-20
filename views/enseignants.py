import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Enseignant, LogActivite

def afficher_enseignants():
    st.subheader("👨‍🏫 Gestion des Enseignants")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'ENREGISTREMENT ---
    with st.form("form_enseignant"):
        st.write("### Enregistrer un nouvel enseignant")
        
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        telephone = st.text_input("Téléphone")
        specialite = st.text_input("Spécialité (ex: Mathématiques, Physique)")
        
        submitted = st.form_submit_button("Enregistrer l'enseignant")
        if submitted:
            if nom.strip() and prenom.strip():
                nouveau_prof = Enseignant(
                    nom=nom,
                    prenom=prenom,
                    telephone=telephone,
                    specialite=specialite
                )
                db.add(nouveau_prof)
                
                # Traçabilité dans le journal d'activité
                db.add(LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get('user_role', 'Admin'),
                    action="ENREGISTREMENT ENSEIGNANT",
                    details=f"Ajout de l'enseignant {nom} {prenom} (Spécialité: {specialite or 'N/A'})"
                ))
                
                db.commit()
                st.success("✅ Enseignant enregistré avec succès !")
                st.rerun()
            else:
                st.warning("⚠️ Veuillez remplir au moins le nom et le prénom de l'enseignant.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION DES ENSEIGNANTS ---
    with st.expander("🛠️ Supprimer ou corriger un enseignant enregistré par erreur"):
        enseignants = db.query(Enseignant).order_by(Enseignant.nom).all()
        if enseignants:
            options_e = {f"ID {e.id} - {e.nom} {e.prenom} (Spécialité: {e.specialite or 'N/A'})": e.id for e in enseignants}
            choix_e = st.selectbox("Sélectionner l'enseignant à supprimer", list(options_e.keys()))
            
            if st.button("🗑️ Supprimer définitivement cet enseignant", type="primary"):
                e_id = options_e[choix_e]
                e_obj = db.query(Enseignant).filter(Enseignant.id == e_id).first()
                if e_obj:
                    nom_complet = f"{e_obj.nom} {e_obj.prenom}"
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION ENSEIGNANT",
                        details=f"Suppression de l'enseignant ID {e_obj.id} ({nom_complet})"
                    ))
                    db.delete(e_obj)
                    db.commit()
                    st.success(f"✅ L'enseignant {nom_complet} a été supprimé avec succès.")
                    st.rerun()
        else:
            st.info("Aucun enseignant enregistré à corriger.")

    st.markdown("---")
    
    # --- LISTE DES ENSEIGNANTS ---
    st.write("### 📋 Liste des enseignants")
    tous_profs = db.query(Enseignant).order_by(Enseignant.nom).all()
    if tous_profs:
        data = [{
            "ID": e.id,
            "Nom": e.nom,
            "Prénom": e.prenom,
            "Spécialité": e.specialite or "N/A",
            "Téléphone": e.telephone or "N/A"
        } for e in tous_profs]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun enseignant enregistré pour le moment.")
        
    db.close()