import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Message, Eleve, LogActivite

def afficher_messages(niveau_actif=None):
    st.subheader(f"💬 Messagerie et Communications - {niveau_actif or 'Général'}")
    
    db = SessionLocal()
    try:
        # --- FORMULAIRE D'ENVOI DE MESSAGE ---
        with st.form("form_message"):
            st.write("### Envoyer un message direct")
            
            eleves = db.query(Eleve).all()
            if eleves:
                options_eleves = {f"{e.nom} {e.prenom} (Mat: {e.matricule}) - Tél: {e.telephone or 'N/A'}": e.telephone for e in eleves}
                choix_eleve = st.selectbox("Choisir l'élève / Parent", list(options_eleves.keys()))
                telephone_dest = options_eleves[choix_eleve]
            else:
                telephone_dest = ""
                st.warning("⚠️ Aucun élève trouvé dans le système.")
            
            canal = st.selectbox("Canal direct", ["WhatsApp (Direct)", "SMS Interne"])
            sujet = st.text_input("Objet du message")
            contenu = st.text_area("Contenu du message")
            
            submitted = st.form_submit_button("Envoyer le message")
            if submitted:
                if contenu.strip():
                    try:
                        nouveau_msg = Message(
                            expediteur=st.session_state.get('username', 'Admin'),
                            destinataire=telephone_dest if telephone_dest else "Général",
                            sujet=sujet,
                            contenu=contenu,
                            date=datetime.now().strftime("%Y-%m-%d %H:%M")
                        )
                        db.add(nouveau_msg)
                        
                        # Traçabilité dans le journal d'activité
                        db.add(LogActivite(
                            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            utilisateur=st.session_state.get('user_role', 'Admin'),
                            action="ENVOI MESSAGE",
                            details=f"Message envoyé via {canal} - Sujet: {sujet}"
                        ))
                        
                        db.commit()
                        st.success("✅ Message enregistré et envoyé avec succès !")
                        db.close()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Erreur lors de l'envoi du message : {e}")
                else:
                    st.warning("⚠️ Veuillez saisir le contenu du message.")

        st.markdown("---")
        
        # --- HISTORIQUE DES MESSAGES ---
        st.write("### 📋 Historique des messages")
        messages = db.query(Message).order_by(Message.id.desc()).all()
        
        if messages:
            data_msg = [{
                "Date": m.date,
                "Expéditeur": m.expediteur,
                "Destinataire": m.destinataire,
                "Sujet": m.sujet or "Sans objet",
                "Contenu": m.contenu
            } for m in messages]
            st.dataframe(pd.DataFrame(data_msg), use_container_width=True)
        else:
            st.info("Aucun message dans l'historique pour le moment.")
            
    finally:
        db.close()
