import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import EmploiDuTemps, Classe, Matiere, Enseignant, LogActivite

def afficher_emploi_du_temps(niveau_actif=None):
    st.subheader(f"📅 Emploi du Temps - {niveau_actif}")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'ENREGISTREMENT ---
    with st.form("form_edt"):
        st.write("### Ajouter un créneau")
        
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
        matieres = db.query(Matiere).all()
        enseignants = db.query(Enseignant).all()
        
        if not classes or not matieres or not enseignants:
            st.warning("⚠️ Assurez-vous d'avoir créé des Classes, Matières et Enseignants avant.")
        else:
            col1, col2 = st.columns(2)
            
            options_classes = {c.nom: c.id for c in classes}
            classe_nom = col1.selectbox("Classe", list(options_classes.keys()))
            classe_id = options_classes[classe_nom]
            
            options_matieres = {m.nom: m.id for m in matieres}
            matiere_nom = col2.selectbox("Matière", list(options_matieres.keys()))
            matiere_id = options_matieres[matiere_nom]
            
            col3, col4 = st.columns(2)
            options_profs = {f"{p.nom} {p.prenom}": p.id for p in enseignants}
            enseignant_nom = col3.selectbox("Enseignant", list(options_profs.keys()))
            enseignant_id = options_profs[enseignant_nom]
            
            jour = col4.selectbox("Jour", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"])
            heure = st.text_input("Créneau horaire (ex: 08:00 - 10:00)")
            semestre = st.selectbox("Semestre", [1, 2])
            
            submitted = st.form_submit_button("Ajouter à l'emploi du temps")
            if submitted:
                if heure.strip():
                    nouveau_creneau = EmploiDuTemps(
                        classe_id=classe_id,
                        matiere_id=matiere_id,
                        enseignant_id=enseignant_id,
                        jour=jour,
                        heure=heure,
                        semestre=semestre
                    )
                    db.add(nouveau_creneau)
                    
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SAISIE EDT",
                        details=f"Programmation : {classe_nom} | {matiere_nom} | {jour} {heure}"
                    ))
                    
                    db.commit()
                    st.success("✅ Créneau ajouté avec succès !")
                    st.rerun()
                else:
                    st.warning("⚠️ Veuillez indiquer le créneau horaire.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger un créneau erroné"):
        creneaux = db.query(EmploiDuTemps).join(Classe).filter(Classe.cycle == niveau_actif).all()
        if creneaux:
            options_c = {f"ID {c.id} - {c.jour} {c.heure} | {c.classe.nom} | {c.matiere.nom}": c.id for c in creneaux}
            choix_c = st.selectbox("Sélectionner le créneau à supprimer", list(options_c.keys()))
            
            if st.button("🗑️ Supprimer définitivement ce créneau", type="primary"):
                c_id = options_c[choix_c]
                c_obj = db.query(EmploiDuTemps).filter(EmploiDuTemps.id == c_id).first()
                if c_obj:
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION EDT",
                        details=f"Suppression du créneau ID {c_obj.id} ({c_obj.jour} {c_obj.heure})"
                    ))
                    db.delete(c_obj)
                    db.commit()
                    st.success("✅ Créneau supprimé et action tracée avec succès !")
                    st.rerun()
        else:
            st.info("Aucun créneau programmé pour ce cycle.")

    st.markdown("---")
    
    # --- LISTE DES CRÉNEAUX ---
    st.write(f"### 📋 Emploi du temps - {niveau_actif}")
    tous_creneaux = db.query(EmploiDuTemps).join(Classe).filter(Classe.cycle == niveau_actif).all()
    if tous_creneaux:
        data = [{
            "Jour": c.jour,
            "Heure": c.heure,
            "Classe": c.classe.nom,
            "Matière": c.matiere.nom,
            "Enseignant": f"{c.enseignant.nom} {c.enseignant.prenom}" if c.enseignant else "N/A"
        } for c in tous_creneaux]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun emploi du temps programmé pour le moment.")
        
    db.close()