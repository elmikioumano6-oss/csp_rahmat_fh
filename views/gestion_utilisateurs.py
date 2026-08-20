import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import User, Enseignant, Eleve

def afficher_gestion_utilisateurs():
    st.subheader("👥 Gestion des Utilisateurs & Sécurité")
    db = SessionLocal()

    try:
        # --- 1. CRÉATION D'UN NOUVEL UTILISATEUR ---
        with st.expander("➕ Créer un nouvel utilisateur", expanded=True):
            username = st.text_input("Nom d'utilisateur", key="create_username")
            password = st.text_input("Mot de passe", type="password", key="create_password")
            role = st.selectbox("Rôle", ["admin", "proviseur", "prof", "parent"], key="create_role")
            
            entite_id = None
            enfants_ids_str = None

            if role == "prof":
                profs = db.query(Enseignant).all()
                if profs:
                    choix_prof = st.selectbox("Lier au profil Enseignant", profs, format_func=lambda x: f"{x.nom} {x.prenom}", key="create_prof_link")
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
            
            elif role in ["proviseur", "admin"]:
                st.info(f"ℹ️ Le rôle **{role.upper()}** dispose d'un accès étendu et ne nécessite pas de liaison élève/professeur.")

            if st.button("Créer le compte", key="btn_create_user"):
                if not username or not password:
                    st.error("Veuillez remplir le nom d'utilisateur et le mot de passe.")
                elif db.query(User).filter(User.username == username).first():
                    st.error("Ce nom d'utilisateur existe déjà.")
                else:
                    try:
                        user_data = {
                            "username": username,
                            "password": password,
                            "role": role,
                            "entite_id": entite_id,
                            "is_active": True
                        }
                        if hasattr(User, 'enfants_ids'):
                            user_data["enfants_ids"] = enfants_ids_str

                        new_user = User(**user_data)
                        db.add(new_user)
                        db.commit()
                        st.success(f"Compte '{username}' ({role}) créé avec succès !")
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Erreur lors de la création : {e}")

        # --- 2. LISTE ET STATUT DES UTILISATEURS ---
        st.markdown("---")
        st.markdown("### 📋 Liste et Statut des utilisateurs")
        
        users = db.query(User).all()
        if users:
            data_users = []
            for u in users:
                 liaison = "Aucune"
                 if u.role == "prof" and u.entite_id:
                     prof = db.query(Enseignant).filter(Enseignant.id == u.entite_id).first()
                     liaison = f"Enseignant : {prof.nom} {prof.prenom}" if prof else "ID Inconnu"
                 elif u.role == "parent":
                     raw_enfants = getattr(u, 'enfants_ids', None)
                     if raw_enfants:
                         ids = [int(i) for i in raw_enfants.split(",") if i.isdigit()]
                         eleves_lies = db.query(Eleve).filter(Eleve.id.in_(ids)).all()
                         liaison = ", ".join([f"{e.nom} {e.prenom}" for e in eleves_lies]) if eleves_lies else "Aucun enfant"
                     elif u.entite_id:
                         eleve = db.query(Eleve).filter(Eleve.id == u.entite_id).first()
                         liaison = f"Élève : {eleve.nom} {eleve.prenom}" if eleve else "Aucun"
                 elif u.role in ["admin", "proviseur"]:
                     liaison = f"Accès Global ({u.role.upper()})"
                
                 is_active_val = getattr(u, 'is_active', True)
                 statut_texte = "🟢 Actif" if is_active_val else "🔴 Bloqué / Déconnecté"
                
                 data_users.append({
                     "Nom d'utilisateur": u.username,
                     "Rôle": u.role.upper(),
                     "Rattachement": liaison,
                     "Statut": statut_texte
                 })
            
            st.dataframe(pd.DataFrame(data_users), use_container_width=True)

            # --- 3. ACTIONS RAPIDES & GESTION ---
            st.markdown("---")
            st.markdown("### ⚙️ Actions Rapides sur un Compte")
            
            user_dict = {f"{u.username} (Rôle : {u.role})": u.id for u in users}
            selected_choice = st.selectbox("Sélectionner un compte utilisateur à gérer", list(user_dict.keys()), key="select_manage_account")
            
            selected_id = user_dict[selected_choice]
            target_user = db.query(User).filter(User.id == selected_id).first()
            
            if target_user:
                st.info(f"Compte sélectionné : **{target_user.username}** | Rôle : **{target_user.role.upper()}**")
                
                col_action1, col_action2, col_action3 = st.columns(3)
                
                # --- BOUTON 1 : RÉINITIALISATION DU MOT DE PASSE ---
                with col_action1:
                    st.markdown("#### 🔑 Réinitialisation")
                    if st.button("🔄 Réinitialiser MDP à '1234'", key=f"btn_reset_pwd_{target_user.id}"):
                        target_user.password = "1234"
                        db.commit()
                        st.success(f"Mot de passe de '{target_user.username}' réinitialisé à **1234** !")
                        st.rerun()

                # --- BOUTON 2 : BLOQUER / ACTIVER ---
                with col_action2:
                    st.markdown("#### 🔒 Sécurité & Accès")
                    is_active_current = getattr(target_user, 'is_active', True)
                    if target_user.username == "admin":
                        st.info("Le compte admin principal ne peut pas être bloqué.")
                    else:
                        if is_active_current:
                            if st.button("🚫 Bloquer / Déconnecter", type="secondary", key=f"btn_block_{target_user.id}"):
                                target_user.is_active = False
                                db.commit()
                                st.warning(f"Le compte '{target_user.username}' a été bloqué !")
                                st.rerun()
                        else:
                            if st.button("✅ Activer le compte", type="primary", key=f"btn_unblock_{target_user.id}"):
                                target_user.is_active = True
                                db.commit()
                                st.success(f"Le compte '{target_user.username}' a été réactivé !")
                                st.rerun()

                # --- BOUTON 3 : SUPPRESSION ---
                with col_action3:
                    st.markdown("#### ❌ Suppression")
                    if target_user.username == "admin":
                        st.info("Le compte admin principal ne peut pas être supprimé.")
                    else:
                        if st.button(f"Supprimer le compte", type="primary", key=f"del_user_{target_user.id}"):
                            db.delete(target_user)
                            db.commit()
                            st.error(f"Compte '{target_user.username}' supprimé !")
                            st.rerun()
        else:
            st.info("Aucun utilisateur trouvé.")
            
    finally:
        db.close()
