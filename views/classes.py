import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Classe, LogActivite

def afficher_classes(niveau_actif=None):
    st.subheader(f"🏫 Gestion des Classes - {niveau_actif if niveau_actif else 'Général'}")
    
    db = SessionLocal()
    
    # --- FORMULAIRE D'ENREGISTREMENT ---
    with st.form("form_classe"):
        st.write("### Créer une nouvelle classe")
        
        nom = st.text_input("Nom de la classe (ex: Terminale D, 3ème A)")
        
        cycles_disponibles = ["Primaire", "Collège", "Secondaire", "Lycée"]
        default_index = cycles_disponibles.index(niveau_actif) if niveau_actif in cycles_disponibles else 0
        cycle = st.selectbox("Cycle", cycles_disponibles, index=default_index)
        
        tarif_scolarite = st.number_input("Tarif annuel de scolarité (FCFA)", min_value=0.0, step=5000.0)
        
        submitted = st.form_submit_button("Enregistrer la classe")
        if submitted:
            if nom.strip():
                existe = db.query(Classe).filter(Classe.nom == nom).first()
                if existe:
                    st.error("❌ Cette classe existe déjà.")
                else:
                    nouvelle_classe = Classe(
                        nom=nom,
                        cycle=cycle,
                        tarif_scolarite=tarif_scolarite
                    )
                    db.add(nouvelle_classe)
                    
                    # Traçabilité dans le journal d'activité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SAISIE CLASSE",
                        details=f"Création de la classe '{nom}' ({cycle}) - Tarif: {tarif_scolarite:,.0f} FCFA"
                    ))
                    
                    db.commit()
                    st.success("✅ Classe enregistrée avec succès !")
                    st.rerun()
            else:
                st.warning("⚠️ Veuillez indiquer le nom de la classe.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger une classe erronée"):
        classes = db.query(Classe).all()
        if classes:
            options_c = {f"ID {c.id} - {c.nom} ({c.cycle}) | Tarif: {c.tarif_scolarite:,.0f} FCFA": c.id for c in classes}
            choix_c = st.selectbox("Sélectionner la classe à supprimer", list(options_c.keys()))
            
            if st.button("🗑️ Supprimer définitivement cette classe", type="primary"):
                c_id = options_c[choix_c]
                c_obj = db.query(Classe).filter(Classe.id == c_id).first()
                if c_obj:
                    nom_classe = c_obj.nom
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION CLASSE",
                        details=f"Suppression de la classe ID {c_obj.id} ({nom_classe})"
                    ))
                    db.delete(c_obj)
                    db.commit()
                    st.success(f"✅ La classe '{nom_classe}' a été supprimée avec succès.")
                    st.rerun()
        else:
            st.info("Aucune classe enregistrée à corriger.")

    st.markdown("---")
    
    # --- LISTE DES CLASSES ---
    st.write("### 📋 Liste des classes")
    toutes_classes = db.query(Classe).all()
    if toutes_classes:
        data = [{
            "ID": c.id,
            "Nom de la classe": c.nom,
            "Cycle": c.cycle,
            "Tarif Scolarité (FCFA)": f"{c.tarif_scolarite:,.0f}".replace(",", " ") if c.tarif_scolarite else "0"
        } for c in toutes_classes]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucune classe enregistrée pour le moment.")
        
    db.close()