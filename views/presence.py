import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Presence, Eleve, Classe, LogActivite

def afficher_presence():
    st.subheader("✅ Gestion des Présences")
    
    db = SessionLocal()
    
    # --- FORMULAIRE DE SAISIE DE PRÉSENCE ---
    with st.form("form_presence"):
        st.write("### Enregistrer une présence/absence")
        
        # Sélection classe pour filtrer les élèves
        classes = db.query(Classe).all()
        options_classes = {c.nom: c.id for c in classes}
        classe_nom = st.selectbox("Classe", list(options_classes.keys()))
        classe_id = options_classes[classe_nom]
        
        eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
        if eleves:
            options_eleves = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in eleves}
            eleve_label = st.selectbox("Élève", list(options_eleves.keys()))
            eleve_id = options_eleves[eleve_label]
            
            date_presence = st.date_input("Date", value=datetime.today())
            statut = st.selectbox("Statut", ["Présent", "Absent", "Retard"])
            
            submitted = st.form_submit_button("Enregistrer la présence")
            if submitted:
                # Vérifier si une entrée existe déjà pour ce jour
                date_str = date_presence.strftime("%Y-%m-%d")
                existe = db.query(Presence).filter(Presence.eleve_id == eleve_id, Presence.date == date_str).first()
                
                if existe:
                    existe.statut = statut
                    action_str = "MODIFICATION PRÉSENCE"
                else:
                    nouvelle_pres = Presence(eleve_id=eleve_id, date=date_str, statut=statut)
                    db.add(nouvelle_pres)
                    action_str = "SAISIE PRÉSENCE"
                
                # Traçabilité
                db.add(LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get('user_role', 'Admin'),
                    action=action_str,
                    details=f"Élève ID {eleve_id} le {date_str} : {statut}"
                ))
                
                db.commit()
                st.success(f"✅ Présence enregistrée ({statut}) !")
                st.rerun()
        else:
            st.info("Aucun élève dans cette classe.")

    st.markdown("---")
    
    # --- ESPACE DE CORRECTION / SUPPRESSION ---
    with st.expander("🛠️ Supprimer ou corriger une présence erronée"):
        presences = db.query(Presence).order_by(Presence.date.desc()).all()
        if presences:
            options_p = {f"{p.date} | {p.eleve.nom} {p.eleve.prenom} | {p.statut}": p.id for p in presences}
            choix_p = st.selectbox("Sélectionner l'entrée à supprimer", list(options_p.keys()))
            
            if st.button("🗑️ Supprimer définitivement cette présence", type="primary"):
                p_id = options_p[choix_p]
                p_obj = db.query(Presence).filter(Presence.id == p_id).first()
                if p_obj:
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION PRÉSENCE",
                        details=f"Suppression présence ID {p_obj.id} ({p_obj.eleve.nom} - {p_obj.date})"
                    ))
                    db.delete(p_obj)
                    db.commit()
                    st.success("✅ Entrée supprimée et action tracée avec succès !")
                    st.rerun()
        else:
            st.info("Aucune présence enregistrée à corriger.")

    st.markdown("---")
    
    # --- HISTORIQUE ---
    st.write("### 📋 Historique des présences")
    toutes_pres = db.query(Presence).order_by(Presence.date.desc()).all()
    if toutes_pres:
        data = [{
            "Date": p.date,
            "Élève": f"{p.eleve.nom} {p.eleve.prenom}",
            "Statut": p.statut
        } for p in toutes_pres]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    
    db.close()