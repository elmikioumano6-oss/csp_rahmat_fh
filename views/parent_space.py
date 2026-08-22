import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import User, Eleve, Classe, Note

def afficher_espace_parent():
    st.subheader("👨‍👩‍👧 Espace Parent - Suivi de l'Enfant")
    
    db = SessionLocal()
    try:
        current_username = st.session_state.get("username", "")
        parent_user = db.query(User).filter(User.username == current_username).first()
        
        if not parent_user:
            st.warning("⚠️ Compte parent introuvable.")
            return

        # Récupérer les élèves liés à ce parent via parent_id
        enfants = db.query(Eleve).filter(Eleve.parent_id == parent_user.id).all()
        
        if not enfants:
            st.info("ℹ️ Aucun enfant n'est actuellement associé à votre compte parent. Veuillez contacter l'administration.")
            return

        # Sélectionner l'enfant si le parent en a plusieurs
        enfant_options = {f"{e.nom} {e.prenom} - Classe : {e.classe.nom if e.classe else 'Non assignée'} [Matricule: {e.matricule}]": e.id for e in enfants}
        
        choix_enfant = st.selectbox("Sélectionner votre enfant", list(enfant_options.keys()))
        enfant_id = enfant_options[choix_enfant]
        
        enfant_actif = db.query(Eleve).filter(Eleve.id == enfant_id).first()
        
        if enfant_actif:
            st.markdown("---")
            st.write(f"### 📋 Bulletins & Notes de : {enfant_actif.nom} {enfant_actif.prenom}")
            
            # Récupérer les notes de l'élève
            notes = db.query(Note).filter(Note.eleve_id == enfant_actif.id).all()
            if notes:
                data_notes = []
                for n in notes:
                    matiere_nom = n.matiere.nom if n.matiere else "Matière inconnue"
                    total = (n.note_classe or 0) + (n.note_compo or 0) # Ajustez selon votre formule de calcul
                    data_notes.append({
                        "Matière": matiere_nom,
                        "Semestre": n.semestre,
                        "Note Classe (/20)": n.note_classe or 0.0,
                        "Note Compo (/20)": n.note_compo or 0.0
                    })
                st.dataframe(pd.DataFrame(data_notes), use_container_width=True, hide_index=True)
            else:
                st.info("Aucune note enregistrée pour le moment.")

    finally:
        db.close()