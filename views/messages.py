import streamlit as st
import pandas as pd
from datetime import datetime
from urllib.parse import quote
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
            
            submitted = st.form_submit_button("Enregistrer et Préparer l'envoi")
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
                            details=f"Message enregistré via {canal} - Sujet: {sujet}"
                        ))
                        
                        db.commit()
                        
                        # Stocker dans session_state pour afficher le bouton d'envoi externe instantanément
                        st.session_state['dernier_message'] = {
                            'telephone': telephone_dest,
                            'contenu': f"[{sujet}] {contenu}" if sujet else contenu,
                            'canal': canal
                        }
                        st.success("✅ Message enregistré dans l'historique avec succès !")
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Erreur lors de l'enregistrement : {e}")
                else:
                    st.warning("⚠️ Veuillez saisir le contenu du message.")

        # --- BOUTON D'OUVERTURE DIRECTE WHATSAPP / SMS ---
        if 'dernier_message' in st.session_state:
            msg_info = st.session_state['dernier_message']
            tel = msg_info['telephone']
            texte = msg_info['contenu']
            canal_choisi = msg_info['canal']
            
            if tel:
                # Nettoyage du numéro de téléphone
                tel_clean = "".join(filter(str.isdigit, tel))
                # Ajout automatique de l'indicatif du Niger (+227) si le numéro comporte 8 chiffres
                if len(tel_clean) == 8:
                    tel_clean = "227" + tel_clean
                
                encoded_text = quote(texte)
                
                st.markdown("---")
                st.info("🚀 **Action rapide : Ouvrir l'application externe pour envoyer**")
                
                if "WhatsApp" in canal_choisi:
                    wa_url = f"https://wa.me/{tel_clean}?text={encoded_text}"
                    st.markdown(f"""
                        <a href="{wa_url}" target="_blank" style="display:inline-block;padding:12px 20px;background-color:#25D366;color:white;text-decoration:none;border-radius:6px;font-weight:bold;font-size:16px;">
                            📲 Cliquer ici pour envoyer via WhatsApp
                        </a>
                    """, unsafe_allow_html=True)
                else:
                    sms_url = f"sms:{tel_clean}?body={encoded_text}"
                    st.markdown(f"""
                        <a href="{sms_url}" style="display:inline-block;padding:12px 20px;background-color:#007BFF;color:white;text-decoration:none;border-radius:6px;font-weight:bold;font-size:16px;">
                            📱 Cliquer ici pour envoyer par SMS
                        </a>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Aucun numéro de téléphone associé à cet élève pour un envoi direct.")

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
