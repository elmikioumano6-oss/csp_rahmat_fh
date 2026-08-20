import streamlit as st
from database.db_config import SessionLocal
from database.models import User, Enseignant, Eleve

def afficher_gestion_utilisateurs():
    st.subheader("⚙️ Gestion des Comptes Utilisateurs")
    db = SessionLocal()

    # --- PARTIE CRÉATION (Inchangée) ---
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
                    choix_eleve = st.selectbox("Lier à l'élève", eleves, format_func=lambda x: f"{x.nom} {x.prenom}")
                    entite_id = choix_eleve.id

            if st.form_submit_button("Créer le compte"):
                if db.query(User).filter(User.username == username).first():
                    st.error("Ce nom existe déjà.")
                else:
                    db.add(User(username=username, password=password, role=role, entite_id=entite_id))
                    db.commit()
                    st.success("Compte créé !")
                    st.rerun()

    # --- PARTIE GESTION (Suppression / Réinitialisation) ---
    st.markdown("---")
    st.markdown("### 📋 Liste et Gestion des comptes")
    
    users = db.query(User).all()
    for user in users:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        col1.write(f"**{user.username}** ({user.role})")
        
        # Bouton Suppression
        if col2.button("❌", key=f"del_{user.id}"):
            if user.username == "admin":
                st.error("Impossible de supprimer l'admin !")
            else:
                db.delete(user)
                db.commit()
                st.rerun()
        
        # Réinitialisation MDP
        new_pass = col4.text_input("Nouv. MDP", type="password", key=f"pass_{user.id}")
        if col3.button("🔄", key=f"reset_{user.id}"):
            if new_pass:
                user.password = new_pass
                db.commit()
                st.success(f"MDP mis à jour pour {user.username}")
                st.rerun()
            else:
                st.warning("Entrez un MDP")

    db.close()
