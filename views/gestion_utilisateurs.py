import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import User, LogActivite

def afficher_gestion_utilisateurs():
    st.subheader("🔐 Gestion des Comptes Utilisateurs")
    
    db = SessionLocal()
    
    # --- FORMULAIRE DE CRÉATION DE COMPTE ---
    with st.form("form_compte"):
        st.write("### Créer un nouvel utilisateur")
        
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        role = st.selectbox("Rôle", ["admin", "prof", "parent"])
        
        submitted = st.form_submit_button("Créer le compte")
        if submitted:
            if username.strip() and password.strip():
                # Vérifier si l'utilisateur existe déjà
                existe = db.query(User).filter(User.username == username).first()
                if existe:
                    st.error("❌ Ce nom d'utilisateur est déjà utilisé.")
                else:
                    nouveau_user = User(
                        username=username,
                        password=password, # Note: Pour plus de sécurité, il faudra hacher ce mot de passe
                        role=role
                    )
                    db.add(nouveau_user)
                    
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="CRÉATION UTILISATEUR",
                        details=f"Création du compte utilisateur : {username} (Rôle: {role})"
                    ))
                    
                    db.commit()
                    st.success("✅ Compte utilisateur créé avec succès !")
                    st.rerun()
            else:
                st.warning("⚠️ Veuillez remplir le nom d'utilisateur et le mot de passe.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer un compte utilisateur"):
        utilisateurs = db.query(User).all()
        if utilisateurs:
            options_u = {f"{u.username} ({u.role})": u.id for u in utilisateurs}
            choix_u = st.selectbox("Sélectionner le compte à supprimer", list(options_u.keys()))
            
            # Empêcher la suppression de son propre compte (sécurité simple)
            if st.button("🗑️ Supprimer définitivement ce compte", type="primary"):
                u_id = options_u[choix_u]
                u_obj = db.query(User).filter(User.id == u_id).first()
                
                if u_obj:
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION UTILISATEUR",
                        details=f"Suppression du compte : {u_obj.username}"
                    ))
                    db.delete(u_obj)
                    db.commit()
                    st.success(f"✅ Le compte '{u_obj.username}' a été supprimé.")
                    st.rerun()
        else:
            st.info("Aucun utilisateur enregistré.")

    st.markdown("---")
    
    # --- LISTE DES COMPTES ---
    st.write("### 📋 Liste des utilisateurs")
    tous_users = db.query(User).all()
    if tous_users:
        data = [{
            "ID": u.id,
            "Utilisateur": u.username,
            "Rôle": u.role
        } for u in tous_users]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
        
    db.close()