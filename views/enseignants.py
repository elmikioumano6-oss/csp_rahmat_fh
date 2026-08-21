import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Enseignant, LogActivite, User, Classe, Matiere, Affectation

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
    
    # --- ESPACE DE LIAISON ET D'AFFECTATION (NOUVEAU) ---
    with st.expander("🔗 Lier un compte et Assigner des classes", expanded=False):
        enseignants = db.query(Enseignant).all()
        comptes_profs = db.query(User).filter(User.role == "prof").all()
        classes = db.query(Classe).all()
        matieres = db.query(Matiere).all()

        if not enseignants or not comptes_profs:
            st.warning("⚠️ Créez au moins un profil Enseignant et un Compte Utilisateur 'prof' pour utiliser cette section.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**1. Lier au compte de connexion**")
                ens_opts = {f"{e.nom} {e.prenom}": e.id for e in enseignants}
                prof_choisi = st.selectbox("Sélectionner l'Enseignant", list(ens_opts.keys()), key="link_prof")
                
                cpt_opts = {u.username: u.id for u in comptes_profs}
                cpt_choisi = st.selectbox("Lier au compte utilisateur (Login)", ["Aucun"] + list(cpt_opts.keys()), key="link_account")
                
                if st.button("Lier le compte"):
                    ens_obj = db.query(Enseignant).filter(Enseignant.id == ens_opts[prof_choisi]).first()
                    ens_obj.user_id = cpt_opts[cpt_choisi] if cpt_choisi != "Aucun" else None
                    db.commit()
                    st.success(f"✅ Compte '{cpt_choisi}' lié à {prof_choisi} !")
                    st.rerun()

            with col2:
                st.write("**2. Assigner une Matière et une Classe**")
                class_opts = {c.nom: c.id for c in classes}
                mat_opts = {m.nom: m.id for m in matieres}
                
                # On réutilise le prof sélectionné dans la col1 pour l'affectation
                st.write(f"Affectation pour : **{prof_choisi}**")
                classe_choisie = st.selectbox("Classe", list(class_opts.keys()) if class_opts else ["Aucune"])
                matiere_choisie = st.selectbox("Matière", list(mat_opts.keys()) if mat_opts else ["Aucune"])
                
                if st.button("Ajouter l'affectation"):
                    if classe_choisie != "Aucune" and matiere_choisie != "Aucune":
                        # Vérifier si l'affectation existe déjà
                        existe = db.query(Affectation).filter(
                            Affectation.enseignant_id == ens_opts[prof_choisi],
                            Affectation.classe_id == class_opts[classe_choisie],
                            Affectation.matiere_id == mat_opts[matiere_choisie]
                        ).first()
                        
                        if existe:
                            st.warning("⚠️ Cette affectation existe déjà.")
                        else:
                            nouvelle_affectation = Affectation(
                                enseignant_id=ens_opts[prof_choisi],
                                classe_id=class_opts[classe_choisie],
                                matiere_id=mat_opts[matiere_choisie]
                            )
                            db.add(nouvelle_affectation)
                            db.commit()
                            st.success(f"✅ {prof_choisi} enseignera {matiere_choisie} en {classe_choisie}.")
                            st.rerun()
                    else:
                        st.error("Veuillez créer des classes et des matières d'abord.")

            # Afficher les affectations actuelles
            st.write("---")
            st.write("**Affectations enregistrées :**")
            toutes_affectations = db.query(Affectation).all()
            if toutes_affectations:
                aff_data = [{
                    "ID": a.id,
                    "Enseignant": f"{a.enseignant.nom} {a.enseignant.prenom}" if a.enseignant else "N/A",
                    "Classe": a.classe.nom if a.classe else "N/A",
                    "Matière": a.matiere.nom if a.matiere else "N/A"
                } for a in toutes_affectations]
                st.dataframe(pd.DataFrame(aff_data), use_container_width=True)
            else:
                st.info("Aucune affectation enregistrée.")

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
                        
                        # Supprimer d'abord les affectations liées pour éviter les erreurs de clés étrangères
                        db.query(Affectation).filter(Affectation.enseignant_id == e_obj.id).delete()
                        
                        db.add(LogActivite(
                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            utilisateur=st.session_state.get('user_role', 'Admin'),
                            action="SUPPRESSION ENSEIGNANT",
                            details=f"Suppression de l'enseignant ID {e_obj.id} ({nom_complet}) et de ses affectations."
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
            "Téléphone": e.telephone or "N/A",
            "Compte lié": e.user.username if e.user else "Non lié" # NOUVEAU
        } for e in tous_profs]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun enseignant enregistré pour le moment.")
        
    db.close()