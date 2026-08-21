import streamlit as st
import os
from database.db_config import SessionLocal
from database.models import Eleve, Classe, AnneeScolaire

def afficher_cartes_scolaires(niveau_actif):
    st.subheader(f"🪪 Générateur de Cartes Scolaires - {niveau_actif}")
    db = SessionLocal()

    # Récupérer l'année scolaire active
    annee_active = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
    annee_libelle = annee_active.libelle if annee_active else "2026-2027"

    # Récupérer les classes du cycle actif
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    if not classes:
        st.warning("⚠️ Aucune classe trouvée pour ce cycle.")
        db.close()
        return

    options_classes = {c.nom: c.id for c in classes}
    choix_classe_nom = st.selectbox("Sélectionner la classe pour les cartes :", list(options_classes.keys()))
    classe_id = options_classes[choix_classe_nom]

    eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
    if not eleves:
        st.warning("⚠️ Aucun élève trouvé dans cette classe.")
        db.close()
        return

    st.markdown("---")
    st.info(f"💡 Aperçu des cartes scolaires pour la classe de **{choix_classe_nom}** (Année : {annee_libelle})")

    # Affichage des cartes sous forme de grille (2 cartes par ligne)
    cols = st.columns(2)
    for index, eleve in enumerate(eleves):
        col_courante = cols[index % 2]
        
        with col_courante:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="text-align: center; background-color: #004080; color: white; padding: 5px; border-radius: 5px 5px 0 0;">
                        <b>COMPLEXE SCOLAIRE PRIVÉ RAHMAT-FH</b><br>
                        <span style="font-size: 12px;">CARTE D'IDENTITÉ SCOLAIRE ({annee_libelle})</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                c_img, c_info = st.columns([1, 2])
                
                with c_img:
                    if eleve.photo and os.path.exists(eleve.photo):
                        st.image(eleve.photo, width=90)
                    else:
                        # Remplacement hors-ligne par un bloc élégant et cohérent
                        st.markdown(
                            """
                            <div style="width: 90px; height: 110px; background-color: #2b2b2b; color: #aaa; display: flex; align-items: center; justify-content: center; font-size: 11px; text-align: center; border-radius: 4px; border: 1px dashed #555; margin-top: 5px;">
                                Pas de<br>photo
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                with c_info:
                    st.markdown(f"**Nom :** {eleve.nom}")
                    st.markdown(f"**Prénom :** {eleve.prenom}")
                    st.markdown(f"**Matricule :** `{eleve.matricule}`")
                    st.markdown(f"**Classe :** {choix_classe_nom}")
                    st.markdown(f"**Sexe :** {eleve.sexe}")
                
                st.markdown(
                    f"""
                    <div style="text-align: center; font-size: 11px; color: gray; border-top: 1px solid #ddd; padding-top: 5px;">
                        Contact Tél : {eleve.telephone if eleve.telephone else 'N/A'} | Le Directeur
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        
        if index % 2 != 0:
            st.markdown("<br>", unsafe_allow_html=True)

    db.close()