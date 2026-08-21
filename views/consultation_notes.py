from datetime import datetime
from database.db_config import SessionLocal
from database.models import Classe, Eleve, Matiere, Note
import pandas as pd
import streamlit as st


def afficher_consultation_notes(niveau_actif):
    st.subheader(f"📖 Consultation des Notes et Relevés - {niveau_actif}")

    db = SessionLocal()

    # 1. Sélectionner la classe du cycle actif
    classes = db.query(Classe).filter(Classe.cycle == niveau_actif).all()
    if not classes:
        st.warning(f"⚠️ Aucune classe trouvée pour le cycle {niveau_actif}.")
        db.close()
        return

    options_classes = {c.nom: c.id for c in classes}
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        classe_nom = st.selectbox(
            "Sélectionner la classe", list(options_classes.keys())
        )
        classe_id = options_classes[classe_nom]

    with col_f2:
        semestre = st.selectbox("Sélectionner le Semestre", [1, 2])

    st.markdown("---")

    # 2. Options avancées de filtrage (Élève et Matière)
    col_f3, col_f4 = st.columns(2)

    with col_f3:
        eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
        # Option pour inclure toute la classe
        options_eleves = {"👥 Tous les élèves (Classe entière)": 0}
        for e in eleves:
            options_eleves[f"{e.nom} {e.prenom} (Matricule: {e.matricule})"] = (
                e.id
            )

        eleve_label = st.selectbox(
            "Sélectionner l'élève ou la classe entière",
            list(options_eleves.keys()),
        )
        eleve_id = options_eleves[eleve_label]

    with col_f4:
        matieres = db.query(Matiere).all()
        options_matieres = {"📚 Toutes les matières": 0}
        for m in matieres:
            options_matieres[m.nom] = m.id

        matiere_label = st.selectbox(
            "Sélectionner la matière (ou toutes)",
            list(options_matieres.keys()),
        )
        matiere_id = options_matieres[matiere_label]

    st.markdown("---")

    if st.button("Afficher le Relevé", type="primary", use_container_width=True):
        # Construction de la requête selon les filtres choisis
        query = (
            db.query(Note)
            .join(Eleve)
            .filter(Eleve.classe_id == classe_id, Note.semestre == semestre)
        )

        # Si un élève spécifique est choisi
        if eleve_id != 0:
            query = query.filter(Note.eleve_id == eleve_id)

        # Si une matière spécifique est choisie
        if matiere_id != 0:
            query = query.filter(Note.matiere_id == matiere_id)

        notes_resultats = query.all()

        if notes_resultats:
            data = []
            for n in notes_resultats:
                nom_eleve = (
                    f"{n.eleve.nom} {n.eleve.prenom}"
                    if n.eleve
                    else "Inconnu"
                )
                matricule_eleve = n.eleve.matricule if n.eleve else "-"
                nom_matiere = n.matiere.nom if n.matiere else "-"

                # Calcul de la moyenne de la ligne si besoin (Classe + Compo par exemple)
                nc = float(n.note_classe or 0.0)
                nco = float(n.note_compo or 0.0)
                # Formule standard pondérée (ex: (Classe*1 + Compo*2)/3 ou moyenne simple selon votre barème)
                moyenne_matiere = round((nc + nco * 2) / 3, 2)

                data.append({
                    "Matricule": matricule_eleve,
                    "Élève": nom_eleve,
                    "Matière": nom_matiere,
                    "Note Classe": nc,
                    "Note Compo": nco,
                    "Moyenne": moyenne_matiere,
                    "Semestre": f"Semestre {n.semestre}",
                })

            df = pd.DataFrame(data)

            st.success(
                f"📊 Relevé généré avec succès ({len(df)} enregistrement(s) trouvé(s))."
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Bouton de téléchargement CSV pour impression ou sauvegarde
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger ce relevé (CSV)",
                data=csv_data,
                file_name=f"releve_classe_{classe_nom}_semestre_{semestre}.csv",
                mime="text/csv",
            )
        else:
            st.info(
                "ℹ️ Aucun résultat trouvé pour les critères sélectionnés."
            )

    db.close()