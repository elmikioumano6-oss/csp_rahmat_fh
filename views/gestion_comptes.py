import streamlit as st
import bcrypt
from database.db_config import SessionLocal
from database.models import User

@st.cache_data(ttl=300)
def charger_utilisateurs_cache():
    db = SessionLocal()
    try:
        users = db.query(User.id, User.username, User.role).all()
        return [{"id": u.id, "username": u.username, "role": u.role} for u in users]
    finally:
        db.close()

def afficher_gestion_utilisateurs():
    st.subheader("👥 Gestion des Comptes (Parents & Profs)")
    db = SessionLocal()

    with st.form("ajout_compte"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        role = st.selectbox("Rôle", ["prof", "parent"])
        submit = st.form_submit_button("Créer le compte")

        if submit:
            if db.query(User).filter(User.username == username).first():
                st.error("Ce nom d'utilisateur existe déjà !")
            else:
                sel = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), sel).decode('utf-8')
                nouveau_user = User(username=username, password=hashed, role=role)
                db.add(nouveau_user)
                db.commit()
                st.cache_data.clear()  # Vider le cache après l'ajout d'un utilisateur
                st.success(f"Compte {role} créé avec succès !")
                st.rerun()
    
    st.write("---")
    st.write("Liste des comptes existants")
    users = charger_utilisateurs_cache()
    if users:
        st.table([{"ID": u["id"], "User": u["username"], "Rôle": u["role"]} for u in users])
    else:
        st.info("Aucun compte enregistré.")
        
    db.close()