import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Eleve, Classe, Note, LogActivite

def afficher_conseil_classe(niveau_actif=None):
    st.subheader(f"👨‍🏫 Conseil de Classe - {niveau_actif}")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'APPRÉCIATION ---
    with st.form("form_conseil"):
        st.write("### Saisir une appréciation / décision")
        
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
        if not classes:
            st.warning(f"⚠️ Aucune classe trouvée pour le cycle {niveau_actif}.")
            db.close()
            return
            
        options_classes = {c.nom: c.id for c in classes}
        classe_nom = st.selectbox("Classe", list(options_classes.keys()))
        classe_id = options_classes[classe_nom]
        
        eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
        if not eleves:
            st.warning("⚠️ Aucun élève trouvé dans cette classe.")
            db.close()
            return
            
        options_eleves = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in eleves}
        eleve_label = st.selectbox("Sélectionner l'élève", list(options_eleves.keys()))
        eleve_id = options_eleves[eleve_label]
        
        semestre = st.selectbox("Semestre", [1, 2])
        
        # Suggestions types pour un conseil de classe rigoureux
        decisions_types = [
            "Tableau d'honneur", 
            "Encouragements", 
            "Félicitations", 
            "Avertissement travail", 
            "Avertissement conduite", 
            "Blâme", 
            "Passage en classe supérieure", 
            "Redoublement"
        ]
        
        mention_type = st.selectbox("Mention / Décision type", ["-- Libre --"] + decisions_types)
        appreciation = st.text_area("Appréciation détaillée du conseil")
        
        submitted = st.form_submit_button("Enregistrer la décision")
        if submitted:
            texte_final = f"[{mention_type}] {appreciation}" if mention_type != "-- Libre --" else appreciation
            
            if texte_final.strip():
                # Astuce : On cherche si une note/synthèse existe pour ce semestre pour y stocker l'appréciation, 
                # ou l'on met à jour un champ dédié si vous ajoutez une colonne 'appreciation' dans votre modèle Note.
                note_concernee = db.query(Note).filter(
                    Note.eleve_id == eleve_id,
                    Note.semestre == semestre
                ).first()
                
                if note_concernee:
                    note_concernee.appreciation = texte_final.strip()
                
                # Traçabilité dans le journal
                db.add(LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get('user_role', 'Admin'),
                    action="SAISIE CONSEIL",
                    details=f"Appréciation pour élève ID {eleve_id} (Semestre {semestre}) : {texte_final[:50]}..."
                ))
                
                db.commit()
                st.success("✅ Appréciation enregistrée avec succès !")
                st.rerun()
            else:
                st.warning("⚠️ Veuillez écrire ou sélectionner une appréciation.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Consulter ou supprimer les appréciations saisies"):
        logs_conseil = db.query(LogActivite).filter(LogActivite.action == "SAISIE CONSEIL").order_by(LogActivite.id.desc()).all()
        if logs_conseil:
            options_l = {f"{l.date} | {l.details}": l.id for l in logs_conseil}
            choix_l = st.selectbox("Sélectionner l'entrée à supprimer", list(options_l.keys()))
            
            if st.button("🗑️ Supprimer définitivement cette trace", type="primary"):
                l_id = options_l[choix_l]
                l_obj = db.query(LogActivite).filter(LogActivite.id == l_id).first()
                if l_obj:
                    db.delete(l_obj)
                    db.commit()
                    st.success("✅ Trace supprimée avec succès !")
                    st.rerun()
        else:
            st.info("Aucune appréciation enregistrée à corriger.")

    db.close()