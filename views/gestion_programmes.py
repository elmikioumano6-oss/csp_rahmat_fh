import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Classe, Matiere, Programme

def afficher_gestion_programmes(niveau_actif):
    st.subheader(f"📚 Référentiel des Programmes Officiels - {niveau_actif}")
    db = SessionLocal()

    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    matieres = db.query(Matiere).all()

    if not classes or not matieres:
        st.warning("⚠️ Veuillez d'abord configurer des classes et des matières dans le système.")
        db.close()
        return

    # --- FORMULAIRE DE PARAMÉTRAGE D'UN PROGRAMME ---
    with st.expander("➕ Enregistrer / Mettre à jour un volume du programme officiel", expanded=True):
        with st.form("form_programme"):
            col1, col2, col3 = st.columns(3)
            
            options_classes = {c.nom: c.id for c in classes}
            choix_classe_nom = col1.selectbox("Classe", list(options_classes.keys()))
            
            options_matieres = {m.nom: m.id for m in matieres}
            choix_matiere_nom = col2.selectbox("Matière", list(options_matieres.keys()))
            
            semestre = col3.selectbox("Semestre / Trimestre", [1, 2])
            
            volume_prevu = st.number_input("Volume horaire officiel prévu (heures selon le PDF)", min_value=1.0, value=30.0, step=1.0)
            
            submitted = st.form_submit_button("Enregistrer dans le Référentiel", type="primary")
            if submitted:
                classe_id = options_classes[choix_classe_nom]
                matiere_id = options_matieres[choix_matiere_nom]
                
                # Vérifier si un enregistrement existe déjà
                existant = db.query(Programme).filter(
                    Programme.classe_id == classe_id,
                    Programme.matiere_id == matiere_id,
                    Programme.semestre == semestre
                ).first()
                
                if existant:
                    existant.volume_horaire_prevu = volume_prevu
                    st.success(f"✅ Programme mis à jour pour **{choix_matiere_nom}** en **{choix_classe_nom}**.")
                else:
                    nouveau = Programme(
                        classe_id=classe_id,
                        matiere_id=matiere_id,
                        volume_horaire_prevu=volume_prevu,
                        semestre=semestre
                    )
                    db.add(nouveau)
                    st.success(f"✅ Référentiel officiel enregistré pour **{choix_matiere_nom}** en **{choix_classe_nom}**.")
                
                db.commit()

    st.markdown("---")

    # --- TABLEAU RÉCAPITULATIF DES PROGRAMMES ENREGISTRÉS ---
    st.markdown(f"### 📋 Récapitulatif des volumes horaires officiels - Cycle {niveau_actif}")
    
    programmes_enregistres = db.query(Programme).join(Classe).filter(Classe.cycle == niveau_actif).all()
    
    if not programmes_enregistres:
        st.info("ℹ️ Aucun volume horaire officiel n'a encore été saisi pour ce cycle. Utilisez le formulaire ci-dessus pour définir les bases.")
    else:
        data = []
        for p in programmes_enregistres:
            c_nom = p.classe.nom if p.classe else "N/A"
            m_nom = p.matiere.nom if p.matiere else "N/A"
            data.append({
                "Classe": c_nom,
                "Matière": m_nom,
                "Semestre": p.semestre,
                "Volume Horaire Officiel (h)": p.volume_horaire_prevu
            })
        
        df_prog = pd.DataFrame(data)
        st.dataframe(df_prog, use_container_width=True)

    db.close()