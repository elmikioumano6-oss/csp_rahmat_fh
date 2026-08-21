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
                    nom=nom.strip(),
                    prenom=prenom.strip(),
                    telephone=telephone.strip(),
                    specialite=specialite.strip()
                )
                db.add(nouveau_prof)
                
                # Traçabilité dans le journal d'activité
                db.add(LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get('user_role', 'Admin'),
                    action="ENREGISTREMENT ENSEIGNANT",
                    details=f"Ajout de l'enseignant {nom.strip()} {prenom.strip()} (Spécialité: {specialite.strip() or 'N/A'})"
                ))
                
                db.commit()
                st.success("✅ Enseignant enregistré avec succès !")
                st.rerun()
            else:
                st.warning("⚠️ Veuillez remplir au moins le nom et le prénom de l'enseignant.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / MODIFICATION / SUPPRESSION DES ENSEIGNANTS ---
    with st.expander("🛠️ Modifier ou supprimer un enseignant enregistré"):
        enseignants = db.query(Enseignant).order_by(Enseignant.nom).all()
        if enseignants:
            options_e = {f"ID {e.id} - {e.nom} {e.prenom} (Spécialité: {e.specialite or 'N/A'})": e.id for e in enseignants}
            choix_e = st.selectbox("Sélectionner l'enseignant", list(options_e.keys()), key="select_enseignant_modif")
            e_id = options_e[choix_e]
            e_obj = db.query(Enseignant).filter(Enseignant.id == e_id).first()
            
            if e_obj:
                action_type = st.radio("Action à effectuer", ["Modifier", "Supprimer"], horizontal=True, key="radio_action_enseignant")
                
                if action_type == "Modifier":
                    with st.form("form_modif_enseignant"):
                        nouveau_nom = st.text_input("Nom", value=e_obj.nom)
                        nouveau_prenom = st.text_input("Prénom", value=e_obj.prenom)
                        nouveau_tel = st.text_input("Téléphone", value=e_obj.telephone or "")
                        nouvelle_spec = st.text_input("Spécialité", value=e_obj.specialite or "")
                        
                        submit_modif = st.form_submit_button("💾 Mettre à jour l'enseignant")
                        if submit_modif:
                            if nouveau_nom.strip() and nouveau_prenom.strip():
                                ancien_nom = f"{e_obj.nom} {e_obj.prenom}"
                                e_obj.nom = nouveau_nom.strip()
                                e_obj.prenom = nouveau_prenom.strip()
                                e_obj.telephone = nouveau_tel.strip()
                                e_obj.specialite = nouvelle_spec.strip()
                                
                                db.add(LogActivite(
                                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    utilisateur=st.session_state.get('user_role', 'Admin'),
                                    action="MODIFICATION ENSEIGNANT",
                                    details=f"Modification de l'enseignant ID {e_obj.id}: '{ancien_nom}' -> '{e_obj.nom} {e_obj.prenom}' (Spécialité: {e_obj.specialite or 'N/A'})"
                                ))
                                db.commit()
                                st.success(f"✅ L'enseignant {e_obj.nom} {e_obj.prenom} a été mis à jour avec succès.")
                                st.rerun()
                            else:
                                st.warning("⚠️ Le nom et le prénom ne peuvent pas être vides.")
                else:
                    if st.button("🗑️ Supprimer définitivement cet enseignant", type="primary", key="btn_suppr_enseignant"):
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
            st.info("Aucun enseignant enregistré à modifier ou supprimer.")

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