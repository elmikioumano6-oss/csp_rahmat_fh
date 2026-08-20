import streamlit as st
from database.db_config import SessionLocal
from database.models import User, Enseignant, Eleve

def afficher_gestion_utilisateurs():
    st.subheader("⚙️ Gestion des Comptes & Associations")
    db = SessionLocal()

    try:
        # --- 1. CRÉATION D'UN NOUVEL UTILISATEUR ---
        with st.expander("➕ Créer un compte et lier ses entités", expanded=True):
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
                    st.info("💡 Le professeur accèdera aux modules de saisie et de suivi selon ses affectations.")
                else:
                    st.warning("⚠️ Aucun enseignant trouvé. Veuillez d'abord en créer dans le menu 'Enseignants'.")

            elif role == "parent":
                eleves = db.query(Eleve).all()
                if eleves:
                    choix_eleves = st.multiselect("Lier aux enfants (Plusieurs choix possibles)", eleves, format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})", key="create_parent_enfants")
                    if choix_eleves:
                        enfants_ids_str = ",".join([str(e.id) for e in choix_eleves])
                        entite_id = choix_eleves[0].id  # Pour la rétrocompatibilité
                else:
                    st.warning("⚠️ Aucun élève trouvé. Veuillez d'abord inscrire des élèves.")

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

        # --- 2. GESTION ET MODIFICATION DES COMPTES EXISTANTS ---
        st.markdown("---")
        st.markdown("### 📋 Modifier ou Lier les comptes existants")
        
        users = db.query(User).all()
        if users:
            user_dict = {f"{u.username} (Rôle : {u.role})": u.id for u in users}
            selected_choice = st.selectbox("Sélectionner un compte utilisateur", list(user_dict.keys()), key="select_manage_account")
            
            selected_id = user_dict[selected_choice]
            target_user = db.query(User).filter(User.id == selected_id).first()
            
            if target_user:
                st.info(f"Compte en cours : **{target_user.username}** | Rôle : **{target_user.role.upper()}**")
                
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
                            
                    # ASSOCIATION PARENT (Multi-enfants)
                    if target_user.role == "parent":
                        st.markdown("---")
                        st.markdown("#### 🔗 Association Parent ➔ Élèves")
                        eleves = db.query(Eleve).all()
                        if eleves:
                            current_eleve_ids = []
                            if target_user.enfants_ids:
                                current_eleve_ids = [int(i) for i in target_user.enfants_ids.split(",") if i.isdigit()]
                            elif target_user.entite_id:
                                current_eleve_ids = [target_user.entite_id]
                                
                            default_eleves = [el for el in eleves if el.id in current_eleve_ids]
                            
                            selected_enfants = st.multiselect(
                                "Enfants rattachés à ce parent", 
                                eleves, 
                                default=default_eleves, 
                                format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})", 
                                key=f"multi_eleves_{target_user.id}"
                            )
                            
                            if st.button("💾 Enregistrer les enfants liés", key=f"save_enfants_{target_user.id}"):
                                target_user.enfants_ids = ",".join([str(e.id) for e in selected_enfants]) if selected_enfants else None
                                target_user.entite_id = selected_enfants[0].id if selected_enfants else None
                                db.commit()
                                st.success("Liaisons des enfants mises à jour avec succès !")
                                st.rerun()
                        else:
                            st.info("Aucun élève enregistré.")

                    # ASSOCIATION PROFESSEUR
                    elif target_user.role == "prof":
                        st.markdown("---")
                        st.markdown("#### 🔗 Association Professeur ➔ Fiche Enseignant")
                        profs = db.query(Enseignant).all()
                        if profs:
                            current_prof_index = 0
                            if target_user.entite_id:
                                for idx, p in enumerate(profs):
                                    if p.id == target_user.entite_id:
                                        current_prof_index = idx
                                        break
                                        
                            selected_prof = st.selectbox(
                                "Lier au profil Enseignant", 
                                profs, 
                                index=current_prof_index, 
                                format_func=lambda x: f"{x.nom} {x.prenom} (Spécialité : {getattr(x, 'specialite', 'N/A')})", 
                                key=f"select_prof_{target_user.id}"
                            )
                            
                            if st.button("💾 Enregistrer le lien Enseignant", key=f"save_prof_{target_user.id}"):
                                target_user.entite_id = selected_prof.id
                                db.commit()
                                st.success(f"Compte lié à l'enseignant {selected_prof.nom} {selected_prof.prenom} !")
                                st.rerun()
                        else:
                            st.info("Aucun enseignant enregistré.")

                with col2:
                    st.markdown("#### ❌ Suppression du compte")
                    if target_user.username == "admin":
                        st.warning("⚠️ Le compte admin principal ne peut pas être supprimé.")
                    else:
                        if st.button(f"Supprimer le compte {target_user.username}", type="primary", key=f"del_user_{target_user.id}"):
                            db.delete(target_user)
                            db.commit()
                            st.success(f"Compte '{target_user.username}' supprimé avec succès !")
                            st.rerun()
        else:
            st.info("Aucun utilisateur trouvé.")
            
    finally:
        db.close()
