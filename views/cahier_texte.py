import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import CahierTexte, Classe, Matiere, Enseignant, LogActivite

def afficher_cahier_texte(niveau_actif=None):
    st.subheader(f"📖 Cahier de Texte - {niveau_actif}")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'ENREGISTREMENT ---
    with st.form("form_cahier_texte"):
        st.write("### Enregistrer le contenu d'un cours")
        
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
        matieres = db.query(Matiere).all()
        enseignants = db.query(Enseignant).all()
        
        if not classes or not matieres or not enseignants:
            st.warning("⚠️ Assurez-vous d'avoir créé des Classes, Matières et Enseignants.")
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
            
            date_cours = col4.date_input("Date du cours", value=datetime.today())
            semestre = st.selectbox("Semestre", [1, 2])
            contenu = st.text_area("Contenu / Sujet du cours")
            
            submitted = st.form_submit_button("Enregistrer l'entrée")
            if submitted:
                if contenu.strip():
                    nouvelle_entree = CahierTexte(
                        classe_id=classe_id,
                        matiere_id=matiere_id,
                        enseignant_id=enseignant_id,
                        date=date_cours.strftime("%Y-%m-%d"),
                        contenu=contenu,
                        semestre=semestre
                    )
                    db.add(nouvelle_entree)
                    
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SAISIE CAHIER TEXTE",
                        details=f"Cours : {classe_nom} | {matiere_nom} | {date_cours}"
                    ))
                    
                    db.commit()
                    st.success("✅ Entrée enregistrée avec succès !")
                    st.rerun()
                else:
                    st.warning("⚠️ Veuillez remplir le contenu du cours.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger une entrée erronée"):
        entrees = db.query(CahierTexte).join(Classe).filter(Classe.cycle == niveau_actif).order_by(CahierTexte.date.desc()).all()
        if entrees:
            options_e = {f"ID {e.id} - {e.date} | {e.classe.nom} | {e.matiere.nom}": e.id for e in entrees}
            choix_e = st.selectbox("Sélectionner l'entrée à supprimer", list(options_e.keys()))
            
            if st.button("🗑️ Supprimer définitivement cette entrée", type="primary"):
                e_id = options_e[choix_e]
                e_obj = db.query(CahierTexte).filter(CahierTexte.id == e_id).first()
                if e_obj:
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION CAHIER TEXTE",
                        details=f"Suppression entrée ID {e_obj.id} ({e_obj.date} - {e_obj.classe.nom})"
                    ))
                    db.delete(e_obj)
                    db.commit()
                    st.success("✅ Entrée supprimée et action tracée avec succès !")
                    st.rerun()
        else:
            st.info("Aucune entrée dans le cahier de texte pour ce cycle.")

    st.markdown("---")
    
    # --- LISTE DES ENTRÉES ---
    st.write(f"### 📋 Historique du cahier de texte - {niveau_actif}")
    toutes_entrees = db.query(CahierTexte).join(Classe).filter(Classe.cycle == niveau_actif).order_by(CahierTexte.date.desc()).all()
    if toutes_entrees:
        data = [{
            "Date": e.date,
            "Classe": e.classe.nom,
            "Matière": e.matiere.nom,
            "Contenu": e.contenu,
            "Enseignant": f"{e.enseignant.nom} {e.enseignant.prenom}" if e.enseignant else "N/A"
        } for e in toutes_entrees]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucune entrée enregistrée pour le moment.")
        
    db.close()