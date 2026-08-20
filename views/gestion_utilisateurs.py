import streamlit as st
from database.db_config import SessionLocal
from database.models import User, Enseignant, Eleve

def afficher_gestion_utilisateurs():
    st.subheader("⚙️ Gestion des Comptes Utilisateurs")
    db = SessionLocal()

    try:
        # --- 1. FORMULAIRE DE CRÉATION ---
        with st.expander("➕ Créer un nouvel utilisateur", expanded=True):
            username = st.text_input("Nom d'utilisateur", key="input_new_username")
            password = st.text_input("Mot de passe", type="password", key="input_new_password")
            role = st.selectbox("Rôle", ["admin", "proviseur", "prof", "parent"], key="input_new_role")
            
            entite_id = None
            enfants_ids_str = None
            
            if role == "prof":
                profs = db.query(Enseignant).all()
                if profs:
                    choix_prof = st.selectbox("Lier à l'enseignant", profs, format_func=lambda x: f"{x.nom} {x.prenom}", key="select_prof_link")
                    entite_id = choix_prof.id
                else:
                    st.info("ℹ️ Aucun enseignant enregistré.")
                    
            elif role == "parent":
                eleves = db.query(Eleve).all()
                if eleves:
                    choix_eleves = st.multiselect("Lier aux comptes des élèves (Plusieurs choix possibles)", eleves, format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})", key="multiselect_eleves_link")
                    if choix_eleves:
                        enfants_ids_str = ",".join([str(e.id) for e in choix_eleves])
                else:
                    st.info("ℹ️ Aucun élève enregistré.")

            if st.button("Créer le compte", key="btn_submit_create"):
                if not username or not password:
                    st.error("Veuillez remplir tous les champs.")
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

        # --- 2. GESTION DES COMPTES EXISTANTS ---
        st.markdown("---")
        st.markdown("### 📋 Modifier ou Supprimer un compte")
        
        users = db.query(User).all()
        if users:
            user_dict = {f"{u.username} (Rôle : {u.role})": u.id for u in users}
            selected_choice = st.selectbox("Sélectionner un utilisateur à gérer", list(user_dict.keys()), key="select_manage_user")
            
            selected_id = user_dict[selected_choice]
            target_user = db.query(User).filter(User.id == selected_id).first()
            
            if target_user:
                st.info(f"Compte sélectionné : **{target_user.username}** | Rôle : **{target_user.role}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_pwd = st.text_input("Nouveau mot de passe", type="password", key=f"pwd_{target_user.id}")
                    if st.button("🔄 Mettre à jour le mot de passe", key=f"btn_pwd_{target_user.id}"):
                        if new_pwd:
                            target_user.password = new_pwd
                            db.commit()
                            st.success(f"Mot de passe mis à jour pour {target_user.username} !")
                            st.rerun()
                        else:
                            st.warning("Veuillez saisir un mot de passe.")
                            
                    # Association de plusieurs élèves si c'est un parent
                    if target_user.role == "parent":
                        st.markdown("---")
                        st.write("🔗 **Association avec les élèves (Multi-enfants)**")
                        eleves = db.query(Eleve).all()
                        if eleves:
                            # Récupérer les IDs déjà enregistrés
                            default_eleves = []
                            if target_user.enfants_ids:
                                current_ids = [int(i) for i in target_user.enfants_ids.split(",") if i.isdigit()]
                                default_eleves = [el for el in eleves if el.id in current_ids]
                            elif target_user.entite_id: # Rétrocompatibilité ancien champ unique
                                default_eleves = [el for el in eleves if el.id == target_user.entite_id]

                            new_eleves = st.multiselect("Sélectionner les enfants de ce parent", eleves, default=default_eleves, format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})", key=f"link_eleves_{target_user.id}")
                            
                            if st.button("Valider les liaisons élèves", key=f"btn_link_{target_user.id}"):
                                target_user.enfants_ids = ",".join([str(e.id) for e in new_eleves]) if new_eleves else None
                                db.commit()
                                st.success(f"Succès ! Les liaisons pour {target_user.username} ont été mises à jour.")
                                st.rerun()
                        else:
                            st.info("Aucun élève enregistré.")
                            
                with col2:
                    st.write("Zone de suppression")
                    if target_user.username == "admin":
                        st.warning("⚠️ Le compte 'admin' principal ne peut pas être supprimé.")
                    else:
                        if st.button(f"❌ Supprimer {target_user.username}", type="primary", key=f"btn_del_{target_user.id}"):
                            db.delete(target_user)
                            db.commit()
                            st.success(f"Compte '{target_user.username}' supprimé avec succès !")
                            st.rerun()
        else:
            st.info("Aucun utilisateur trouvé.")
            
    finally:
        db.close()
