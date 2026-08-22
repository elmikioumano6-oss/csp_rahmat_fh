from datetime import datetime
import pandas as pd
from database.db_config import SessionLocal
from database.models import CahierTexte, Classe, Enseignant, LogActivite, Matiere
import streamlit as st


def afficher_cahier_texte(niveau_actif):
    st.subheader(
        f"📖 Cahier de Texte & Suivi du Travail Abattu - {niveau_actif}"
    )
    st.markdown(
        "Garantissez la traçabilité complète et permanente des enseignements dispensés."
    )

    db = SessionLocal()
    try:
        # --- FORMULAIRE DE SAISIE ---
        with st.form("form_cahier_texte", clear_on_submit=True):
            st.write("### ✍️ Enregistrer le travail effectué en classe")

            classes = (
                db.query(Classe).filter(Classe.cycle == niveau_actif).all()
            )
            if not classes:
                st.warning(
                    "⚠️ Aucune classe enregistrée pour ce cycle. Veuillez en créer d'abord."
                )
                return

            # Correction : Clé unique combinant le nom, le cycle et l'ID pour gérer les doublons (ex: plusieurs 3ème)
            classe_options = {f"{c.nom} ({c.cycle}) [ID:{c.id}]": c.id for c in classes}
            classe_libelle = st.selectbox("Classe", list(classe_options.keys()))
            classe_id = classe_options[classe_libelle]

            matieres = db.query(Matiere).all()
            if not matieres:
                st.warning("⚠️ Aucune matière enregistrée dans le système.")
                return
            matiere_options = {m.nom: m.id for m in matieres}
            matiere_nom = st.selectbox("Matière", list(matiere_options.keys()))
            matiere_id = matiere_options[matiere_nom]

            enseignants = db.query(Enseignant).all()
            ens_options = (
                {
                    f"{e.nom} {e.prenom}": e.id
                    for e in enseignants
                    if e.nom and e.prenom
                }
                if enseignants
                else {}
            )

            ens_id = None
            if ens_options:
                ens_nom = st.selectbox(
                    "Enseignant responsable", list(ens_options.keys())
                )
                ens_id = ens_options[ens_nom]
            else:
                st.info(
                    "ℹ️ Aucun enseignant enregistré (champ optionnel)."
                )

            col1, col2 = st.columns(2)
            with col1:
                date_cours = st.date_input(
                    "Date du cours", value=datetime.today()
                )
            with col2:
                semestre = st.selectbox("Semestre", [1, 2], index=0)

            contenu = st.text_area(
                "Description détaillée du travail abattu (Leçons, chapitres, exercices, observations...)"
            )

            submitted = st.form_submit_button(
                "💾 Enregistrer définitivement"
            )
            if submitted:
                if contenu.strip():
                    try:
                        nouveau_cours = CahierTexte(
                            classe_id=classe_id,
                            matiere_id=matiere_id,
                            enseignant_id=ens_id,
                            date=date_cours.strftime("%Y-%m-%d"),
                            contenu=contenu.strip(),
                            semestre=semestre,
                        )
                        db.add(nouveau_cours)

                        db.add(
                            LogActivite(
                                date=datetime.now().strftime(
                                    "%Y-%m-%d %H:%M"
                                ),
                                utilisateur=st.session_state.get(
                                    "username", "Admin"
                                ),
                                action="SAISIE CAHIER DE TEXTE",
                                details=f"Classe ID {classe_id}, Matière ID {matiere_id} le {date_cours}",
                            )
                        )

                        db.commit()
                        st.success(
                            "✅ Travail abattu enregistré et sauvegardé de manière permanente !"
                        )
                    except Exception as commit_err:
                        db.rollback()
                        st.error(
                            f"❌ Erreur lors de l'enregistrement en base : {commit_err}"
                        )
                else:
                    st.warning(
                        "⚠️ Le contenu du cahier de texte ne peut pas être vide."
                    )

        st.markdown("---")
        st.write("### 📋 Historique et Consultation du Travail Abattu")

        # Filtre de consultation par classe avec la même clé unique
        selected_classe_filtre = st.selectbox(
            "Sélectionner une classe pour consulter l'historique",
            list(classe_options.keys()),
            key="filtre_classe_ct",
        )
        filtre_id = classe_options[selected_classe_filtre]

        historique = (
            db.query(CahierTexte)
            .filter(CahierTexte.classe_id == filtre_id)
            .order_by(CahierTexte.date.desc())
            .all()
        )

        if historique:
            data = []
            for h in historique:
                m_nom = h.matiere.nom if h.matiere else "N/A"
                e_nom = (
                    f"{h.enseignant.nom} {h.enseignant.prenom}"
                    if h.enseignant
                    else "N/A"
                )
                data.append(
                    {
                        "Date": h.date,
                        "Matière": m_nom,
                        "Enseignant": e_nom,
                        "Semestre": f"S{h.semestre}",
                        "Travail Abattu": h.contenu,
                    }
                )
            st.dataframe(
                pd.DataFrame(data), use_container_width=True, hide_index=True
            )
        else:
            st.info(
                "📭 Aucun enregistrement de travail abattu trouvé pour cette classe."
            )

    except Exception as e:
        st.error(f"❌ Erreur critique de chargement : {e}")
    finally:
        db.close()