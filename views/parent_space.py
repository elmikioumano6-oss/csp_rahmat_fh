import streamlit as st
import pandas as pd
from database.db_config import SessionLocal
from database.models import User, Eleve, Note, Matiere, Presence, EcheancePaiement, Classe

def afficher_espace_parent():
    st.subheader("👨‍👩‍👧‍👦 Espace Suivi - Espace Parent")
    
    db = SessionLocal()
    
    # Récupérer l'utilisateur connecté
    username = st.session_state.get('username')
    user_record = db.query(User).filter(User.username == username).first()
    
    if not user_record or not user_record.entity_id:
        st.warning("⚠️ Aucun élève n'est actuellement associé à ce compte parent. Veuillez contacter l'administration.")
        db.close()
        return
        
    # Récupérer l'élève lié
    eleve = db.query(Eleve).filter(Eleve.id == user_record.entity_id).first()
    if not eleve:
        st.error("❌ Fiche élève introuvable dans le système.")
        db.close()
        return
        
    classe_obj = db.query(Classe).filter(Classe.id == eleve.classe_id).first() if eleve.classe_id else None
    
    # --- EN-TÊTE PROFIL DE L'ÉLÈVE ---
    st.markdown(f"""
    ### 👤 Fiche de l'élève
    * **Nom et Prénom :** {eleve.nom} {eleve.prenom}
    * **Matricule :** `{eleve.matricule}`
    * **Classe :** {classe_obj.nom if classe_obj else 'Non assignée'}
    * **Sexe :** {getattr(eleve, 'sexe', 'N/A')}
    """)
    
    st.markdown("---")
    
    # Choix du semestre pour la consultation
    semestre_choisi = st.selectbox("Sélectionner le Semestre", ["1er Semestre", "2ème Semestre"])
    sem_num = 1 if semestre_choisi == "1er Semestre" else 2
    
    tab1, tab2, tab3 = st.tabs(["📚 Notes & Bulletins", "📋 Assiduité & Présences", "💰 Situation Financière"])
    
    # --- ONGLET 1 : NOTES ---
    with tab1:
        st.write(f"#### Notes du {semestre_choisi}")
        notes_eleve = db.query(Note).filter(Note.eleve_id == eleve.id, Note.semestre == sem_num).all()
        
        if notes_eleve:
            data_notes = []
            total_points = 0
            total_coeffs = 0
            
            for n in notes_eleve:
                mat = db.query(Matiere).filter(Matiere.id == n.matiere_id).first()
                c = getattr(mat, 'coefficient', 1) or 1
                n_cl = n.note_classe if n.note_classe is not None else 0.0
                n_co = n.note_compo if n.note_compo is not None else 0.0
                
                moy_mat = (n_cl + (n_co * 2)) / 3
                total_points += moy_mat * c
                total_coeffs += c
                
                data_notes.append({
                    "Matière": mat.nom if mat else "N/A",
                    "Interro / Classe": n_cl,
                    "Composition": n_co,
                    "Coefficient": c,
                    "Moyenne Matière": round(moy_mat, 2)
                })
                
            st.dataframe(pd.DataFrame(data_notes), use_container_width=True)
            
            moy_generale = round(total_points / total_coeffs, 2) if total_coeffs > 0 else 0.0
            st.metric(f"Moyenne Générale du {semestre_choisi}", f"{moy_generale} / 20")
        else:
            st.info("Aucune note enregistrée pour le moment sur ce semestre.")
            
    # --- ONGLET 2 : PRÉSENCES ---
    with tab2:
        st.write("#### Historique des Présences et Absences")
        presences = db.query(Presence).filter(Presence.eleve_id == eleve.id).all()
        
        if presences:
            data_pres = []
            nb_abs = 0
            nb_ret = 0
            nb_pres = 0
            
            for p in presences:
                if p.statut == "Présent": nb_pres += 1
                elif p.statut == "Absent": nb_abs += 1
                elif p.statut == "Retard": nb_ret += 1
                
                data_pres.append({
                    "Date": p.date,
                    "Statut": p.statut
                })
                
            col_p1, col_p2, col_p3 = st.columns(3)
            col_p1.metric("Jours Présent", nb_pres)
            col_p2.metric("Absences", nb_abs)
            col_p3.metric("Retards", nb_ret)
            
            st.markdown("---")
            st.dataframe(pd.DataFrame(data_pres), use_container_width=True)
        else:
            st.info("Aucun historique de présence enregistré pour le moment.")
            
    # --- ONGLET 3 : FINANCES ---
    with tab3:
        st.write("#### Suivi des Frais de Scolarité")
        echeance = db.query(EcheancePaiement).filter(EcheancePaiement.eleve_id == eleve.id).first()
        
        if echeance:
            total = echeance.montant_total
            paye = echeance.montant_paye
            reste = total - paye
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("Scolarité Totale", f"{total:,.0f} FCFA".replace(",", " "))
            col_f2.metric("Montant Payé", f"{paye:,.0f} FCFA".replace(",", " "))
            col_f3.metric("Reste à Payer", f"{reste:,.0f} FCFA".replace(",", " "), delta_color="inverse" if reste > 0 else "off")
            
            if reste <= 0:
                st.success("✅ La scolarité de l'enfant est totalement réglée.")
            else:
                st.warning(f"⚠️ Solde restant dû : **{reste:,.0f} FCFA**")
        else:
            st.info("Aucune information financière configurée pour cet élève.")

    db.close()