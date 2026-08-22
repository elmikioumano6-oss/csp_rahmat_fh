import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Enseignant, Affectation, Classe, Matiere, Eleve, Note, LogActivite
from datetime import datetime

def afficher_enseignants(niveau_actif=None):
    user_role = st.session_state.get("user_role", "admin")
    
    # --- SI C'EST UN PROFESSEUR : Afficher son Espace Dédié ---
    if user_role == "prof":
        afficher_espace_prof_dedie()
        return

    # --- SI C'EST UN ADMIN : Gestion classique des enseignants ---
    st.subheader("👨‍🏫 Gestion des Enseignants & Affectations")
    
    db = SessionLocal()
    try:
        tab_liste, tab_affectation = st.tabs(["📋 Liste des Enseignants", "🔗 Affectations Classes & Matières"])
        
        with tab_liste:
            st.write("### Enseignants enregistrés")
            enseignants = db.query(Enseignant).all()
            if enseignants:
                data = [{"ID": e.id, "Nom": e.nom, "Prénom": e.prenom, "Spécialité": e.specialite or "N/A", "Téléphone": e.telephone or "N/A"} for e in enseignants]
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun enseignant enregistré.")
                
        with tab_affectation:
            st.write("### Assigner un enseignant à une classe et une matière")
            # Ici vous gérez les affectations (Affectation model)
            st.info("Utilisez ce module pour lier un prof à une classe spécifique (ex: Troisième A, Terminale D, etc.).")

    finally:
        db.close()

def afficher_espace_prof_dedie():
    st.subheader("👨‍🏫 Mon Espace Enseignant")
    st.markdown("Interface dédiée pour consulter vos classes assignées et saisir vos notes en toute sécurité.")
    
    db = SessionLocal()
    try:
        current_username = st.session_state.get("username", "")
        
        # Trouver l'enseignant connecté
        enseignant = db.query(Enseignant).first() # À affiner selon votre liaison user_id
        if not enseignant:
            st.warning("⚠️ Aucun profil enseignant associé à votre compte.")
            return

        st.markdown(f"**Bienvenue, Professeur {enseignant.nom} {enseignant.prenom}**")
        st.markdown("---")

        # Récupérer les affectations de cet enseignant
        affectations = db.query(Affectation).filter(Affectation.enseignant_id == enseignant.id).all()
        if not affectations:
            st.info("ℹ️ Aucune classe ne vous a encore été assignée par l'administration.")
            return

        # Classes uniques sécurisées contre les doublons (ex: plusieurs 3ème)
        classes_assignees = {f"{aff.classe.nom} ({aff.classe.cycle}) [ID:{aff.classe.id}]": aff.classe_id for aff in affectations if aff.classe}
        
        if not classes_assignees:
            st.warning("⚠️ Vos affectations ne comportent aucune classe valide.")
            return

        col1, col2 = st.columns(2)
        with col1:
            classe_libelle = st.selectbox("🎯 Mes Classes Assignées", list(classes_assignees.keys()))
            classe_id_selectionnee = classes_assignees[classe_libelle]

        matieres_disponibles = {aff.matiere.nom: aff.matiere_id for aff in affectations if aff.classe_id == classe_id_selectionnee and aff.matiere}
        
        with col2:
            if matieres_disponibles:
                matiere_nom = st.selectbox("📚 Matières", list(matieres_disponibles.keys()))
                matiere_id_selectionnee = matieres_disponibles[matiere_nom]
            else:
                st.warning("Aucune matière liée à cette classe.")
                return

        st.markdown("---")
        
        # Onglets de travail du prof
        tab_eleves, tab_notes = st.tabs(["👥 Liste des Élèves", "📝 Saisie des Notes"])
        
        with tab_eleves:
            eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id_selectionnee).order_by(Eleve.nom).all()
            if eleves:
                st.dataframe(pd.DataFrame([{"Matricule": e.matricule, "Nom": e.nom, "Prénom": e.prenom} for e in eleves]), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun élève dans cette classe.")

        with tab_notes:
            st.write(f"### Saisie des Notes - {matiere_nom}")
            eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id_selectionnee).order_by(Eleve.nom).all()
            semestre = st.selectbox("Semestre", [1, 2], key="sem_prof_n")
            
            if eleves:
                with st.form("form_notes_prof_unique"):
                    notes_saisies = []
                    for el in eleves:
                        note_ex = db.query(Note).filter(Note.eleve_id == el.id, Note.matiere_id == matiere_id_selectionnee, Note.semestre == semestre).first()
                        val_c = note_ex.note_classe if note_ex else 0.0
                        val_co = note_ex.note_compo if note_ex else 0.0

                        c1, c2, c3 = st.columns([3, 2, 2])
                        with c1:
                            st.text(f"{el.nom} {el.prenom}")
                        with c2:
                            nc = st.number_input("Classe (/20)", 0.0, 20.0, float(val_c), 0.25, key=f"nc_{el.id}", label_visibility="collapsed")
                        with c3:
                            nco = st.number_input("Compo (/20)", 0.0, 20.0, float(val_co), 0.25, key=f"nco_{el.id}", label_visibility="collapsed")
                        
                        notes_saisies.append({"eleve_id": el.id, "nc": nc, "nco": nco})

                    if st.form_submit_button("Enregistrer les notes"):
                        for item in notes_saisies:
                            n_obj = db.query(Note).filter(Note.eleve_id == item["eleve_id"], Note.matiere_id == matiere_id_selectionnee, Note.semestre == semestre).first()
                            if n_obj:
                                n_obj.note_classe = item["nc"]
                                n_obj.note_compo = item["nco"]
                            else:
                                db.add(Note(eleve_id=item["eleve_id"], matiere_id=matiere_id_selectionnee, note_classe=item["nc"], note_compo=item["nco"], semestre=semestre))
                        db.commit()
                        st.success("✅ Notes enregistrées avec succès !")

    finally:
        db.close()