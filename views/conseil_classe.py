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
        else:
            options_classes = {c.nom: c.id for c in classes}
            classe_nom = st.selectbox("Classe", list(options_classes.keys()))
            classe_id = options_classes[classe_nom]
            
            eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
            if eleves:
                options_eleves = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in eleves}
                eleve_label = st.selectbox("Sélectionner l'élève", list(options_eleves.keys()))
                eleve_id = options_eleves[eleve_label]
                
                semestre = st.selectbox("Semestre", [1, 2])
                appreciation = st.text_area("Appréciation / Décision (ex: Félicitations, Avertissement, Passage)")
                
                submitted = st.form_submit_button("Enregistrer la décision")
                if submitted:
                    if appreciation.strip():
                        # Traçabilité
                        db.add(LogActivite(
                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            utilisateur=st.session_state.get('user_role', 'Admin'),
                            action="SAISIE CONSEIL",
                            details=f"Appréciation saisie pour élève ID {eleve_id} (Semestre {semestre}) : {appreciation[:50]}..."
                        ))
                        db.commit()
                        st.success("✅ Appréciation enregistrée avec succès !")
                        st.rerun()
                    else:
                        st.warning("⚠️ Veuillez écrire une appréciation.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger une appréciation erronée"):
        # On affiche les logs de conseil pour permettre de les supprimer si besoin
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