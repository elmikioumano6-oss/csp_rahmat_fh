import streamlit as st
from database.db_config import SessionLocal
from database.models import User, Enseignant, Eleve

def afficher_gestion_utilisateurs():
    st.subheader("👥 Gestion des Utilisateurs & Statuts")
    db = SessionLocal()

    try:
        # --- 1. CRÉATION D'UN NOUVEL UTILISATEUR ---
        with st.expander("➕ Créer un nouvel utilisateur", expanded=False):
            username = st.text_input("Nom d'utilisateur", key="create_username")
            password = st.text_input("Mot de passe", type="password", key="create_password")
            role = st.selectbox("Rôle", ["admin", "proviseur", "prof", "parent"], key="create_role")
            
            entite_id = None
            enfants_ids_str = None

            if role == "prof":
                profs = db.query(Enseignant).all()
                if profs:
                    choix_prof = st.selectbox("Lier au profil Enseignant", profs, format_func=lambda x: f"{x.nom} {x.prenom} (Spécialité : {getattr(x, 'specialite', 'N/A')})", key="create_prof_link")
                    entite_id = choix_prof.id
                else:
                    st.warning("⚠️ Aucun enseignant trouvé.")

            elif role == "parent":
                eleves = db.query(Eleve).all()
                if eleves:
                    choix_eleves = st.multiselect("Lier aux enfants (Plusieurs choix possibles)", eleves, format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})", key="create_parent_enfants")
                    if choix_eleves:
                        enfants_ids_str = ",".join([str(e.id) for e in choix_eleves])
                        entite_id = choix_eleves[0].id
                else:
                    st.warning("⚠️ Aucun élève trouvé.")

            if st.button("Créer le compte", key="btn_create_user"):
                if not username or not password:
                    st.error("Veuillez remplir le nom d'utilisateur et le mot de passe.")
                elif db.query(User).filter(User.username == username).first():
                    st.error("Ce nom d'utilisateur existe déjà.")
                else:
                    new_user = User(
                        username=username,
                        password=password,
                        role=role,
                        entite_id=entite_id,
                        enfants_ids=enfants_ids_str
                    )
                    db.add(new_user)
                    db.commit()
                    st.success(f"Compte '{username}' ({role}) créé avec succès !")
                    st.rerun()

        # --- 2. LISTE ET STATUT DES UTILISATEURS ---
        st.markdown("---")
        st.markdown("### 📋 Liste des utilisateurs enregistrés")
        
        users = db.query(User).all()
        if users:
            # Tableau récapitulatif
            data_users = []
            for u in users:
                 liaison = "Aucune"
                 if u.role == "prof" and u.entite_id:
                     prof = db.query(Enseignant).filter(Enseignant.id == u.entite_id).first()
                     liaison = f"Enseignant : {prof.nom} {prof.prenom}" if prof else "ID Inconnu"
                 elif u.role == "parent":
                     if u.enfants_ids:
                         ids = [int(i) for i in u.enfants_ids.split(",") if i.isdigit()]
                         eleves_lies = db.query(Eleve).filter(Eleve.id.in_(ids)).all()
                         liaison = ", ".join([f"{e.nom} {e.prenom}" for e in eleves_lies]) if eleves_lies else "Aucun enfant"
                     elif u.entite_id:
                         eleve = db.query(Eleve).filter(Eleve.id == u.entite_id).first()
                         liaison = f"Élève : {eleve.nom} {eleve.prenom}" if eleve else "Aucun"
                 elif u.role == "admin":
                     liaison = "Accès Complet (Admin)"
                
                 data_users.append({
                     "Nom d'utilisateur": u.username,
                     "Rôle": u.role.upper(),
                     "Rattachement": liaison,
                     "Statut": "🟢 Actif / Enregistré"
                 })
            
            import pandas as pd
            st.dataframe(pd.DataFrame(data_users), use_container_width=True)

            # --- 3. MODIFICATION / SUPPRESSION ---
            st.markdown("---")
            st.markdown("### ⚙️ Modifier ou Gérer un compte spécifique")
            
            user_dict = {f"{u.username} (Rôle : {u.role})": u.id for u in users}
            selected_choice = st.selectbox("Sélectionner un compte utilisateur", list(user_dict.keys()), key="select_manage_account")
            
            selected_id = user_dict[selected_choice]
            target_user = db.query(User).filter(User.id == selected_id).first()
            
            if target_user:
                col1, col2 = st.columns(2)
                
                with col1:
                    new_pwd = st.text_input("Nouveau mot de passe", type="password", key=f"pwd_mod_{target_user.id}")
                    if st.button("🔄 Mettre à jour le mot de passe", key=f"btn_pwd_{target_user.id}"):
                        if new_pwd:
                            target_user.password = new_pwd
                            db.commit()
                            st.success(f"Mot de passe mis à jour pour {target_user.username} !")
                            st.rerun()
                        else:
                            st.warning("Veuillez entrer un mot de passe.")
                            
                    # ASSOCIATION PARENT
                    if target_user.role == "parent":
                        st.markdown("#### 🔗 Modifier les enfants rattachés")
                        eleves = db.query(Eleve).all()
                        if eleves:
                            current_eleve_ids = []
                            if target_user.enfants_ids:
                                current_eleve_ids = [int(i) for i in target_user.enfants_ids.split(",") if i.isdigit()]
                            elif target_user.entite_id:
                                current_eleve_ids = [target_user.entite_id]
                                
                            default_eleves = [el for el in eleves if el.id in current_eleve_ids]
                            
                            selected_enfants = st.multiselect(
                                "Enfants rattachés", 
                                eleves, 
                                default=default_eleves, 
                                format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})", 
                                key=f"multi_eleves_{target_user.id}"
                            )
                            
                            if st.button("💾 Enregistrer les modifications", key=f"save_enfants_{target_user.id}"):
                                target_user.enfants_ids = ",".join([str(e.id) for e in selected_enfants]) if selected_enfants else None
                                target_user.entite_id = selected_enfants[0].id if selected_enfants else None
                                db.commit()
                                st.success("Liaisons mises à jour avec succès !")
                                st.rerun()

                    # ASSOCIATION PROFESSEUR
                    elif target_user.role == "prof":
                        st.markdown("#### 🔗 Modifier la fiche Enseignant liée")
                        profs = db.query(Enseignant).all()
                        if profs:
                            current_prof_index = 0
                            if target_user.entite_id:
                                for idx, p in enumerate(profs):
                                    if p.id == target_user.entite_id:
                                        current_prof_index = idx
                                        break
                                        
                            selected_prof = st.selectbox(
                                "Profil Enseignant", 
                                profs, 
                                index=current_prof_index, 
                                format_func=lambda x: f"{x.nom} {x.prenom}", 
                                key=f"select_prof_{target_user.id}"
                            )
                            
                            if st.button("💾 Enregistrer le lien", key=f"save_prof_{target_user.id}"):
                                target_user.entite_id = selected_prof.id
                                db.commit()
                                st.success("Lien enseignant mis à jour !")
                                st.rerun()

                with col2:
                    st.markdown("#### ❌ Suppression")
                    if target_user.username == "admin":
                        st.warning("⚠️ Le compte admin principal ne peut pas être supprimé.")
                    else:
                        if st.button(f"Supprimer {target_user.username}", type="primary", key=f"del_user_{target_user.id}"):
                            db.delete(target_user)
                            db.commit()
                            st.success(f"Compte '{target_user.username}' supprimé !")
                            st.rerun()
        else:
            st.info("Aucun utilisateur trouvé.")
            
    finally:
        db.close()
