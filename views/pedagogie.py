import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Note, Inscription, Eleve, Classe, MatiereClasse, AnneeScolaire
from utils.pdf_service import generer_bulletin_niger_pdf

def afficher_pedagogie(cycle_actif):
    st.markdown(f"<div class='page-title-orange'>Gestion Pédagogique - {cycle_actif}</div>", unsafe_allow_html=True)
    db = SessionLocal()
    
    annee = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
    classes = db.query(Classe).filter(Classe.cycle == cycle_actif).all()
    
    if not classes:
        st.warning("Aucune classe trouvée. Veuillez d'abord créer des classes dans l'administration.")
        db.close()
        return

    c1, c2 = st.columns(2)
    classe_sel = c1.selectbox("Sélectionner une classe", [c.libelle for c in classes])
    classe_obj = db.query(Classe).filter(Classe.libelle == classe_sel).first()
    
    matieres = db.query(MatiereClasse).filter(MatiereClasse.classe_id == classe_obj.id).all()
    
    # --- ONGLET SAISIE DES NOTES ---
    tab1, tab2 = st.tabs(["✍️ Saisie des notes", "🖨️ Bulletins"])
    
    with tab1:
        if not matieres:
            st.warning("Veuillez définir les matières pour cette classe.")
        else:
            matiere_sel = st.selectbox("Matière", [m.nom_matiere for m in matieres])
            matiere_obj = db.query(MatiereClasse).filter(MatiereClasse.nom_matiere == matiere_sel, MatiereClasse.classe_id == classe_obj.id).first()
            inscrits = db.query(Inscription, Eleve).join(Eleve).filter(Inscription.classe_id == classe_obj.id, Inscription.annee_id == annee.id).all()
            
            if not inscrits:
                st.info("Aucun élève n'est inscrit dans cette classe pour l'année active. Veuillez en inscrire via le menu Scolarité > Élèves.")
            else:
                with st.form("form_notes"):
                    notes_data = []
                    for insc, elv in inscrits:
                        note_existante = db.query(Note).filter(Note.inscription_id == insc.id, Note.matiere_id == matiere_obj.id).first()
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.write(f"{elv.nom} {elv.prenom}")
                        nc = c2.number_input(f"Classe {elv.id}", 0.0, 20.0, float(note_existante.note_classe or 0) if note_existante else 0.0, label_visibility="collapsed")
                        nco = c3.number_input(f"Compo {elv.id}", 0.0, 20.0, float(note_existante.note_compo or 0) if note_existante else 0.0, label_visibility="collapsed")
                        notes_data.append((insc.id, nc, nco))
                        
                    if st.form_submit_button("Enregistrer les notes"):
                        for ins_id, n_c, n_co in notes_data:
                            note = db.query(Note).filter(Note.inscription_id == ins_id, Note.matiere_id == matiere_obj.id).first()
                            if not note:
                                note = Note(inscription_id=ins_id, matiere_id=matiere_obj.id, semestre=st.session_state.semestre_actif)
                                db.add(note)
                            note.note_classe, note.note_compo = n_c, n_co
                        db.commit()
                        st.success("Notes enregistrées avec succès !")
                        st.rerun()

    # --- ONGLET BULLETINS ---
    with tab2:
        st.subheader("Génération des Bulletins")
        inscrits = db.query(Inscription, Eleve).join(Eleve).filter(Inscription.classe_id == classe_obj.id, Inscription.annee_id == annee.id).all()
        
        if not inscrits:
            st.info("Aucun élève inscrit dans cette classe pour générer des bulletins.")
        else:
            liste_eleves_str = [f"{e.matricule} - {e.nom} {e.prenom}" for _, e in inscrits]
            eleve_choisi = st.selectbox("Choisir l'élève", liste_eleves_str)
            
            if eleve_choisi:
                mat_e = eleve_choisi.split(" - ")[0]
                
                if st.button("🖨️ Générer le Bulletin PDF"):
                    row_e = next(e for _, e in inscrits if e.matricule == mat_e)
                    df_n = pd.DataFrame([{"matiere": "Mathématiques", "note_classe": 15, "note_compo": 14, "coef": 4, "moyen_coef": 58, "rang": 1}])
                    
                    pdf_bytes = generer_bulletin_niger_pdf(
                        nom_eleve=f"{row_e.nom} {row_e.prenom}", matricule=mat_e, classe=classe_sel, df_notes=df_n,
                        effectif_total=len(inscrits), garcons=0, filles=0, rang_general=1,
                        moy_classe=12, max_moy=18, min_moy=7, nb_moyennes=10, 
                        semestre=st.session_state.semestre_actif, moy_annuelle=12, nb_absences=0, nb_retards=0
                    )
                    st.download_button("📥 Télécharger le Bulletin", pdf_bytes, f"Bulletin_{mat_e}.pdf", "application/pdf")
            
    db.close()