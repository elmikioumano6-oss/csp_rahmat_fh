import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import CahierTexte, Classe, Matiere, Enseignant, LogActivite, User, Affectation

def afficher_cahier_texte(niveau_actif=None, prof_id=None):
    # Récupération automatique du prof_id depuis la session si non fourni
    if not prof_id and st.session_state.get("user_role") == "prof":
        db_temp = SessionLocal()
        username = st.session_state.get("username")
        user = db_temp.query(User).filter(User.username == username).first()
        if user:
            ens = db_temp.query(Enseignant).filter(Enseignant.user_id == user.id).first()
            if ens:
                prof_id = ens.id
        db_temp.close()

    role_actuel = st.session_state.get("user_role", "Admin")

    if role_actuel == "prof":
        st.subheader(f"📖 Cahier de Texte (Espace Professeur) - {niveau_actif}")
    else:
        st.subheader(f"📖 Cahier de Texte - {niveau_actif}")
    
    db = SessionLocal()
    
    # --- FILTRAGE DES CLASSES SELON LE RÔLE ---
    classes = []
    affectations_prof = []
    
    if prof_id:
        affectations_prof = db.query(Affectation).filter(Affectation.enseignant_id == prof_id).all()
        # On ne garde que les classes du cycle actif
        affectations_cycle = [aff for aff in affectations_prof if aff.classe and aff.classe.cycle == niveau_actif]
        classes_dict = {aff.classe.id: aff.classe for aff in affectations_cycle}
        classes = list(classes_dict.values())
    else:
        classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()

    # --- FORMULAIRE D'ENREGISTREMENT ---
    with st.form("form_cahier_texte"):
        st.write("### Enregistrer le contenu d'un cours")
        
        if not classes:
            st.warning("⚠️ Aucune classe ne vous est assignée pour ce cycle." if prof_id else "⚠️ Aucune classe enregistrée pour ce cycle.")
            db.close()
            return
            
        col1, col2 = st.columns(2)
        
        options_classes = {c.nom: c.id for c in classes}
        classe_nom = col1.selectbox("Classe", list(options_classes.keys()))
        classe_id = options_classes[classe_nom]
        
        # Filtrage dynamique des matières
        matieres_disponibles = []
        if prof_id:
            matieres_pour_classe = [aff.matiere for aff in affectations_prof if aff.classe_id == classe_id]
            matieres_dict = {m.id: m for m in matieres_pour_classe if m}
            matieres_disponibles = list(matieres_dict.values())
        else:
            matieres_disponibles = db.query(Matiere).all()
            
        if not matieres_disponibles:
            st.warning("⚠️ Aucune matière ne vous est assignée pour cette classe." if prof_id else "⚠️ Aucune matière enregistrée.")
            db.close()
            return

        options_matieres = {m.nom: m.id for m in matieres_disponibles}
        matiere_nom = col2.selectbox("Matière", list(options_matieres.keys()))
        matiere_id = options_matieres[matiere_nom]
        
        col3, col4 = st.columns(2)
        
        # Gestion du champ Enseignant
        enseignant_id = None
        if prof_id:
            enseignant_id = prof_id
            prof_obj = db.query(Enseignant).filter(Enseignant.id == prof_id).first()
            col3.text_input("Enseignant", value=f"{prof_obj.nom} {prof_obj.prenom}", disabled=True)
        else:
            enseignants = db.query(Enseignant).all()
            if not enseignants:
                st.warning("⚠️ Aucun enseignant enregistré dans la base.")
                db.close()
                return
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
    
    # --- PRÉPARATION DES DONNÉES FILTRÉES POUR HISTORIQUE ET MODIFICATION ---
    if prof_id:
        entrees_autorisees = (
            db.query(CahierTexte)
            .join(Classe)
            .filter(Classe.cycle == niveau_actif, CahierTexte.enseignant_id == prof_id)
            .order_by(CahierTexte.date.desc())
            .all()
        )
    else:
        entrees_autorisees = (
            db.query(CahierTexte)
            .join(Classe)
            .filter(Classe.cycle == niveau_actif)
            .order_by(CahierTexte.date.desc())
            .all()
        )

    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger une entrée erronée"):
        if entrees_autorisees:
            options_e = {f"ID {e.id} - {e.date} | {e.classe.nom} | {e.matiere.nom}": e.id for e in entrees_autorisees}
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
            st.info("Aucune entrée dans le cahier de texte à corriger pour vos classes.")

    st.markdown("---")
    
    # --- LISTE DES ENTRÉES ---
    st.write(f"### 📋 Historique du cahier de texte - {niveau_actif}")
    if entrees_autorisees:
        data = [{
            "Date": e.date,
            "Classe": e.classe.nom if e.classe else "N/A",
            "Matière": e.matiere.nom if e.matiere else "N/A",
            "Contenu": e.contenu,
            "Enseignant": f"{e.enseignant.nom} {e.enseignant.prenom}" if e.enseignant else "N/A"
        } for e in entrees_autorisees]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucune entrée enregistrée pour le moment.")
        
    db.close()