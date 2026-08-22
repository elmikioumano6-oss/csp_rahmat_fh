import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Eleve, Classe, Note, Matiere, LogActivite
from datetime import datetime
import urllib.parse

def afficher_alerte_performance(niveau_actif):
    st.subheader(f"🚨 Censeur Numérique - Alerte & Suivi Pédagogique ({niveau_actif})")
    st.markdown("Détection automatique des élèves en difficulté académique (moyenne inférieure au seuil critique) pour un accompagnement proactif.")

    db = SessionLocal()

    # Récupérer les classes du cycle actif
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    if not classes:
        st.warning(f"⚠️ Aucune classe trouvée pour le cycle {niveau_actif}.")
        db.close()
        return

    options_classes = {c.nom: c.id for c in classes}
    classe_nom = st.selectbox("Sélectionner la classe à auditer", list(options_classes.keys()))
    classe_id = options_classes[classe_nom]

    # Seuil d'alerte personnalisable
    seuil_alerte = st.slider("Seuil critique de moyenne (sur 20)", min_value=5.0, max_value=12.0, value=9.0, step=0.5)

    eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
    if not eleves:
        st.info("Aucun élève dans cette classe.")
        db.close()
        return

    matieres = db.query(Matiere).all()

    eleves_en_difficulte = []

    for eleve in eleves:
        notes = db.query(Note).filter(Note.eleve_id == eleve.id).all()
        eleve_pts, eleve_coefs = 0, 0

        for n in notes:
            mat = db.query(Matiere).filter(Matiere.id == n.matiere_id).first()
            c = getattr(mat, "coefficient", 1) or 1
            nc = n.note_classe or 0
            nco = n.note_compo or 0
            m = (
                (nc + (nco * 2)) / 3
                if (n.note_classe is not None and n.note_compo is not None)
                else (nc or nco)
            )
            eleve_pts += m * c
            eleve_coefs += c

        moyenne_generale = round(eleve_pts / eleve_coefs, 2) if eleve_coefs > 0 else 0.0

        if moyenne_generale < seuil_alerte:
            eleves_en_difficulte.append({
                "id": eleve.id,
                "Matricule": eleve.matricule,
                "Nom": eleve.nom,
                "Prénom": eleve.prenom,
                "Téléphone Parent": eleve.telephone or "Non renseigné",
                "Moyenne Générale": moyenne_generale
            })

    st.markdown("---")
    st.markdown(f"### 📋 Résultats de l'analyse (Seuil : < {seuil_alerte}/20)")

    if eleves_en_difficulte:
        df_alerte = pd.DataFrame(eleves_en_difficulte)
        st.dataframe(df_alerte[["Matricule", "Nom", "Prénom", "Téléphone Parent", "Moyenne Générale"]], use_container_width=True, hide_index=True)

        st.markdown("### ✉️ Action Rapide : Convocation ou Alerte Parentale")
        choix_eleve = st.selectbox("Sélectionner l'élève concerné", [f"{e['Nom']} {e['Prénom']} ({e['Moyenne Générale']}/20)" for e in eleves_en_difficulte])
        
        # Retrouver l'élève sélectionné
        index_choix = [f"{e['Nom']} {e['Prénom']} ({e['Moyenne Générale']}/20)" for e in eleves_en_difficulte].index(choix_eleve)
        eleve_cible = eleves_en_difficulte[index_choix]

        message_defaut = f"CSP RAHMAT-FH - Avertissement Pédagogique : Votre enfant {eleve_cible['Nom']} {eleve_cible['Prénom']} obtient actuellement une moyenne générale de {eleve_cible['Moyenne Générale']}/20 dans la classe de {classe_nom}. Merci de bien vouloir passer d'urgence à l'établissement pour un entretien avec le Censeur."
        
        contenu_msg = st.text_area("Message de convocation", value=message_defaut)

        if eleve_cible["Téléphone Parent"] != "Non renseigné":
            texte_wa = urllib.parse.quote(contenu_msg)
            url_whatsapp = f"https://wa.me/{eleve_cible['Téléphone Parent']}?text={texte_wa}"
            st.markdown(f"📱 **[Envoyer l'alerte par WhatsApp au parent ({eleve_cible['Téléphone Parent']})]({url_whatsapp})**", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Aucun numéro de téléphone valide enregistré pour le parent de cet élève.")

        if st.button("🛡️ Enregistrer l'action dans le Journal d'Audit", type="primary"):
            db.add(LogActivite(
                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                utilisateur=st.session_state.get('user_role', 'Admin'),
                action="ALERTE PEDAGOGIQUE",
                details=Habillage := f"Génération d'alerte de performance pour l'élève {eleve_cible['Nom']} {eleve_cible['Prénom']} (Moyenne: {eleve_cible['Moyenne Générale']})"
            ))
            db.commit()
            st.success("✅ Action enregistrée avec succès dans le journal de traçabilité !")
    else:
        st.success(f"🎉 Excellent ! Aucun élève n'est en dessous du seuil de {seuil_alerte}/20 dans cette classe.")

    db.close()