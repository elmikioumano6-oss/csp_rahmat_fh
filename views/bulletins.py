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


def construire_html_bulletin(
    eleve, eleves, matieres, db, classe_nom, annee_libelle
):
    notes = db.query(Note).filter(Note.eleve_id == eleve.id).all()
    sexe_eleve = (
        eleve.sexe if (hasattr(eleve, "sexe") and eleve.sexe) else "Garçon"
    )

    total_eleves = len(eleves)
    nb_filles = sum(1 for e in eleves if getattr(e, "sexe", "") == "Fille")
    nb_garcons = total_eleves - nb_filles

    # Chargement sécurisé et conversion du logo en base64
    logo_filename = "Logo CSP-RAHMAT-FH.png"
    logo_src = ""
    if os.path.exists(logo_filename):
        with open(logo_filename, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            logo_src = f"data:image/png;base64,{encoded}"

    logo_html = (
        f'<img src="{logo_src}" alt="Logo" style="width:100%; height:100%; object-fit:contain;">'
        if logo_src
        else "<b>C.S.P</b>"
    )

    # Calcul des moyennes de la classe
    moyennes_classe = []
    for e in eleves:
        e_notes = db.query(Note).filter(Note.eleve_id == e.id).all()
        e_pts, e_coefs = 0, 0
        for en in e_notes:
            mat = db.query(Matiere).filter(Matiere.id == en.matiere_id).first()
            c = getattr(mat, "coefficient", 1) or 1
            nc = en.note_classe or 0
            nco = en.note_compo or 0
            m = (
                (nc + (nco * 2)) / 3
                if (en.note_classe is not None and en.note_compo is not None)
                else (nc or nco)
            )
            e_pts += m * c
            e_coefs += c
        if e_coefs > 0:
            moyennes_classe.append(e_pts / e_coefs)
        else:
            moyennes_classe.append(0.0)

    # Calcul des points de l'élève actuel
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

    moyenne_generale = (
        round(eleve_pts / eleve_coefs, 2) if eleve_coefs > 0 else 0.0
    )

    # Classement
    toutes_moyennes = []
    for e in eleves:
        e_notes = db.query(Note).filter(Note.eleve_id == e.id).all()
        ep, ec = 0, 0
        for en in e_notes:
            mat = db.query(Matiere).filter(Matiere.id == en.matiere_id).first()
            c = getattr(mat, "coefficient", 1) or 1
            nc = en.note_classe or 0
            nco = en.note_compo or 0
            m = (
                (nc + (nco * 2)) / 3
                if (en.note_classe is not None and en.note_compo is not None)
                else (nc or nco)
            )
            ep += m * c
            ec += c
        toutes_moyennes.append((e.id, ep / ec if ec > 0 else 0.0))

    toutes_moyennes.sort(key=lambda x: x[1], reverse=True)
    rang = 1
    for idx, (eid, m_val) in enumerate(toutes_moyennes):
        if eid == eleve.id:
            rang = idx + 1
            break

    if rang == 1:
        rang_str = "1 er" if sexe_eleve == "Garçon" else "1 ère"
    else:
        rang_str = f"{rang} ème"

    if moyennes_classe:
        moy_classe_val = round(sum(moyennes_classe) / len(moyennes_classe), 2)
        max_moy = round(max(moyennes_classe), 2)
        min_moy = round(min(moyennes_classe), 2)
        nb_moy = sum(1 for m in moyennes_classe if m >= 10)
    else:
        moy_classe_val, max_moy, min_moy, nb_moy = 0.0, 0.0, 0.0, 0

    total_points = 0
    total_coeffs = 0
    lignes_tableau = ""

    for m in matieres:
        n = (
            db.query(Note)
            .filter(Note.eleve_id == eleve.id, Note.matiere_id == m.id)
            .first()
        )
        n_cl = n.note_classe if n and n.note_classe is not None else 0.0
        n_co = n.note_compo if n and n.note_compo is not None else 0.0
        coef = getattr(m, "coefficient", 1) or 1

        moy_mat = (
            (n_cl + (n_co * 2)) / 3
            if (n and n.note_classe is not None and n.note_compo is not None)
            else (n_cl or n_co)
        )
        moyen_coef = moy_mat * coef

        total_points += moyen_coef
        total_coeffs += coef

        app_mat = (
            "Bien"
            if moy_mat >= 12
            else ("Assez Bien" if moy_mat >= 10 else "Faible")
        )

        lignes_tableau += f"""
        <tr>
            <td style="text-align: left; padding-left: 6px; padding-top: 6px; padding-bottom: 6px; vertical-align: middle; border: 1px solid #000 !important;">{m.nom}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{n_cl}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{n_co}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{coef}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{round(moyen_coef, 1)}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{rang_str}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;">{app_mat}</td>
            <td style="text-align: center; vertical-align: middle; border: 1px solid #000 !important; padding-top: 6px; padding-bottom: 6px;"></td>
        </tr>
        """

    app_base_url = "http://localhost:8501"
    verification_payload = (
        f"{app_base_url}/?verifier=true&matricule={eleve.matricule}"
        f"&nom={urllib.parse.quote(eleve.nom + ' ' + eleve.prenom)}"
        f"&moyenne={moyenne_generale}&classe={urllib.parse.quote(classe_nom)}"
    )
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
                Nom et Prénom : &nbsp; <b>{eleve.nom} {eleve.prenom}</b><br>
                Matricule : &nbsp; <b>{eleve.matricule}</b><br>
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
                <tr style="font-weight: bold; background-color: #1a365d !important; color: #fff;">
                    <td colspan="4" style="text-align: right; color: #fff; padding: 5px 8px 5px 0; border: 1px solid #000 !important; font-size: 10px;">Moyenne Semestre Nº2</td>
                    <td colspan="4" style="text-align: left; padding: 5px 0 5px 6px; color: #fff; border: 1px solid #000 !important; font-size: 10px;">-</td>
                </tr>
                <tr style="font-weight: bold; background-color: #1a365d !important; color: #fff;">
                    <td colspan="4" style="text-align: right; color: #fff; padding: 5px 8px 5px 0; border: 1px solid #000 !important; font-size: 10px;">Moyenne Annuelle</td>
                    <td colspan="4" style="text-align: left; padding: 5px 0 5px 6px; color: #fff; border: 1px solid #000 !important; font-size: 10px;">-</td>
                </tr>
            </tbody>
        </table>

        <table style="width: 100%; border-collapse: collapse; margin-top: 3px;">
            <tr>
                <td width="38%" style="border: 1px solid #000 !important; padding: 4px; vertical-align: top; font-size: 9px; text-align: left; line-height: 1.25;">
                    <b>Travail de la Classe</b><br>
                    Conduite de la classe : 18,00<br>
                    Moyenne de la classe : {moy_classe_val}<br>
                    Plus Forte Moyenne : {max_moy}<br>
                    Plus Faible Moyenne : {min_moy}<br>
                    Nombre de Moyenne : {nb_moy}
                </td>
                <td width="30%" style="border: 1px solid #000 !important; padding: 4px; vertical-align: top; font-size: 9px; text-align: left; line-height: 1.25;">
                    <b>Conduite</b><br>
                    <div>☐ Bien</div>
                    <div>☐ Passable</div>
                    <div>☐ Mal</div>
                    <div>☐ Avertissement</div>
                    <div>☐ Blame</div>
                </td>
                <td width="17%" style="border: 1px solid #000 !important; padding: 4px; vertical-align: top; font-size: 9px; text-align: left; line-height: 1.25;">
                    <b>Tableau d'honneur</b><br>
                    <div>☐ Inscrit(e)</div>
                    <div>☐ Félicitations</div>
                    <div>☐ Encouragement</div>
                    <div>☐ Non Inscrit(e)</div>
                </td>
                <td width="15%" style="border: 1px solid #000 !important; padding: 4px; vertical-align: top; font-size: 9px; text-align: left; line-height: 1.25;">
                    <b>Assiduité-Retard</b><br><br>
                    <span style="color: red; font-weight: bold; font-size: 11px;">R - A - S</span>
                </td>
            </tr>
        </table>

        <table style="width: 100%; border-collapse: collapse; margin-top: 5px;">
            <tr>
                <td style="width: 50%; border: 1px solid #000 !important; height: 55px; vertical-align: top; padding: 4px; text-align: left; font-size: 10px;"><b>Le Proviseur</b></td>
                <td style="width: 50%; border: 1px solid #000 !important; height: 55px; vertical-align: top; padding: 4px; text-align: left; font-size: 10px;"><b>Appréciation des Parents :</b></td>
            </tr>
        </table>
        
        <div style="text-align: center; margin-top: 5px; font-size: 8.5px; border-top: 1px solid #000 !important; padding-top: 2px; font-weight: bold;">
            QUARTIER AEROPORT NIAMEY-NIGER &nbsp;|&nbsp; TEL: 97327752 / 89522398 / 92532710
        </div>
    </div>
    """


def afficher_bulletins(niveau_actif=None):
    st.subheader("📄 Édition des Bulletins Scolaires")

    db = SessionLocal()

    classes = db.query(Classe).all()
    if not classes:
        st.warning("⚠️ Aucune classe enregistrée.")
        db.close()
        return

    options_classes = {c.nom: c.id for c in classes}
    classe_nom = st.selectbox(
        "Sélectionner la classe", list(options_classes.keys())
    )
    classe_id = options_classes[classe_nom]

    eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
    if not eleves:
        st.info("Aucun élève dans cette classe.")
        db.close()
        return

    options_eleves = {
        f"{e.nom} {e.prenom} (Matricule: {e.matricule})": e.id
        for e in eleves
    }
    eleve_choisi_str = st.selectbox(
        "Sélectionner l'élève", list(options_eleves.keys())
    )
    eleve_id = options_eleves[eleve_choisi_str]

    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()

    annee_active = (
        db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
    )
    annee_libelle = annee_active.libelle if annee_active else "2025-2026"

    mode_generation = st.radio(
        "Portée :",
        ["Élève sélectionné uniquement", "Toute la classe entière"],
        horizontal=True,
    )

    col_b1, col_b2 = st.columns(2)
    btn_generer = col_b1.button(
        "👁️ Générer / Afficher le Bulletin",
        type="primary",
        use_container_width=True,
    )

    matieres = db.query(Matiere).all()

    if btn_generer:
        corps_bulletins = ""
        if mode_generation == "Élève sélectionné uniquement":
            corps_bulletins = construire_html_bulletin(
                eleve, eleves, matieres, db, classe_nom, annee_libelle
            )
        else:
            for e in eleves:
                corps_bulletins += construire_html_bulletin(
                    e, eleves, matieres, db, classe_nom, annee_libelle
                )

        html_global = f"""
        <html>
        <head>
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 0mm;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 10px; 
                    color: #000; 
                    background: #fff; 
                    margin: 0; 
                    padding: 0; 
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                .print-bar {{ text-align: center; padding: 8px; background: #f8f9fa; border-bottom: 1px solid #ccc; margin-bottom: 10px; }}
                .print-btn {{ background-color: #800020; color: white; padding: 8px 16px; font-size: 13px; font-weight: bold; border: none; border-radius: 5px; cursor: pointer; }}
                .print-btn:hover {{ background-color: #a00028; }}

                @media print {{
                    .print-bar {{ display: none; }}
                    body {{ margin: 0; background: #fff; }}
                    table, th, td, div {{
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }}
                    th, td {{
                        border: 1px solid #000 !important;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="print-bar">
                <button class="print-btn" onclick="window.print()">🖨️ Imprimer / Enregistrer en PDF (Format A4 Exact)</button>
            </div>
            {corps_bulletins}
        </body>
        </html>
        """

        components.html(html_global, height=980, scrolling=True)

    st.markdown("---")
    if mode_generation == "Élève sélectionné uniquement":
        html_single = construire_html_bulletin(
            eleve, eleves, matieres, db, classe_nom, annee_libelle
        )
        st.download_button(
            label="📥 Enregistrer le bulletin de cet élève (HTML)",
            data=html_single.encode("utf-8"),
            file_name=f"Bulletin_{eleve.nom}_{eleve.prenom}.html",
            mime="text/html",
            use_container_width=True,
        )
    else:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as z:
            for e in eleves:
                html_e = construire_html_bulletin(
                    e, eleves, matieres, db, classe_nom, annee_libelle
                )
                z.writestr(
                    f"Bulletin_{e.nom}_{e.prenom}.html", html_e.encode("utf-8")
                )

        st.download_button(
            label="📦 Enregistrer TOUS les bulletins de la classe en ZIP",
            data=zip_buffer.getvalue(),
            file_name=f"Bulletins_{classe_nom}.zip",
            mime="application/zip",
            use_container_width=True,
        )

    db.close()