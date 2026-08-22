import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime
from database.db_config import SessionLocal
from database.models import User, LogActivite

@st.cache_data(ttl=300)
def charger_utilisateurs_cache():
    db = SessionLocal()
    try:
        utilisateurs = db.query(User).all()
        return [{"id": u.id, "username": u.username, "role": u.role} for u in utilisateurs]
    finally:
        db.close()

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
                existe = db.query(User).filter(User.username == username.strip()).first()
                if existe:
                    st.error("❌ Ce nom d'utilisateur est déjà utilisé.")
                else:
                    # Hachage sécurisé du mot de passe avec bcrypt
                    sel = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), sel).decode('utf-8')
                    
                    nouveau_user = User(
                        username=username.strip(),
                        password=hashed_password,
                        role=role
                    )
                    db.add(nouveau_user)
                    
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="CRÉATION UTILISATEUR",
                        details=f"Création sécurisée du compte utilisateur : {username.strip()} (Rôle: {role})"
                    ))
                    
                    db.commit()
                    st.cache_data.clear()  # Vider le cache après l'ajout
                    st.success("✅ Compte utilisateur créé et sécurisé avec succès !")
                    st.rerun()
            else:
                st.warning("⚠️ Veuillez remplir le nom d'utilisateur et le mot de passe.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer un compte utilisateur"):
        utilisateurs_liste = charger_utilisateurs_cache()
        if utilisateurs_liste:
            options_u = {f"{u['username']} ({u['role']})": u['id'] for u in utilisateurs_liste}
            choix_u = st.selectbox("Sélectionner le compte à supprimer", list(options_u.keys()))
            
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
                    st.cache_data.clear()  # Vider le cache après suppression
                    st.success(f"✅ Le compte '{u_obj.username}' a été supprimé.")
                    st.rerun()
        else:
            st.info("Aucun utilisateur enregistré.")

    st.markdown("---")
    
    # --- LISTE DES COMPTES (Via le cache) ---
    st.write("### 📋 Liste des utilisateurs")
    tous_users = charger_utilisateurs_cache()
    if tous_users:
        data = [{
            "ID": u["id"],
            "Utilisateur": u["username"],
            "Rôle": u["role"]
        } for u in tous_users]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun utilisateur enregistré pour le moment.")
        
    db.close()