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

        # --- 2. GESTION DES COMPTES EXISTANTS (SÉLECTION SÉCURISÉE) ---
        st.markdown("---")
        st.markdown("### 📋 Modifier ou Supprimer un compte")
        
        users = db.query(User).all()
        if users:
            # Création d'une liste de choix lisible
            user_dict = {f"{u.username} (Rôle : {u.role})": u for u in users}
            selected_choice = st.selectbox("Sélectionner un utilisateur à gérer", list(user_dict.keys()))
            
            target_user = user_dict[selected_choice]
            
            st.info(f"Compte sélectionné : **{target_user.username}** | Rôle : **{target_user.role}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_pwd = st.text_input("Nouveau mot de passe", type="password", key=f"pwd_{target_user.id}")
                if st.button("🔄 Mettre à jour le mot de passe"):
                    if new_pwd:
                        target_user.password = new_pwd
                        db.commit()
                        st.success(f"Mot de passe mis à jour pour {target_user.username} !")
                        st.rerun()
                    else:
                        st.warning("Veuillez saisir un mot de passe.")
                        
            with col2:
                st.write("Zone de suppression")
                # Utilisation d'un bouton direct pour supprimer l'utilisateur sélectionné
                if st.button(f"❌ Supprimer {target_user.username}", type="primary"):
                    if target_user.username == "admin":
                        st.error("Impossible de supprimer le compte administrateur principal !")
                    else:
                        db.delete(target_user)
                        db.commit()
                        st.success(f"Compte '{target_user.username}' supprimé avec succès !")
                        st.rerun()
        else:
            st.info("Aucun utilisateur trouvé.")
            
    finally:
        db.close()
