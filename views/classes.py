import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Classe, LogActivite

@st.cache_data(ttl=300)
def charger_classes_cache():
    db = SessionLocal()
    try:
        classes = db.query(Classe.id, Classe.nom, Classe.cycle, Classe.tarif_scolarite).all()
        return [{"id": c.id, "nom": c.nom, "cycle": c.cycle, "tarif_scolarite": c.tarif_scolarite} for c in classes]
    finally:
        db.close()

def afficher_classes(niveau_actif=None):
    st.subheader(f"🏫 Gestion des Classes - {niveau_actif if niveau_actif else 'Général'}")
    
    db = SessionLocal()
    try:
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
                    existe = db.query(Classe).filter(Classe.nom == nom.strip()).first()
                    if existe:
                        st.error("❌ Cette classe existe déjà.")
                    else:
                        nouvelle_classe = Classe(
                            nom=nom.strip(),
                            cycle=cycle,
                            tarif_scolarite=tarif_scolarite
                        )
                        db.add(nouvelle_classe)
                        
                        # Traçabilité dans le journal d'activité
                        db.add(LogActivite(
                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            utilisateur=st.session_state.get('user_role', 'Admin'),
                            action="SAISIE CLASSE",
                            details=f"Création de la classe '{nom.strip()}' ({cycle}) - Tarif: {tarif_scolarite:,.0f} FCFA"
                        ))
                        
                        db.commit()
                        st.cache_data.clear()
                        st.success("✅ Classe enregistrée avec succès !")
                else:
                    st.warning("⚠️ Veuillez indiquer le nom de la classe.")

        st.markdown("---")
        
        # --- ESPACE DE CORRECTION / MODIFICATION / SUPPRESSION ---
        with st.expander("🛠️ Modifier ou supprimer une classe existante"):
            classes = db.query(Classe).all()
            if classes:
                options_c = {f"ID {c.id} - {c.nom} ({c.cycle}) | Tarif: {c.tarif_scolarite:,.0f} FCFA": c.id for c in classes}
                choix_c = st.selectbox("Sélectionner la classe", list(options_c.keys()), key="select_classe_modif")
                c_id = options_c[choix_c]
                c_obj = db.query(Classe).filter(Classe.id == c_id).first()
                
                if c_obj:
                    action_type = st.radio("Action à effectuer", ["Modifier", "Supprimer"], horizontal=True, key="radio_action_classe")
                    
                    if action_type == "Modifier":
                        with st.form("form_modif_classe"):
                            nouveau_nom = st.text_input("Nom de la classe", value=c_obj.nom)
                            
                            idx_cycle = cycles_disponibles.index(c_obj.cycle) if c_obj.cycle in cycles_disponibles else 0
                            nouveau_cycle = st.selectbox("Cycle", cycles_disponibles, index=idx_cycle, key="mod_cycle")
                            
                            nouveau_tarif = st.number_input("Tarif annuel de scolarité (FCFA)", min_value=0.0, step=5000.0, value=float(c_obj.tarif_scolarite or 0.0))
                            
                            submit_modif = st.form_submit_button("💾 Mettre à jour la classe")
                            if submit_modif:
                                if nouveau_nom.strip():
                                    doublon = db.query(Classe).filter(Classe.nom == nouveau_nom.strip(), Classe.id != c_obj.id).first()
                                    if doublon:
                                        st.error("❌ Une autre classe porte déjà ce nom.")
                                    else:
                                        ancien_nom = c_obj.nom
                                        c_obj.nom = nouveau_nom.strip()
                                        c_obj.cycle = nouveau_cycle
                                        c_obj.tarif_scolarite = nouveau_tarif
                                        
                                        db.add(LogActivite(
                                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                            utilisateur=st.session_state.get('user_role', 'Admin'),
                                            action="MODIFICATION CLASSE",
                                            details=f"Modification de la classe ID {c_obj.id}: '{ancien_nom}' -> '{c_obj.nom}' ({nouveau_cycle}) - Tarif: {nouveau_tarif:,.0f} FCFA"
                                        ))
                                        db.commit()
                                        st.cache_data.clear()
                                        st.success(f"✅ La classe '{c_obj.nom}' a été mise à jour avec succès.")
                                else:
                                    st.warning("⚠️ Le nom de la classe ne peut pas être vide.")
                    
                    else:  # Suppression
                        if st.button("🗑️ Supprimer définitivement cette classe", type="primary", key="btn_suppr_classe"):
                            nom_classe = c_obj.nom
                            db.add(LogActivite(
                                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                utilisateur=st.session_state.get('user_role', 'Admin'),
                                action="SUPPRESSION CLASSE",
                                details=f"Suppression de la classe ID {c_obj.id} ({nom_classe})"
                            ))
                            db.delete(c_obj)
                            db.commit()
                            st.cache_data.clear()
                            st.success(f"✅ La classe '{nom_classe}' a été supprimée avec succès.")
            else:
                st.info("Aucune classe enregistrée à modifier ou supprimer.")

        st.markdown("---")
        
        # --- LISTE DES CLASSES ---
        st.write("### 📋 Liste des classes")
        toutes_classes = charger_classes_cache()
        if toutes_classes:
            data = [{
                "ID": c["id"],
                "Nom de la classe": c["nom"],
                "Cycle": c["cycle"],
                "Tarif Scolarité (FCFA)": f"{c['tarif_scolarite']:,.0f}".replace(",", " ") if c["tarif_scolarite"] else "0"
            } for c in toutes_classes]
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("Aucune classe enregistrée pour le moment.")
    finally:
        db.close()