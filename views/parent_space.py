import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import User, Eleve, Note

def afficher_espace_parent():
    st.subheader("👥 Espace Suivi - Espace Parent")
    db = SessionLocal()
    
    try:
        username = st.session_state.get('username')
        user_record = db.query(User).filter(User.username == username).first()
        
        # Correction : utilisation de entite_id au lieu de entity_id
        if not user_record or not user_record.entite_id:
            st.warning("⚠️ Votre compte parent n'est pas encore lié à un élève. Veuillez contacter l'administrateur pour associer votre compte à une fiche élève.")
            return
            
        eleve_id = user_record.entite_id
        eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
        
        if eleve:
            st.success(f"Bienvenue dans l'espace de suivi de votre enfant : **{eleve.nom} {eleve.prenom}** (Matricule : {eleve.matricule})")
            
            # Affichage des notes de l'élève
            notes = db.query(Note).filter(Note.eleve_id == eleve.id).all()
            if notes:
                st.markdown("### 📚 Notes de l'élève")
                data_notes = [{"Matière": n.matiere, "Note": n.valeur, "Appréciation": getattr(n, 'appreciation', '-')} for n in notes]
                st.dataframe(pd.DataFrame(data_notes), use_container_width=True)
            else:
                st.info("Aucune note enregistrée pour le moment.")
        else:
            st.error("Élève introuvable dans la base de données.")
            
    finally:
        db.close()
