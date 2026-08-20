import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Matiere, LogActivite

def afficher_matieres():
    st.subheader("📚 Gestion des Matières et Coefficients")
    
    db = SessionLocal()
    try:
        # --- FORMULAIRE D'ENREGISTREMENT ---
        with st.form("form_matiere"):
            st.write("### Ajouter une nouvelle matière")
            
            nom = st.text_input("Nom de la matière")
            coefficient = st.number_input("Coefficient", min_value=1, step=1)
            
            submitted = st.form_submit_button("Enregistrer la matière")
            if submitted:
                if nom.strip():
                    try:
                        # Vérifier si la matière existe déjà
                        existe = db.query(Matiere).filter(Matiere.nom == nom).first()
                        if existe:
                            st.error("❌ Cette matière existe déjà.")
                        else:
                            nouvelle_matiere = Matiere(
                                nom=nom,
                                coefficient=coefficient
                            )
                            db.add(nouvelle_matiere)
                            
                            # Traçabilité dans le journal d'activité
                            db.add(LogActivite(
                                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                utilisateur=st.session_state.get('user_role', 'Admin'),
                                action="SAISIE MATIÈRE",
                                details=f"Ajout de la matière '{nom}' (Coeff: {coefficient})"
                            ))
                            
                            db.commit()
                            st.success("✅ Matière enregistrée avec succès !")
                            db.close()
                            st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Erreur lors de l'enregistrement de la matière : {e}")
                else:
                    st.warning("⚠️ Veuillez indiquer le nom de la matière.")

        st.markdown("---")
        
        # --- ESPACE DE CORRECTION / SUPPRESSION DES MATIÈRES ---
        with st.expander("🛠️ Supprimer ou corriger une matière enregistrée par erreur"):
            matieres = db.query(Matiere).order_by(Matiere.nom).all()
            if matieres:
                options_m = {f"ID {m.id} - {m.nom} (Coeff: {m.coefficient})": m.id for m in matieres}
                choix_m = st.selectbox("Sélectionner la matière à supprimer", list(options_m.keys()))
                
                if st.button("🗑️ Supprimer définitivement cette matière", type="primary"):
                    try:
                        m_id = options_m[choix_m]
                        m_obj = db.query(Matiere).filter(Matiere.id == m_id).first()
                        if m_obj:
                            nom_matiere = m_obj.nom
                            db.add(LogActivite(
                                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                utilisateur=st.session_state.get('user_role', 'Admin'),
                                action="SUPPRESSION MATIÈRE",
                                details=f"Suppression de la matière ID {m_obj.id} ({nom_matiere})"
                            ))
                            db.delete(m_obj)
                            db.commit()
                            st.success(f"✅ La matière '{nom_matiere}' a été supprimée avec succès.")
                            db.close()
                            st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Erreur lors de la suppression : {e}")
            else:
                st.info("Aucune matière enregistrée à corriger.")

        st.markdown("---")
        
        # --- LISTE DES MATIÈRES ---
        st.write("### 📋 Liste des matières")
        toutes_matieres = db.query(Matiere).order_by(Matiere.nom).all()
        if toutes_matieres:
            data = [{
                "ID": m.id,
                "Nom": m.nom,
                "Coefficient": m.coefficient
            } for m in toutes_matieres]
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("Aucune matière enregistrée pour le moment.")
            
    finally:
        db.close()
