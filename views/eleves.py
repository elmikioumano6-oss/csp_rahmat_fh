import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
# J'ai ajouté User ici
from database.models import Eleve, Classe, LogActivite, User 

def afficher_eleves(niveau_actif=None):
    st.subheader(f"👥 Inscription et Gestion des Élèves - {niveau_actif}")
    
    db = SessionLocal()
    
    # Récupération des parents pour le menu déroulant
    parents = db.query(User).filter(User.role == 'parent').all()
    parent_options = {p.username: p.id for p in parents}
    
    # --- FORMULAIRE D'INSCRIPTION ---
    with st.form("form_inscription_eleve"):
        st.write("### Inscrire un nouvel élève")
        
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
        if not classes:
            st.warning(f"⚠️ Veuillez d'abord créer des classes pour le cycle {niveau_actif}.")
            db.close()
            return
            
        options_classes = {c.nom: c.id for c in classes}
        classe_nom = st.selectbox("Classe", list(options_classes.keys()))
        classe_id = options_classes[classe_nom]
        
        col1, col2 = st.columns(2)
        with col1:
            matricule = st.text_input("Matricule unique")
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
        
        with col2:
            sexe = st.selectbox("Sexe", ["Garçon", "Fille"])
            telephone = st.text_input("Téléphone (Contact)")
            montant_reduction = st.number_input("Montant de réduction (FCFA)", min_value=0.0, step=1000.0)
            
            # NOUVEAU : Sélecteur de parent
            parent_select = st.selectbox(
                "Assigner un compte parent (Optionnel)", 
                ["Aucun"] + list(parent_options.keys())
            )
        
        submitted = st.form_submit_button("Inscrire l'élève")
        if submitted:
            if matricule.strip() and nom.strip() and prenom.strip():
                existe = db.query(Eleve).filter(Eleve.matricule == matricule).first()
                if existe:
                    st.error("❌ Ce matricule existe déjà dans la base de données.")
                else:
                    # Logique pour le parent_id
                    parent_id = parent_options.get(parent_select) # Retourne l'ID ou None si "Aucun"
                    
                    nouvel_eleve = Eleve(
                        matricule=matricule,
                        nom=nom,
                        prenom=prenom,
                        sexe=sexe,
                        telephone=telephone,
                        montant_reduction=montant_reduction,
                        classe_id=classe_id,
                        parent_id=parent_id # <--- Liaison avec le parent
                    )
                    db.add(nouvel_eleve)
                    
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="INSCRIPTION ÉLÈVE",
                        details=f"Inscription de {nom} {prenom} (Matricule: {matricule}). Parent lié: {parent_select}"
                    ))
                    
                    db.commit()
                    st.success(f"✅ Élève {nom} {prenom} inscrit avec succès !")
                    st.rerun()
            else:
                st.warning("⚠️ Veuillez remplir le matricule, le nom et le prénom.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger un élève"):
        eleves_cycle = db.query(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).order_by(Eleve.nom).all()
        if eleves_cycle:
            options_e = {f"Matricule: {e.matricule} - {e.nom} {e.prenom}": e.id for e in eleves_cycle}
            choix_e = st.selectbox("Sélectionner l'élève", list(options_e.keys()))
            
            if st.button("🗑️ Supprimer définitivement cet élève", type="primary"):
                e_id = options_e[choix_e]
                e_obj = db.query(Eleve).filter(Eleve.id == e_id).first()
                if e_obj:
                    nom_complet = f"{e_obj.nom} {e_obj.prenom} ({e_obj.matricule})"
                    db.delete(e_obj)
                    db.commit()
                    st.success(f"✅ L'élève {nom_complet} a été supprimé.")
                    st.rerun()
        else:
            st.info("Aucun élève enregistré pour ce cycle.")

    st.markdown("---")
    
    # --- LISTE DES ÉLÈVES ---
    st.write(f"### 📋 Liste des élèves inscrits - {niveau_actif}")
    tous_eleves = db.query(Eleve).join(Classe).filter(Classe.cycle == niveau_actif).order_by(Eleve.nom).all()
    if tous_eleves:
        data = [{
            "Matricule": e.matricule,
            "Nom": e.nom,
            "Prénom": e.prenom,
            "Classe": e.classe.nom if e.classe else "N/A",
            "Parent lié": e.parent.username if e.parent else "Aucun"
        } for e in tous_eleves]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun élève inscrit pour le moment.")
        
    db.close()