import base64
from datetime import datetime
from io import BytesIO
import os
import urllib.parse
import zipfile
from database.db_config import SessionLocal
from database.models import AnneeScolaire, Classe, Eleve, Matiere, Note
import streamlit as st
import streamlit.components.v1 as components

@st.cache_data(ttl=60)
def charger_donnees_bulletin_cache(classe_id):
    """Charge toutes les notes, matières et élèves en une seule fois pour éviter les requêtes en boucle."""
    db = SessionLocal()
    try:
        eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
        matieres = db.query(Matiere).all()
        notes = db.query(Note).join(Eleve).filter(Eleve.classe_id == classe_id).all()
        
        # Sérialisation propre pour le cache
        eleves_data = [{"id": e.id, "nom": e.nom, "prenom": e.prenom, "matricule": e.matricule, "sexe": getattr(e, "sexe", "Garçon")} for e in eleves]
        matieres_data = [{"id": m.id, "nom": m.nom, "coefficient": m.coefficient or 1} for m in matieres]
        notes_data = [{"eleve_id": n.eleve_id, "matiere_id": n.matiere_id, "note_classe": n.note_classe, "note_compo": n.note_compo} for n in notes]
        
        return eleves_data, matieres_data, notes_data
    finally:
        db.close()

def construire_html_bulletin_optimise(
    eleve_dict, eleves_data, matieres_data, notes_data, classe_nom, annee_libelle
):
    sexe_eleve = eleve_dict["sexe"] if eleve_dict["sexe"] else "Garçon"
    total_eleves = len(eleves_data)
    nb_filles = sum(1 for e in eleves_data if e["sexe"] == "Fille")
    nb_garcons = total_eleves - nb_filles

    # Indexation des matières par ID pour un accès instantané en mémoire ($O(1)$)
    mat_dict = {m["id"]: m for m in matieres_data}

    # Indexation des notes par élève
    notes_par_eleve = {}
    for n in notes_data:
        notes_par_eleve.setdefault(n["eleve_id"], []).append(n)

    # Calcul des moyennes de tous les élèves pour le classement en mémoire
    toutes_moyennes = []
    moyennes_classe_list = []

    for e in eleves_data:
        e_notes = notes_par_eleve.get(e["id"], [])
        e_pts, e_coefs = 0, 0
        for en in e_notes:
            mat = mat_dict.get(en["matiere_id"])
            if not mat:
                continue
            c = mat["coefficient"]
            nc = en["note_classe"] if en["note_classe"] is not None else 0
            nco = en["note_compo"] if en["note_compo"] is not None else 0
            m = (nc + (nco * 2)) / 3 if (en["note_classe"] is not None and en["note_compo"] is not None) else (nc or nco)
            e_pts += m * c
            e_coefs += c
        
        moy_e = e_pts / e_coefs if e_coefs > 0 else 0.0
        toutes_moyennes.append((e["id"], moy_e))
        moyennes_classe_list.append(moy_e)

    # Classement de l'élève actuel
    toutes_moyennes.sort(key=lambda x: x[1], reverse=True)
    rang = 1
    for idx, (eid, m_val) in enumerate(toutes_moyennes):
        if eid == eleve_dict["id"]:
            rang = idx + 1
            break

    if rang == 1:
        rang_str = "1 er" if sexe_eleve == "Garçon" else "1 ère"
    else:
        rang_str = f"{rang} ème"

    # Statistiques de la classe
    if moyennes_classe_list:
        moy_classe_val = round(sum(moyennes_classe_list) / len(moyennes_classe_list), 2)
        max_moy = round(max(moyennes_classe_list), 2)
        min_moy = round(min(moyennes_classe_list), 2)
        nb_moy = sum(1 for m in moyennes_classe_list if m >= 10)
    else:
        moy_classe_val, max_moy, min_moy, nb_moy = 0.0, 0.0, 0.0, 0

    # Notes de l'élève actuel
    notes_eleve = notes_par_eleve.get(eleve_dict["id"], [])
    notes_eleve_dict = {n["matiere_id"]: n for n in notes_eleve}

    total_points = 0
    total_coeffs = 0
    lignes_tableau = ""

    for mat in matieres_data:
        n = notes_eleve_dict.get(mat["id"])
        n_cl = n["note_classe"] if n and n["note_classe"] is not None else 0.0
        n_co = n["note_compo"] if n and n["note_compo"] is not None else 0.0
        coef = mat["coefficient"]

        moy_mat = (n_cl + (n_co * 2)) / 3 if (n and n["note_classe"] is not None and n["note_compo"] is not None) else (n_cl or n_co)
        moyen_coef = moy_mat * coef

        total_points += moyen_coef
        total_coeffs += coef

        app_mat = "Bien" if moy_mat >= 12 else ("Assez Bien" if moy_mat >= 10 else "Faible")

        lignes_tableau += f"""
        <tr>
            <td style="text-align: left; padding-left: 6px; padding-top: 6px; padding-bottom: 6px; vertical-align: middle; border: 1px solid #000 !important;">{mat["nom"]}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{n_cl}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{n_co}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{coef}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{round(moyen_coef, 1)}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{rang_str}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{app_mat}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;"></td>
        </tr>
        """

    moyenne_generale = round(total_points / total_coeffs, 2) if total_coeffs > 0 else 0.0

    # Chargement sécurisé et conversion du logo en base64
    logo_filename = "Logo CSP-RAHMAT-FH.png"
    logo_src = ""
    if os.path.exists(logo_filename):
        with open(logo_filename, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            logo_src = f"data:image/png;base64,{encoded}"
    logo_html = f'<img src="{logo_src}" alt="Logo" style="width:100%; height:100%; object-fit:contain;">' if logo_src else "<b>C.S.P</b>"

    verification_payload = f"http://localhost:8501/?verifier=true&matricule={eleve_dict['matricule']}&nom={urllib.parse.quote(eleve_dict['nom'] + ' ' + eleve_dict['prenom'])}&moyenne={moyenne_generale}&classe={urllib.parse.quote(classe_nom)}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(verification_payload)}"

    return f"""
    <div style="width: 210mm; height: 297mm; max-height: 297mm; margin: 0 auto; border: 2px solid #000 !important; padding: 8px; background: #fff; box-sizing: border-box; page-break-after: always; page-break-inside: avoid; overflow: hidden;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #000 !important; padding-bottom: 3px;">
            <div style="width: 50px; height: 50px; border: 1px solid #000 !important; display: flex; align-items: center; justify-content: center; background: #fff; overflow: hidden;">{logo_html}</div>
            <div style="text-align: center; flex-grow: 1;">
                <strong>REPUBLIQUE DU NIGER</strong><br>
                MINISTERE DE L'EDUCATION NATIONALE<br>
                <span style="font-size: 11px;">COMPLEXE SCOLAIRE PRIVE RAHMAT-FH</span><br>
                <small>Excellence- Perseverance - Reussite</small>
            </div>
            <div style="width: 50px; height: 50px; border: 1px solid #000 !important; display: flex; align-items: center; justify-content: center; background: #fff; overflow: hidden;">{logo_html}</div>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 3px; font-weight: bold; font-size: 10px;">
            <div style="font-size: 10px;">CSP RAHMAT-FH</div>
            <div style="text-align: center;">BULLETIN : 1er Semestre<br>Année Scolaire : {annee_libelle}</div>
            <div style="border: 1px solid #000 !important; padding: 2px; text-align: center; width: 70px; background: #fff;">
                <img src="{qr_url}" width="65" alt="QR Code">
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-top: 3px; border: 1px solid #000 !important; padding: 5px; font-size: 10px;">
            <div style="width: 48%; line-height: 1.3;">
                Nom et Prénom : &nbsp; <b>{eleve_dict['nom']} {eleve_dict['prenom']}</b><br>
                Matricule : &nbsp; <b>{eleve_dict['matricule']}</b><br>
                Moyenne : &nbsp; <b>{moyenne_generale}</b><br>
                Rang : &nbsp; <b>{rang_str}</b>
            </div>
            <div style="width: 48%; line-height: 1.3;">
                Classe : &nbsp; <b>{classe_nom}</b><br>
                Effectif : &nbsp; <b>{total_eleves}</b><br>
                Garçons : &nbsp; <b>{nb_garcons}</b><br>
                Filles : &nbsp; <b>{nb_filles}</b>
            </div>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 3px;">
            <thead>
                <tr>
                    <th style="border: 1px solid #000 !important; padding: 4px 3px; text-align: center; font-size: 10px; background-color: #800020 !important; color: #FFFFFF !important; font-weight: bold;">Matières</th>
                    <th style="border: 1px solid #000 !important; padding: 4px 3px; text-align: center; font-size: 10px; background-color: #800020 !important; color: #FFFFFF !important; font-weight: bold;">NoteClasse/20</th>
                    <th style="border: 1px solid #000 !important; padding: 4px 3px; text-align: center; font-size: 10px; background-color: #800020 !important; color: #FFFFFF !important; font-weight: bold;">NoteCompo/20</th>
                    <th style="border: 1px solid #000 !important; padding: 4px 3px; text-align: center; font-size: 10px; background-color: #800020 !important; color: #FFFFFF !important; font-weight: bold;">Coef</th>
                    <th style="border: 1px solid #000 !important; padding: 4px 3px; text-align: center; font-size: 10px; background-color: #800020 !important; color: #FFFFFF !important; font-weight: bold;">MoyenCoef</th>
                    <th style="border: 1px solid #000 !important; padding: 4px 3px; text-align: center; font-size: 10px; background-color: #800020 !important; color: #FFFFFF !important; font-weight: bold;">Rang</th>
                    <th style="border: 1px solid #000 !important; padding: 4px 3px; text-align: center; font-size: 10px; background-color: #800020 !important; color: #FFFFFF !important; font-weight: bold;">Appréciation</th>
                    <th style="border: 1px solid #000 !important; padding: 4px 3px; text-align: center; font-size: 10px; background-color: #800020 !important; color: #FFFFFF !important; font-weight: bold;">Signature</th>
                </tr>
            </thead>
            <tbody>
                {lignes_tableau}
                <tr style="font-weight: bold; background-color: #1a365d !important; color: #fff;">
                    <td colspan="3" style="text-align: right; color: #fff; padding: 5px 8px 5px 0; border: 1px solid #000 !important; font-size: 10px;">Total du Semestre</td>
                    <td style="color: #fff; border: 1px solid #000 !important; font-size: 10px; text-align: center; padding: 5px 2px;">{total_coeffs}</td>
                    <td style="color: #fff; border: 1px solid #000 !important; font-size: 10px; text-align: center; padding: 5px 2px;">{round(total_points, 1)}</td>
                    <td colspan="3" style="text-align: left; padding: 5px 0 5px 6px; color: #fff; border: 1px solid #000 !important; font-size: 10px;">sur {total_coeffs * 20}</td>
                </tr>
                <tr style="font-weight: bold; background-color: #1a365d !important; color: #fff;">
                    <td colspan="4" style="text-align: right; color: #fff; padding: 5px 8px 5px 0; border: 1px solid #000 !important; font-size: 10px;">Moyenne Semestre Nº1</td>
                    <td colspan="4" style="text-align: left; padding: 5px 0 5px 6px; color: #fff; border: 1px solid #000 !important; font-size: 10px;">{moyenne_generale} &nbsp; sur 20</td>
                </tr>
            </tbody>
        </table>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 3px;">
            <tr>
                <td width="38%" style="border: 1px solid #000 !important; padding: 4px; vertical-align: top; font-size: 9px; text-align: left;">
                    <b>Travail de la Classe</b><br>
                    Moyenne de la classe : {moy_classe_val}<br>
                    Plus Forte Moyenne : {max_moy}<br>
                    Plus Faible Moyenne : {min_moy}<br>
                    Nombre de Moyenne : {nb_moy}
                </td>
                <td width="30%" style="border: 1px solid #000 !important; padding: 4px; vertical-align: top; font-size: 9px;"><b>Conduite</b></td>
                <td width="17%" style="border: 1px solid #000 !important; padding: 4px; vertical-align: top; font-size: 9px;"><b>Tableau d'honneur</b></td>
                <td width="15%" style="border: 1px solid #000 !important; padding: 4px; vertical-align: top; font-size: 9px;"><b>Assiduité</b><br><br><span style="color: red; font-weight: bold;">R - A - S</span></td>
            </tr>
        </table>
    </div>
    """

def afficher_bulletins(niveau_actif=None):
    st.subheader("📄 Édition des Bulletins Scolaires")

    db = SessionLocal()
    try:
        classes = db.query(Classe).all()
        if not classes:
            st.warning("⚠️ Aucune classe enregistrée.")
            return

        options_classes = {c.nom: c.id for c in classes}
        classe_nom = st.selectbox("Sélectionner la classe", list(options_classes.keys()))
        classe_id = options_classes[classe_nom]

        annee_active = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
        annee_libelle = annee_active.libelle if annee_active else "2025-2026"
    finally:
        db.close()

    # Chargement global ultra-rapide en mémoire (sans requêtes en boucle)
    eleves_data, matieres_data, notes_data = charger_donnees_bulletin_cache(classe_id)

    if not eleves_data:
        st.info("Aucun élève dans cette classe.")
        return

    options_eleves = {f"{e['nom']} {e['prenom']} (Matricule: {e['matricule']})": e for e in eleves_data}
    eleve_choisi_str = st.selectbox("Sélectionner l'élève", list(options_eleves.keys()))
    eleve_dict = options_eleves[eleve_choisi_str]

    mode_generation = st.radio("Portée :", ["Élève sélectionné uniquement", "Toute la classe entière"], horizontal=True)

    if st.button("👁️ Générer / Afficher le Bulletin", type="primary", use_container_width=True):
        if mode_generation == "Élève sélectionné uniquement":
            corps_bulletins = construire_html_bulletin_optimise(eleve_dict, eleves_data, matieres_data, notes_data, classe_nom, annee_libelle)
        else:
            corps_bulletins = "".join([construire_html_bulletin_optimise(e, eleves_data, matieres_data, notes_data, classe_nom, annee_libelle) for e in eleves_data])

        html_global = f"<html><body>{corps_bulletins}</body></html>"
        components.html(html_global, height=980, scrolling=True)

    st.markdown("---")
    if mode_generation == "Élève sélectionné uniquement":
        html_single = construire_html_bulletin_optimise(eleve_dict, eleves_data, matieres_data, notes_data, classe_nom, annee_libelle)
        st.download_button("📥 Enregistrer le bulletin (HTML)", data=html_single.encode("utf-8"), file_name=f"Bulletin_{eleve_dict['nom']}.html", mime="text/html", use_container_width=True)
    else:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as z:
            for e in eleves_data:
                html_e = construire_html_bulletin_optimise(e, eleves_data, matieres_data, notes_data, classe_nom, annee_libelle)
                z.writestr(f"Bulletin_{e['nom']}_{e['prenom']}.html", html_e.encode("utf-8"))
        st.download_button("📦 Enregistrer TOUS les bulletins (ZIP)", data=zip_buffer.getvalue(), file_name=f"Bulletins_{classe_nom}.zip", mime="application/zip", use_container_width=True)