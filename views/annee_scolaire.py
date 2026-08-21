import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import AnneeScolaire, LogActivite
from datetime import datetime

def afficher_annee_scolaire():
    st.subheader("📅 Gestion des Années Scolaires")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'AJOUT ---
    with st.form("form_annee"):
        st.write("### Ajouter une nouvelle année scolaire")
        libelle = st.text_input("Libellé (ex: 2026-2027)")
        activer_direct = st.checkbox("Définir comme année active par défaut", value=True)
        
        submitted = st.form_submit_button("Enregistrer l'année")
        if submitted:
            if libelle.strip():
                # Vérifier si l'année existe déjà
                existante = db.query(AnneeScolaire).filter(AnneeScolaire.libelle == libelle).first()
                if existante:
                    st.warning("⚠️ Cette année scolaire existe déjà.")
                else:
                    # Si on choisit de l'activer, on désactive les autres
                    if activer_direct:
                        db.query(AnneeScolaire).update({AnneeScolaire.active: False})
                    
                    nouvelle_annee = AnneeScolaire(
                        libelle=libelle.strip(),
                        active=activer_direct
                    )
                    db.add(nouvelle_annee)
                    
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="AJOUT ANNEE SCOLAIRE",
                        details=f"Création de l'année {libelle}"
                    ))
                    
                    db.commit()
                    st.success(f"✅ Année scolaire {libelle} enregistrée avec succès !")
                    st.rerun()
            else:
                st.warning("⚠️ Veuillez entrer un libellé valide.")

    st.markdown("---")
    
    # --- LISTE ET GESTION DES ANNÉES ---
    st.write("### 📋 Liste des Années Scolaires")
    annees = db.query(AnneeScolaire).all()
    
    if annees:
        for a in annees:
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(f"**{a.libelle}**")
            
            if a.active:
                col2.success("🟢 Active")
            else:
                col2.info("⚪ Inactive")
                
            if not a.active:
                if col3.button("Activer", key=f"act_{a.id}"):
                    # Désactiver toutes les autres
                    db.query(AnneeScolaire).update({AnneeScolaire.active: False})
                    # Activer celle-ci
                    a.active = True
                    db.commit()
                    st.success(f"✅ L'année {a.libelle} est désormais active.")
                    st.rerun()
        
        st.markdown("---")
        
        # --- SECTION SUPPRESSION ---
        with st.expander("🛠️ Supprimer une année scolaire"):
            options_a = {a.libelle: a.id for a in annees}
            choix_a = st.selectbox("Sélectionner l'année à supprimer", list(options_a.keys()))
            
            if st.button("🗑️ Supprimer cette année", type="primary"):
                a_id = options_a[choix_a]
                a_obj = db.query(AnneeScolaire).filter(AnneeScolaire.id == a_id).first()
                if a_obj:
                    db.delete(a_obj)
                    db.commit()
                    st.success("✅ Année supprimée avec succès !")
                    st.rerun()
    else:
        st.info("Aucune année scolaire enregistrée pour le moment. Veuillez en créer une ci-dessus.")
        
    db.close()