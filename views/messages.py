import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Message, Eleve, Classe, LogActivite
import urllib.parse

def afficher_messages(niveau_actif=None):
    st.subheader("💬 Centre de Communication & Alertes SMS/WhatsApp")
    st.markdown("Communiquez instantanément avec les parents d'élèves pour les absences, les notes ou les rappels financiers.")

    db = SessionLocal()

    tab1, tab2 = st.tabs(["✉️ Envoyer un message", "📋 Historique des messages"])

    with tab1:
        st.write("### Nouveau message aux parents")
        
        eleves = db.query(Eleve).all()
        if not eleves:
            st.warning("⚠️ Aucun élève enregistré.")
            db.close()
            return

        # Option d'envoi (Individuel ou Diffusion générale)
        mode_envoi = st.radio("Mode de diffusion", ["Élève spécifique", "Diffusion à toute une classe"], horizontal=True)

        if mode_envoi == "Élève spécifique":
            options_eleves = {f"{e.nom} {e.prenom} (Matricule: {e.matricule})": e for e in eleves}
            choix_eleve_str = st.selectbox("Sélectionner l'élève", list(options_eleves.keys()))
            eleve_cible = options_eleves[choix_eleve_str]
            destinataires = [eleve_cible]
        else:
            classes = db.query(Classe).all()
            options_classes = {c.nom: c.id for c in classes}
            if not options_classes:
                st.warning("⚠️ Aucune classe disponible.")
                db.close()
                return
            classe_nom_choisie = st.selectbox("Sélectionner la classe", list(options_classes.keys()))
            classe_id = options_classes[classe_nom_choisie]
            destinataires = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()

        sujet = st.selectbox("Objet du message", [
            "Alerte Absence / Retard", 
            "Rappel de Paiement de Scolarité", 
            "Performance Académique / Note", 
            "Information Générale de l'École"
        ])
        
        contenu = st.text_area("Contenu du message", placeholder="Écrivez votre message ici...")

        if st.button("🚀 Générer les alertes / Envoyer", type="primary", use_container_width=True):
            if not contenu:
                st.error("Le contenu du message ne peut pas être vide.")
            else:
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                for eleve in destinataires:
                    nouveau_msg = Message(
                        expediteur="Administration CSP RAHMAT-FH",
                        destinataire=f"Parent de {eleve.nom} {eleve.prenom}",
                        sujet=sujet,
                        contenu=contenu,
                        date=date_str
                    )
                    db.add(nouveau_msg)
                
                # Traçabilité
                db.add(LogActivite(
                    date=date_str,
                    utilisateur=st.session_state.get('user_role', 'Admin'),
                    action="ENVOI MESSAGE",
                    details=f"Diffusion objet: '{sujet}' à {len(destinataires)} destinataire(s)"
                ))
                db.commit()
                st.success(f"✅ Messages enregistrés avec succès pour {len(destinataires)} élève(s) !")

                if len(destinataires) == 1 and destinataires[0].telephone:
                    tel = destinataires[0].telephone
                    texte_wa = urllib.parse.quote(f"CSP RAHMAT-FH - {sujet}\n\n{contenu}")
                    url_whatsapp = f"https://wa.me/{tel}?text={texte_wa}"
                    st.markdown(f"📱 **[Cliquer ici pour envoyer l'alerte par WhatsApp directement au parent ({tel})]({url_whatsapp})**", unsafe_allow_html=True)

    with tab2:
        st.write("### Historique des communications")
        messages = db.query(Message).order_by(Message.id.desc()).all()
        if messages:
            data = [{
                "Date": m.date,
                "De": m.expediteur,
                "À": m.destinataire,
                "Sujet": m.sujet,
                "Contenu": m.contenu
            } for m in messages]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("Aucun message dans l'historique.")

    db.close()