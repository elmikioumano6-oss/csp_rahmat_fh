import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import Eleve, Inscription, Classe, AnneeScolaire

def afficher_scolarite(cycle_actif):
    st.markdown(f"<div class='page-title-orange'>Scolarité - {cycle_actif}</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        # Vérification stricte de l'année active
        annee_active = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
        if not annee_active:
            st.error("⛔ Aucune année scolaire n'est définie comme active. Allez dans Administration > Paramètres de l'école pour activer une année (ex: 2026-2027).")
            return

        st.info(f"📅 Année scolaire en cours : **{annee_active.libelle}**")
        tab_liste, tab_insc = st.tabs(["📋 Élèves Inscrits", "➕ Nouvelle Inscription"])

        # --- ONGLET LISTE ---
        with tab_liste:
            inscriptions = db.query(Inscription, Eleve, Classe).join(Eleve).join(Classe).filter(
                Inscription.annee_id == annee_active.id,
                Classe.cycle == cycle_actif
            ).all()
            
            if inscriptions:
                data = []
                for insc, elv, cls in inscriptions:
                    data.append({
                        "Matricule": elv.matricule,
                        "Nom & Prénom": f"{elv.nom} {elv.prenom}",
                        "Sexe": elv.sexe,
                        "Classe": cls.libelle,
                        "Statut": insc.statut
                    })
                df = pd.DataFrame(data)
                
                recherche = st.text_input("🔍 Rechercher un élève...")
                if recherche:
                    mask = df.apply(lambda row: row.astype(str).str.contains(recherche, case=False).any(), axis=1)
                    st.dataframe(df[mask], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info(f"Aucun élève inscrit dans le cycle {cycle_actif} pour l'année {annee_active.libelle}.")

        # --- ONGLET INSCRIPTION ---
        with tab_insc:
            classes_dispo = db.query(Classe).filter(Classe.cycle == cycle_actif).all()
            if not classes_dispo:
                st.warning(f"⚠️ Aucune classe n'existe pour le cycle '{cycle_actif}'. Allez dans Paramètres de l'école > Classes pour en créer une d'abord.")
            else:
                dict_classes = {c.libelle: c.id for c in classes_dispo}
                with st.form("form_nouvel_eleve", clear_on_submit=True):
                    st.subheader("Dossier de l'élève")
                    c1, c2, c3 = st.columns(3)
                    matricule = c1.text_input("Matricule*")
                    nom = c2.text_input("Nom*")
                    prenom = c3.text_input("Prénom*")
                    
                    c4, c5, c6 = st.columns(3)
                    sexe = c4.radio("Sexe*", ["G", "F"], horizontal=True)
                    contact = c5.text_input("Contact Parent")
                    classe_sel = c6.selectbox("Classe d'affectation*", list(dict_classes.keys()))
                    
                    if st.form_submit_button("✅ Enregistrer l'inscription"):
                        if matricule and nom and prenom:
                            try:
                                # Vérifier si l'élève existe déjà physiquement
                                eleve_existant = db.query(Eleve).filter(Eleve.matricule == matricule).first()
                                
                                if not eleve_existant:
                                    eleve_existant = Eleve(matricule=matricule, nom=nom, prenom=prenom, sexe=sexe, contact_parent=contact)
                                    db.add(eleve_existant)
                                    db.flush()
                                
                                # Vérifier si l'inscription existe déjà pour cette année
                                deja_inscrit = db.query(Inscription).filter(
                                    Inscription.eleve_id == eleve_existant.id,
                                    Inscription.annee_id == annee_active.id
                                ).first()
                                
                                if deja_inscrit:
                                    st.error(f"❌ Cet élève (Matricule: {matricule}) est déjà inscrit pour l'année {annee_active.libelle}.")
                                else:
                                    nouvelle_insc = Inscription(
                                        eleve_id=eleve_existant.id,
                                        annee_id=annee_active.id,
                                        classe_id=dict_classes[classe_sel],
                                        statut="Actif"
                                    )
                                    db.add(nouvelle_insc)
                                    db.commit()
                                    st.success(f"🎉 Succès : {nom} {prenom} inscrit(e) en {classe_sel} !")
                                    st.rerun()
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Erreur technique lors de l'enregistrement : {str(e)}")
                        else:
                            st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
    finally:
        db.close()