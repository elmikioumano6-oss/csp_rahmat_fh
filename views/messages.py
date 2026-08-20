import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Message, Enseignant, Personnel, Eleve

def afficher_messages(niveau_actif=None):
    st.subheader(f"💬 Messagerie Directe & Canaux - {niveau_actif}")
    
    db = SessionLocal()
    
    # Initialisation de l'état pour les liens d'action externe
    if 'action_link' not in st.session_state: st.session_state['action_link'] = None
    if 'action_type' not in st.session_state: st.session_state['action_type'] = None

    # Choix du mode hors du formulaire pour une interactivité instantanée
    mode = st.radio("Type de destinataire", ["Groupe (Diffusion)", "Individuel (Spécifique)"], horizontal=True)
    
    with st.form("form_message"):
        st.write("### Envoyer une communication / un message")
        
        destinataire_nom = "Inconnu"
        numero_tel = ""
        canal = ""
        form_valid = True

        if mode == "Groupe (Diffusion)":
            destinataire_nom = st.selectbox("Sélectionner le groupe", ["Tous les parents", "Tous les professeurs", "Tout le personnel"])
            canal = st.selectbox("Canal de diffusion", ["Espace Parent", "WhatsApp (Groupe)", "Affichage Panneau"])
        else:
            categorie = st.selectbox("Catégorie", ["Parent (Élève)", "Professeur", "Personnel"])
            
            if categorie == "Parent (Élève)":
                liste = db.query(Eleve).filter(Eleve.telephone != None, Eleve.telephone != "").all()
                if liste:
                    options = [f"{e.nom} {e.prenom} - {e.telephone}" for e in liste]
                    selection = st.selectbox("Choisir l'élève (Parent)", options)
                    if selection:
                        destinataire_nom = selection.split(" - ")[0]
                        numero_tel = selection.split(" - ")[1]
                else:
                    st.warning("⚠️ Aucun élève n'a de numéro de téléphone enregistré.")
                    form_valid = False
                    
            elif categorie == "Professeur":
                liste = db.query(Enseignant).filter(Enseignant.telephone != None, Enseignant.telephone != "").all()
                if liste:
                    options = [f"{e.nom} {e.prenom} - {e.telephone}" for e in liste]
                    selection = st.selectbox("Choisir le professeur", options)
                    if selection:
                        destinataire_nom = selection.split(" - ")[0]
                        numero_tel = selection.split(" - ")[1]
                else:
                    st.warning("⚠️ Aucun professeur n'a de numéro de téléphone enregistré.")
                    form_valid = False
                    
            else:
                liste = db.query(Personnel).filter(Personnel.telephone != None, Personnel.telephone != "").all()
                if liste:
                    options = [f"{p.nom} {p.prenom} - {p.telephone}" for p in liste]
                    selection = st.selectbox("Choisir le membre du personnel", options)
                    if selection:
                        destinataire_nom = selection.split(" - ")[0]
                        numero_tel = selection.split(" - ")[1]
                else:
                    st.warning("⚠️ Aucun membre du personnel n'a de numéro de téléphone enregistré.")
                    form_valid = False
                
            canal = st.selectbox("Canal direct", ["Espace Parent", "WhatsApp (Direct)", "SMS (Direct)"])

        objet = st.text_input("Objet du message")
        contenu = st.text_area("Contenu du message")
        
        submitted = st.form_submit_button("Enregistrer et préparer l'envoi")
        
        if submitted:
            if not form_valid and mode == "Individuel (Spécifique)":
                st.error("❌ Impossible d'envoyer : aucun contact avec un numéro valide n'est sélectionné.")
            elif objet.strip() and contenu.strip():
                # 1. Enregistrement officiel de la trace dans la base de données
                nouveau_msg = Message(
                    expediteur="Administration",
                    destinataire=f"{destinataire_nom} ({canal})",
                    objet=objet,
                    contenu=contenu,
                    date=datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                db.add(nouveau_msg)
                db.commit()
                st.success("✅ Message archivé en base avec succès !")
                
                # 2. Formatage du texte selon le canal
                if "SMS" in canal:
                    full_text = f"[{objet}] {contenu}"
                else:
                    full_text = f"📢 *{objet}*\n\n{contenu}\n\n(CSP RAHMAT-FH)"
                    
                encoded_text = urllib.parse.quote(full_text)
                
                # 3. Génération du lien d'action externe (WhatsApp ou SMS)
                if "WhatsApp" in canal:
                    if mode == "Individuel (Spécifique)" and numero_tel:
                        st.session_state['action_link'] = f"https://wa.me/{numero_tel}?text={encoded_text}"
                    else:
                        st.session_state['action_link'] = f"https://wa.me/?text={encoded_text}"
                    st.session_state['action_type'] = "WhatsApp"
                elif "SMS" in canal and numero_tel:
                    st.session_state['action_link'] = f"sms:{numero_tel}?body={encoded_text}"
                    st.session_state['action_type'] = "SMS"
                else:
                    st.session_state['action_link'] = None
                    st.session_state['action_type'] = None
            else:
                st.warning("⚠️ Veuillez remplir tous les champs.")

    # Affichage du bouton d'action externe (hors formulaire)
    if st.session_state['action_link']:
        st.markdown("---")
        if st.session_state['action_type'] == "WhatsApp":
            st.info(f"🚀 Prêt à envoyer sur WhatsApp vers : **{numero_tel if mode == 'Individuel (Spécifique)' else 'Groupe'}**")
            st.link_button("👉 Ouvrir WhatsApp", st.session_state['action_link'])
        elif st.session_state['action_type'] == "SMS":
            st.info(f"📱 Prêt à envoyer par SMS vers le numéro : **{numero_tel}**")
            st.link_button("👉 Ouvrir l'application SMS", st.session_state['action_link'])
            
        if st.button("Fermer l'action"):
            st.session_state['action_link'] = None
            st.session_state['action_type'] = None
            st.rerun()

    st.markdown("---")
    st.write("### 📨 Historique des messages et diffusions")
    messages = db.query(Message).order_by(Message.id.desc()).all()
    if messages:
        data = [{"Date": m.date, "Destinataire": m.destinataire, "Objet": m.objet, "Contenu": m.contenu} for m in messages]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("Aucun message enregistré pour le moment.")
        
    db.close()