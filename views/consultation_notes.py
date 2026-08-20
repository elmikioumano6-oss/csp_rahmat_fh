import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Eleve, Classe, Note, Matiere

def afficher_consultation_notes(niveau_actif=None):
    st.subheader("📖 Consultation des Notes et Relevés")
    
    db = SessionLocal()
    
    classes = db.query(Classe).all()
    if not classes:
        st.warning("⚠️ Aucune classe enregistrée.")
        db.close()
        return
        
    options_classes = {c.nom: c.id for c in classes}
    classe_nom = st.selectbox("Sélectionner la classe", list(options_classes.keys()), key="consult_classe")
    classe_id = options_classes[classe_nom]
    
    semestre_choisi = st.selectbox("Sélectionner le Semestre", ["1er Semestre", "2ème Semestre"], key="consult_semestre")
    sem_num = 1 if semestre_choisi == "1er Semestre" else 2
    
    eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
    if not eleves:
        st.info("Aucun élève dans cette classe.")
        db.close()
        return
        
    options_eleves = {f"{e.nom} {e.prenom} (Matricule: {e.matricule})": e.id for e in eleves}
    eleve_choisi_str = st.selectbox("Sélectionner l'élève", list(options_eleves.keys()), key="consult_eleve")
    eleve_id = options_eleves[eleve_choisi_str]
    
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    matieres = db.query(Matiere).all()
    
    if st.button("Afficher le Relevé"):
        st.markdown(f"### 📋 Relevé de notes - **{eleve.nom} {eleve.prenom}** ({semestre_choisi})")
        
        data = []
        total_points = 0
        total_coeffs = 0
        
        for m in matieres:
            n = db.query(Note).filter(
                Note.eleve_id == eleve.id, 
                Note.matiere_id == m.id, 
                Note.semestre == sem_num
            ).first()
            
            n_cl = n.note_classe if n and n.note_classe is not None else 0.0
            n_co = n.note_compo if n and n.note_compo is not None else 0.0
            coef = getattr(m, 'coefficient', 1) or 1
            
            moy_mat = (n_cl + (n_co * 2)) / 3 if (n and n.note_classe is not None and n.note_compo is not None) else (n_cl or n_co)
            moyen_coef = moy_mat * coef
            
            total_points += moyen_coef
            total_coeffs += coef
            
            app_mat = "Bien" if moy_mat >= 12 else ("Assez Bien" if moy_mat >= 10 else "Faible")
            
            data.append({
                "Matière": m.nom,
                "Note Classe /20": n_cl,
                "Note Compo /20": n_co,
                "Coef": coef,
                "Moyenne Matière": round(moy_mat, 2),
                "Moyen x Coef": round(moyen_coef, 1),
                "Appréciation": app_mat
            })
            
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        moyenne_generale = round(total_points / total_coeffs, 2) if total_coeffs > 0 else 0.0
        
        col1, col2 = st.columns(2)
        col1.metric("Total Points / Total Coeffs", f"{round(total_points, 1)} / {total_coeffs * 20}")
        col2.metric(f"Moyenne du {semestre_choisi}", f"{moyenne_generale} / 20")

    db.close()