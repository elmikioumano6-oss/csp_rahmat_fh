import streamlit as st
from database.db_config import SessionLocal
from database.models import User, Enseignant, Eleve

def afficher_gestion_utilisateurs():
    st.subheader("⚙️ Gestion des Comptes Utilisateurs")
    db = SessionLocal()

    # Formulaire de création
    with st.expander("➕ Créer un nouvel utilisateur"):
        with st.form("form_create_user"):
            username = st.text_input("Nom d'utilisateur (Identifiant de connexion)")
            password = st.text_input("Mot de passe", type="password")
            role = st.selectbox("Rôle", ["admin", "proviseur", "prof", "parent"])
            
            entite_id = None
            
            # Logique dynamique : on affiche les listes selon le rôle choisi
            if role == "prof":
                profs = db.query(Enseignant).all()
                if profs:
                    choix_prof = st.selectbox("Choisir l'enseignant à lier", profs, format_func=lambda x: f"{x.nom} {x.prenom}")
                    entite_id = choix_prof.id
                else:
                    st.warning("Aucun enseignant trouvé en base.")
            
            elif role == "parent":
                eleves = db.query(Eleve).all()
                if eleves:
                    choix_eleve = st.selectbox("Lier au compte de l'élève (Parent)", eleves, format_func=lambda x: f"{x.nom} {x.prenom} (Mat: {x.matricule})")
                    entite_id = choix_eleve.id
                else:
                    st.warning("Aucun élève trouvé en base.")

            if st.form_submit_button("Créer le compte"):
                if not username or not password:
                    st.error("Veuillez remplir tous les champs.")
                elif db.query(User).filter(User.username == username).first():
                    st.error("Ce nom d'utilisateur existe déjà.")
                else:
                    new_user = User(
                        username=username, 
                        password=password, 
                        role=role, 
                        entite_id=entite_id
                    )
                    db.add(new_user)
                    db.commit()
                    st.success(f"Compte '{username}' ({role}) créé avec succès !")
                    st.rerun()

    # Affichage de la liste des comptes existants
    st.markdown("---")
    st.markdown("### 📋 Liste des comptes créés")
    utilisateurs = db.query(User).all()
    
    if utilisateurs:
        data = [{"ID": u.id, "Utilisateur": u.username, "Rôle": u.role, "Lien Entité ID": u.entite_id} for u in utilisateurs]
        st.table(data)
    else:
        st.info("Aucun compte utilisateur trouvé.")
    
    db.close()
