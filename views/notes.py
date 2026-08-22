import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Classe, Eleve, Matiere, Note, LogActivite

def afficher_notes(niveau_actif):
    st.subheader(f"📝 Saisie des Notes - {niveau_actif}")
    st.markdown("Attribution des notes de classe et de composition par classe et par matière.")

    db = SessionLocal()
    try:
        # Récupération des classes du cycle actif
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
        if not classes:
            st.warning("⚠️ Aucune classe enregistrée pour ce cycle.")
            return

        # Dictionnaire unique pour éviter les conflits entre classes homonymes
        classe_options = {f"{c.nom} ({c.cycle}) [ID:{c.id}]": c.id for c in classes}
        classe_libelle = st.selectbox("Sélectionner la classe", list(classe_options.keys()))
        classe_id = classe_options[classe_libelle]

        # Récupération des matières
        matieres = db.query(Matiere).all()
        if not matieres:
            st.warning("⚠️ Aucune matière enregistrée.")
            return
        matiere_options = {m.nom: m.id for m in matieres}
        matiere_nom = st.selectbox("Sélectionner la matière", list(matiere_options.keys()))
        matiere_id = matiere_options[matiere_nom]

        semestre = st.selectbox("Sélectionner le semestre", [1, 2], index=0)

        st.markdown("---")

        # Récupération des élèves de la classe sélectionnée
        eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).order_by(Eleve.nom).all()
        if not eleves:
            st.info("ℹ️ Aucun élève inscrit dans cette classe pour le moment.")
            return

        st.write(f"### 📋 Liste des Élèves ({len(eleves)} élèves)")
        
        # Formulaire de saisie groupée des notes
        with st.form("form_saisie_notes"):
            notes_data = []
            
            # En-têtes du tableau de saisie
            col_h1, col_h2, col_h3, col_h4 = st.columns([2, 2, 2, 2])
            col_h1.markdown("**Matricule & Nom**")
            col_h2.markdown("**Prénom**")
            col_h3.markdown("**Note de Classe (/20)**")
            col_h4.markdown("**Note de Compo (/20)**")

            for eleve in eleves:
                # Rechercher si une note existe déjà pour cet élève, cette matière et ce semestre
                note_existante = db.query(Note).filter(
                    Note.eleve_id == eleve.id,
                    Note.matiere_id == matiere_id,
                    Note.semestre == semestre
                ).first()

                val_classe = note_existante.note_classe if note_existante else 0.0
                val_compo = note_existante.note_compo if note_existante else 0.0

                c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
                with c1:
                    st.text(f"{eleve.matricule} - {eleve.nom}")
                with c2:
                    st.text(eleve.prenom)
                with c3:
                    nc = st.number_input(
                        "Classe", min_value=0.0, max_value=20.0, value=float(val_classe), 
                        step=0.25, key=f"nc_{eleve.id}", label_visibility="collapsed"
                    )
                with c4:
                    nco = st.number_input(
                        "Compo", min_value=0.0, max_value=20.0, value=float(val_compo), 
                        step=0.25, key=f"nco_{eleve.id}", label_visibility="collapsed"
                    )
                
                notes_data.append({"eleve_id": eleve.id, "note_classe": nc, "note_compo": nco})

            submitted = st.form_submit_button("💾 Enregistrer toutes les notes")
            if submitted:
                try:
                    for item in notes_data:
                        note_obj = db.query(Note).filter(
                            Note.eleve_id == item["eleve_id"],
                            Note.matiere_id == matiere_id,
                            Note.semestre == semestre
                        ).first()

                        if note_obj:
                            # Mise à jour
                            note_obj.note_classe = item["note_classe"]
                            note_obj.note_compo = item["note_compo"]
                        else:
                            # Création
                            nouvelle_note = Note(
                                eleve_id=item["eleve_id"],
                                matiere_id=matiere_id,
                                note_classe=item["note_classe"],
                                note_compo=item["note_compo"],
                                semestre=semestre
                            )
                            db.add(nouvelle_note)

                    # Journal d'activité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get("username", "Admin"),
                        action="SAISIE DE NOTES",
                        details=f"Notes enregistrées pour la classe ID {classe_id}, Matière ID {matiere_id}, Semestre {semestre}"
                    ))

                    db.commit()
                    st.success("✅ Notes enregistrées et sauvegardées avec succès !")
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Erreur lors de l'enregistrement : {e}")

    finally:
        db.close()