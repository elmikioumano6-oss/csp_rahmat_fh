import streamlit as st
import os
from datetime import datetime
from database.db_config import SessionLocal
from database.models import Eleve, Classe, LogActivite

def afficher_import_photos_masse(niveau_actif):
    st.subheader(f"📂 Importation et Gestion Groupée des Photos - {niveau_actif}")
    db = SessionLocal()

    # Récupérer les classes du cycle actif
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    if not classes:
        st.warning("⚠️ Aucune classe trouvée pour ce cycle.")
        db.close()
        return

    options_classes = {c.nom: c.id for c in classes}
    choix_classe_nom = st.selectbox("Sélectionner la classe cible :", list(options_classes.keys()))
    classe_id = options_classes[choix_classe_nom]

    eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
    if not eleves:
        st.warning("⚠️ Aucun élève trouvé dans cette classe.")
        db.close()
        return

    st.markdown("---")
    st.info("💡 **Consigne :** Glissez-déposez ou sélectionnez plusieurs photos en même temps. Nommez vos fichiers exactement avec le **matricule de l'élève** (Exemple : `E001.jpg` ou `MAT123.png`).")

    photos_uploadees = st.file_uploader(
        "Sélectionnez les photos des élèves",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    dossier_photos = "photos_eleves"
    os.makedirs(dossier_photos, exist_ok=True)

    if photos_uploadees:
        succes_count = 0
        if st.button("🚀 Lancer l'association automatique", type="primary"):
            for uploaded_file in photos_uploadees:
                # Extraire le matricule du nom du fichier (ex: E001.jpg -> E001)
                nom_fichier = uploaded_file.name
                matricule_fichier = os.path.splitext(nom_fichier)[0].strip().upper()

                # Chercher l'élève correspondant dans la classe
                eleve_correspondant = next((e for e in eleves if e.matricule.upper() == matricule_fichier), None)

                if eleve_correspondant:
                    extension = os.path.splitext(nom_fichier)[1]
                    chemin_destination = os.path.join(dossier_photos, f"{eleve_correspondant.matricule}{extension}")
                    
                    # Supprimer l'ancienne photo du disque si elle existait déjà
                    if eleve_correspondant.photo and os.path.exists(eleve_correspondant.photo):
                        try:
                            os.remove(eleve_correspondant.photo)
                        except:
                            pass

                    # Enregistrer le nouveau fichier
                    with open(chemin_destination, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Mettre à jour le champ photo dans l'objet Élève
                    eleve_correspondant.photo = chemin_destination
                    succes_count += 1
            
            # Enregistrer l'action dans le journal d'activité
            db.add(LogActivite(
                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                utilisateur=st.session_state.get('user_role', 'Admin'),
                action="IMPORTATION PHOTOS MASSE",
                details=f"Importation de {succes_count} photo(s) pour la classe de {choix_classe_nom}"
            ))
            db.commit()
            
            st.success(f"🎉 Opération réussie ! {succes_count} photo(s) associée(s) avec succès pour la classe de {choix_classe_nom}.")
            st.rerun()

    st.markdown("---")

    # --- ESPACE DE CORRECTION / SUPPRESSION DES PHOTOS ---
    with st.expander("🛠️ Supprimer ou réinitialiser les photos de cette classe"):
        eleves_avec_photo = [e for e in eleves if e.photo and os.path.exists(e.photo)]
        if eleves_avec_photo:
            options_eleves_p = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in eleves_avec_photo}
            choix_suppr = st.selectbox("Sélectionner l'élève dont il faut retirer la photo", list(options_eleves_p.keys()))
            
            col_del1, col_del2 = st.columns(2)
            
            if col_del1.button("🗑️ Supprimer la photo de cet élève", type="primary"):
                e_id = options_eleves_p[choix_suppr]
                e_obj = db.query(Eleve).filter(Eleve.id == e_id).first()
                if e_obj and e_obj.photo:
                    if os.path.exists(e_obj.photo):
                        os.remove(e_obj.photo)
                    
                    # Traçabilité
                    db.add(LogActivite(
                        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        utilisateur=st.session_state.get('user_role', 'Admin'),
                        action="SUPPRESSION PHOTO",
                        details=f"Suppression de la photo de l'élève {e_obj.nom} {e_obj.prenom} ({e_obj.matricule})"
                    ))
                    
                    e_obj.photo = None
                    db.commit()
                    st.success("✅ Photo de l'élève supprimée avec succès !")
                    st.rerun()
            
            if col_del2.button("🗑️ Tout réinitialiser pour cette classe"):
                for e in eleves_avec_photo:
                    if os.path.exists(e.photo):
                        os.remove(e.photo)
                    e.photo = None
                
                # Traçabilité
                db.add(LogActivite(
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    utilisateur=st.session_state.get('user_role / Admin'),
                    action="RÉINITIALISATION PHOTOS",
                    details=f"Suppression de toutes les photos pour la classe {choix_classe_nom}"
                ))
                db.commit()
                st.success("✅ Toutes les photos de cette classe ont été réinitialisées !")
                st.rerun()
        else:
            st.info("Aucun élève de cette classe n'a de photo enregistrée pour le moment.")

    db.close()