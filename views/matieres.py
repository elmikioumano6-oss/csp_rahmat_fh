import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Matiere, LogActivite

@st.cache_data(ttl=300)
def charger_matieres_cache():
    db = SessionLocal()
    try:
        matieres = db.query(Matiere.id, Matiere.nom, Matiere.coefficient).order_by(Matiere.nom).all()
        return [{"id": m.id, "nom": m.nom, "coefficient": m.coefficient} for m in matieres]
    finally:
        db.close()

def afficher_matieres():
    st.subheader("📚 Gestion des Matières et Coefficients")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'ENREGISTREMENT ---
    with st.form("form_matiere"):
        st.write("### Ajouter une nouvelle matière")
        
        nom = st.text_input("Nom de la matière")
        coefficient = st.number_input("Coefficient", min_value=1, step=1)
        
        submitted = st.form_submit_button("Enregistrer la matière")
        if submitted:
            if nom.strip():
                # Vérifier si la matière existe déjà
                existe = db.query(Matiere).filter(Matiere.nom == nom.strip()).first()
                if existe:
                    st.error("❌ Cette matière existe déjà.")
                else:
                    nouvelle_matiere = Matiere(
                        nom=nom.strip(),
                        coefficient=coefficient
                    )
                    db.add(nouvelle_matiere)
                    
                    # Traçabilité dans le journal d'activité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SAISIE MATIÈRE",
                        details=f"Ajout de la matière '{nom.strip()}' (Coeff: {coefficient})"
                    ))
                    
                    db.commit()
                    st.cache_data.clear()  # Vider le cache après l'écriture
                    st.success("✅ Matière enregistrée avec succès !")
                    st.rerun()
            else:
                st.warning("⚠️ Veuillez indiquer le nom de la matière.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / MODIFICATION / SUPPRESSION ---
    with st.expander("🛠️ Modifier ou supprimer une matière enregistrée"):
        matieres = db.query(Matiere).order_by(Matiere.nom).all()
        if matieres:
            options_m = {f"ID {m.id} - {m.nom} (Coeff: {m.coefficient})": m.id for m in matieres}
            choix_m = st.selectbox("Sélectionner la matière", list(options_m.keys()), key="select_matiere_modif")
            m_id = options_m[choix_m]
            m_obj = db.query(Matiere).filter(Matiere.id == m_id).first()
            
            if m_obj:
                action_type = st.radio("Action à effectuer", ["Modifier", "Supprimer"], horizontal=True, key="radio_action_matiere")
                
                if action_type == "Modifier":
                    with st.form("form_modif_matiere"):
                        nouveau_nom = st.text_input("Nom de la matière", value=m_obj.nom)
                        nouveau_coeff = st.number_input("Coefficient", min_value=1, step=1, value=int(m_obj.coefficient))
                        
                        submit_modif = st.form_submit_button("💾 Mettre à jour la matière")
                        if submit_modif:
                            if nouveau_nom.strip():
                                doublon = db.query(Matiere).filter(Matiere.nom == nouveau_nom.strip(), Matiere.id != m_obj.id).first()
                                if doublon:
                                    st.error("❌ Une autre matière porte déjà ce nom.")
                                else:
                                    ancien_nom = m_obj.nom
                                    m_obj.nom = nouveau_nom.strip()
                                    m_obj.coefficient = nouveau_coeff
                                    
                                    db.add(LogActivite(
                                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                        utilisateur=st.session_state.get('user_role', 'Admin'),
                                        action="MODIFICATION MATIÈRE",
                                        details=f"Modification de la matière ID {m_obj.id}: '{ancien_nom}' -> '{m_obj.nom}' (Coeff: {nouveau_coeff})"
                                    ))
                                    db.commit()
                                    st.cache_data.clear()  # Vider le cache après modification
                                    st.success(f"✅ La matière '{m_obj.nom}' a été mise à jour avec succès.")
                                    st.rerun()
                            else:
                                st.warning("⚠️ Le nom de la matière ne peut pas être vide.")
                else:
                    if st.button("🗑️ Supprimer définitivement cette matière", type="primary", key="btn_suppr_matiere"):
                        nom_matiere = m_obj.nom
                        db.add(LogActivite(
                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            utilisateur=st.session_state.get('user_role', 'Admin'),
                            action="SUPPRESSION MATIÈRE",
                            details=f"Suppression de la matière ID {m_obj.id} ({nom_matiere})"
                        ))
                        db.delete(m_obj)
                        db.commit()
                        st.cache_data.clear()  # Vider le cache après suppression
                        st.success(f"✅ La matière '{nom_matiere}' a été supprimée avec succès.")
                        st.rerun()
        else:
            st.info("Aucune matière enregistrée à modifier ou supprimer.")

    st.markdown("---")
    
    # --- LISTE DES MATIÈRES (Via le cache pour une vitesse maximale) ---
    st.write("### 📋 Liste des matières")
    toutes_matieres = charger_matieres_cache()
    if toutes_matieres:
        data = [{
            "ID": m["id"],
            "Nom": m["nom"],
            "Coefficient": m["coefficient"]
        } for m in toutes_matieres]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucune matière enregistrée pour le moment.")
        
    db.close()