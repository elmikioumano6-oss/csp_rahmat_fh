import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Evaluation, Classe, Matiere, LogActivite

def afficher_planification(niveau_actif=None):
    st.subheader(f"📅 Planification des Évaluations - {niveau_actif}")
    
    db = SessionLocal()
    
    # --- FORMULAIRE DE PLANIFICATION ---
    with st.form("form_planification"):
        st.write("### Planifier une évaluation")
        
        # Sélection classe (filtrée par cycle)
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
        matieres = db.query(Matiere).all()
        
        if not classes or not matieres:
            st.warning("⚠️ Assurez-vous d'avoir créé des classes et des matières avant de planifier.")
        else:
            options_classes = {c.nom: c.id for c in classes}
            classe_nom = st.selectbox("Classe", list(options_classes.keys()))
            classe_id = options_classes[classe_nom]
            
            options_matieres = {m.nom: m.id for m in matieres}
            matiere_nom = st.selectbox("Matière", list(options_matieres.keys()))
            matiere_id = options_matieres[matiere_nom]
            
            titre = st.text_input("Titre de l'évaluation (ex: Devoir 1, Compo)")
            date_eval = st.date_input("Date de l'évaluation", value=datetime.today())
            semestre = st.selectbox("Semestre", [1, 2])
            
            submitted = st.form_submit_button("Enregistrer la planification")
            if submitted:
                if titre.strip():
                    nouvelle_eval = Evaluation(
                        titre=titre,
                        classe_id=classe_id,
                        matiere_id=matiere_id,
                        date=date_eval.strftime("%Y-%m-%d"),
                        semestre=semestre
                    )
                    db.add(nouvelle_eval)
                    
                    # Traçabilité dans le journal d'activité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SAISIE ÉVALUATION",
                        details=f"Planification '{titre}' pour classe ID {classe_id} (Matière ID {matiere_id})"
                    ))
                    
                    db.commit()
                    st.success("✅ Évaluation planifiée avec succès !")
                    st.rerun()
                else:
                    st.warning("⚠️ Veuillez donner un titre à l'évaluation.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger une évaluation planifiée par erreur"):
        evals = db.query(Evaluation).join(Classe).filter(Classe.cycle == niveau_actif).order_by(Evaluation.date).all()
        if evals:
            options_e = {f"ID {e.id} - {e.titre} | {e.classe.nom} | {e.matiere.nom} ({e.date})": e.id for e in evals}
            choix_e = st.selectbox("Sélectionner l'évaluation à supprimer", list(options_e.keys()))
            
            if st.button("🗑️ Supprimer définitivement cette planification", type="primary"):
                e_id = options_e[choix_e]
                e_obj = db.query(Evaluation).filter(Evaluation.id == e_id).first()
                if e_obj:
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION ÉVALUATION",
                        details=f"Suppression de l'évaluation ID {e_obj.id} ({e_obj.titre})"
                    ))
                    db.delete(e_obj)
                    db.commit()
                    st.success("✅ Évaluation supprimée et action tracée avec succès !")
                    st.rerun()
        else:
            st.info("Aucune évaluation planifiée pour ce cycle.")

    st.markdown("---")
    
    # --- LISTE DES PLANIFICATIONS ---
    st.write(f"### 📋 Planning des évaluations - {niveau_actif}")
    toutes_evals = db.query(Evaluation).join(Classe).filter(Classe.cycle == niveau_actif).order_by(Evaluation.date).all()
    if toutes_evals:
        data = [{
            "Titre": e.titre,
            "Date": e.date,
            "Classe": e.classe.nom,
            "Matière": e.matiere.nom,
            "Semestre": e.semestre
        } for e in toutes_evals]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucune évaluation planifiée pour le moment.")
        
    db.close()