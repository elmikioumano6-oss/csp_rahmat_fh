import streamlit as st
from database.db_config import SessionLocal
from database.models import User, Enseignant, Eleve

def afficher_gestion_utilisateurs():
    st.subheader("⚙️ Gestion des Comptes Utilisateurs")
    db = SessionLocal()

    try:
        # --- 1. FORMULAIRE DE CRÉATION ---
        with st.expander("➕ Créer un nouvel utilisateur"):
            with st.form("form_create_user", clear_on_submit=True):
                username = st.text_input("Nom d'utilisateur")
                password = st.text_input("Mot de passe", type="password")
                role = st.selectbox("Rôle", ["admin", "proviseur", "prof", "parent"])
                
                entite_id = None
                if role == "prof":
                    profs = db.query(Enseignant).all()
                    if profs:
                        choix_prof = st.selectbox("Lier à l'enseignant", profs, format_func=lambda x: f"{x.nom} {x.prenom}")
                        entite_id = choix_prof.id
                elif role == "parent":
                    eleves = db.query(Eleve).all()
                    if eleves:
                        choix_eleve = st.selectbox("Lier à l'élève", eleves, format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})")
                        entite_id = choix_eleve.id

                if st.form_submit_button("Créer le compte"):
                    if not username or not password:
                        st.error("Veuillez remplir tous les champs.")
                    elif db.query(User).filter(User.username == username).first():
                        st.error("Ce nom d'utilisateur existe déjà.")
                    else:
                        db.add(User(username=username, password=password, role=role, entite_id=entite_id))
                        db.commit()
                        st.success(f"Compte '{username}' créé avec succès !")
                        st.rerun()

        # --- 2. GESTION DES COMPTES EXISTANTS ---
        st.markdown("---")
        st.markdown("### 📋 Modifier ou Supprimer un compte")
        
        users = db.query(User).all()
        if users:
            user_dict = {f"{u.username} (Rôle : {u.role})": u.id for u in users}
            selected_choice = st.selectbox("Sélectionner un utilisateur à gérer", list(user_dict.keys()))
            
            selected_id = user_dict[selected_choice]
            target_user = db.query(User).filter(User.id == selected_id).first()
            
            if target_user:
                st.info(f"Compte sélectionné : **{target_user.username}** | Rôle : **{target_user.role}** | ID Entité actuel : **{target_user.entite_id if target_user.entite_id else 'Aucun'}**")
                
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
                            
                    # Option de liaison/changement d'élève si c'est un parent
                    if target_user.role == "parent":
                        st.markdown("---")
                        st.write("🔗 **Association avec un élève**")
                        eleves = db.query(Eleve).all()
                        if eleves:
                            current_index = 0
                            if target_user.entite_id:
                                for idx, el in enumerate(eleves):
                                    if el.id == target_user.entite_id:
                                        current_index = idx
                                        break
                                        
                            new_eleve = st.selectbox("Lier au compte de l'élève", eleves, index=current_index, format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})", key=f"link_eleve_{target_user.id}")
                            if st.button("Valider la liaison élève", key=f"btn_link_{target_user.id}"):
                                target_user.entite_id = new_eleve.id
                                db.commit()
                                st.success(f"Succès ! {target_user.username} est maintenant lié à l'élève {new_eleve.nom} {new_eleve.prenom}.")
                                st.rerun()
                        else:
                            st.info("Aucun élève enregistré dans l'établissement.")
                            
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
