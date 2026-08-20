import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from database.db_config import SessionLocal
from database.models import Eleve, Classe, Note, Matiere, AnneeScolaire

def afficher_bulletins(niveau_actif=None):
    st.subheader("📄 Édition des Bulletins Scolaires")
    
    db = SessionLocal()
    
    classes = db.query(Classe).all()
    if not classes:
        st.warning("⚠️ Aucune classe enregistrée.")
        db.close()
        return
        
    options_classes = {c.nom: c.id for c in classes}
    classe_nom = st.selectbox("Sélectionner la classe", list(options_classes.keys()))
    classe_id = options_classes[classe_nom]
    
    eleves = db.query(Eleve).filter(Eleve.classe_id == classe_id).all()
    if not eleves:
        st.info("Aucun élève dans cette classe.")
        db.close()
        return
        
    options_eleves = {f"{e.nom} {e.prenom} (Matricule: {e.matricule})": e.id for e in eleves}
    eleve_choisi_str = st.selectbox("Sélectionner l'élève", list(options_eleves.keys()))
    eleve_id = options_eleves[eleve_choisi_str]
    
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    
    annee_active = db.query(AnneeScolaire).filter(AnneeScolaire.active == True).first()
    annee_libelle = annee_active.libelle if annee_active else "2025-2026"
    
    if st.button("Générer le Bulletin"):
        notes = db.query(Note).filter(Note.eleve_id == eleve.id).all()
        matieres = db.query(Matiere).all()
        
        sexe_eleve = eleve.sexe if (hasattr(eleve, 'sexe') and eleve.sexe) else "Garçon"
        
        total_eleves = len(eleves)
        nb_filles = sum(1 for e in eleves if getattr(e, 'sexe', '') == 'Fille')
        nb_garcons = total_eleves - nb_filles
        
        # Chargement sécurisé et conversion du logo en base64
        logo_filename = "Logo CSP-RAHMAT-FH.png"
        logo_src = ""
        if os.path.exists(logo_filename):
            with open(logo_filename, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                logo_src = f"data:image/png;base64,{encoded}"
        
        logo_html = f'<img src="{logo_src}" alt="Logo" style="width:100%; height:100%; object-fit:contain;">' if logo_src else '<b>C.S.P</b>'

        # Calcul des moyennes de la classe
        moyennes_classe = []
        for e in eleves:
            e_notes = db.query(Note).filter(Note.eleve_id == e.id).all()
            e_pts, e_coefs = 0, 0
            for en in e_notes:
                mat = db.query(Matiere).filter(Matiere.id == en.matiere_id).first()
                c = getattr(mat, 'coefficient', 1) or 1
                nc = en.note_classe or 0
                nco = en.note_compo or 0
                m = (nc + (nco * 2)) / 3 if (en.note_classe is not None and en.note_compo is not None) else (nc or nco)
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
            c = getattr(mat, 'coefficient', 1) or 1
            nc = n.note_classe or 0
            nco = n.note_compo or 0
            m = (nc + (nco * 2)) / 3 if (n.note_classe is not None and n.note_compo is not None) else (nc or nco)
            eleve_pts += m * c
            eleve_coefs += c
        
        moyenne_generale = round(eleve_pts / eleve_coefs, 2) if eleve_coefs > 0 else 0.0
        
        # Classement
        toutes_moyennes = []
        for e in eleves:
            e_notes = db.query(Note).filter(Note.eleve_id == e.id).all()
            ep, ec = 0, 0
            for en in e_notes:
                mat = db.query(Matiere).filter(Matiere.id == en.matiere_id).first()
                c = getattr(mat, 'coefficient', 1) or 1
                nc = en.note_classe or 0
                nco = en.note_compo or 0
                m = (nc + (nco * 2)) / 3 if (en.note_classe is not None and en.note_compo is not None) else (nc or nco)
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
            n = db.query(Note).filter(Note.eleve_id == eleve.id, Note.matiere_id == m.id).first()
            n_cl = n.note_classe if n and n.note_classe is not None else 0.0
            n_co = n.note_compo if n and n.note_compo is not None else 0.0
            coef = getattr(m, 'coefficient', 1) or 1
            
            moy_mat = (n_cl + (n_co * 2)) / 3 if (n and n.note_classe is not None and n.note_compo is not None) else (n_cl or n_co)
            moyen_coef = moy_mat * coef
            
            total_points += moyen_coef
            total_coeffs += coef
            
            app_mat = "Bien" if moy_mat >= 12 else ("Assez Bien" if moy_mat >= 10 else "Faible")
            
            lignes_tableau += f"""
            <tr>
                <td style="text-align: left; padding-left: 6px;">{m.nom}</td>
                <td>{n_cl}</td>
                <td>{n_co}</td>
                <td>{coef}</td>
                <td>{round(moyen_coef, 1)}</td>
                <td>{rang_str}</td>
                <td>{app_mat}</td>
                <td></td>
            </tr>
            """
            
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=http://localhost:8501"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11px; color: #000; background: #fff; margin: 0; padding: 0; }}
                .bulletin-container {{ width: 100%; max-width: 800px; margin: auto; border: 2px solid #000; padding: 10px; background: #fff; box-sizing: border-box; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #000; padding-bottom: 4px; }}
                .logo-box {{ width: 55px; height: 55px; border: 1px solid #000; display: flex; align-items: center; justify-content: center; background: #fff; overflow: hidden; }}
                .header-text {{ text-align: center; flex-grow: 1; }}
                .qr-box {{ border: 1px solid #000; padding: 2px; text-align: center; width: 75px; background: #fff; }}
                
                .sub-header {{ display: flex; justify-content: space-between; align-items: center; margin-top: 4px; font-weight: bold; font-size: 11px; }}
                
                .info-grid {{ display: flex; justify-content: space-between; margin-top: 4px; border: 1px solid #000; padding: 6px; font-size: 11px; }}
                .info-col {{ width: 48%; line-height: 1.4; }}
                
                table {{ width: 100%; border-collapse: collapse; margin-top: 4px; }}
                th, td {{ border: 1px solid #000; padding: 3px; text-align: center; font-size: 11px; }}
                th {{ background-color: #f2f2f2; }}
                
                .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 4px; }}
                .summary-table td {{ border: 1px solid #000; padding: 4px; vertical-align: top; font-size: 10px; text-align: left; line-height: 1.3; }}
                
                .footer-section {{ margin-top: 8px; display: flex; justify-content: space-between; }}
                .footer-box-left {{ border: 1px solid #000; width: 45%; padding: 4px; min-height: 75px; font-size: 10px; }}
                .footer-box-right {{ border: 1px solid #000; width: 45%; padding: 4px; min-height: 75px; font-size: 10px; }}
                
                .bottom-address {{ text-align: center; margin-top: 8px; font-size: 9px; border-top: 1px solid #000; padding-top: 3px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="bulletin-container">
                <div class="header">
                    <div class="logo-box">{logo_html}</div>
                    <div class="header-text">
                        <strong>REPUBLIQUE DU NIGER</strong><br>
                        MINISTERE DE L'EDUCATION NATIONALE<br>
                        <span style="font-size: 12px;">COMPLEXE SCOLAIRE PRIVE RAHMAT-FH</span><br>
                        <small>Excellence- Perseverance - Reussite</small>
                    </div>
                    <div class="logo-box">{logo_html}</div>
                </div>
                
                <div class="sub-header">
                    <div style="font-size: 11px;">CSP RAHMAT-FH</div>
                    <div style="text-align: center;">BULLETIN : 1er Semestre<br>Année Scolaire : {annee_libelle}</div>
                    <div class="qr-box">
                        <img src="{qr_url}" width="70" alt="QR Code">
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-col">
                        Nom et Prénom : &nbsp; <b>{eleve.nom} {eleve.prenom}</b><br>
                        Matricule : &nbsp; <b>{eleve.matricule}</b><br>
                        Moyenne : &nbsp; <b>{moyenne_generale}</b><br>
                        Rang : &nbsp; <b>{rang_str}</b>
                    </div>
                    <div class="info-col">
                        Classe : &nbsp; <b>{classe_nom}</b><br>
                        Effectif : &nbsp; <b>{total_eleves}</b><br>
                        Garçons : &nbsp; <b>{nb_garcons}</b><br>
                        Filles : &nbsp; <b>{nb_filles}</b>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Matières</th>
                            <th>NoteClasse/20</th>
                            <th>NoteCompo/20</th>
                            <th>Coef</th>
                            <th>MoyenCoef</th>
                            <th>Rang</th>
                            <th>Appréciation</th>
                            <th>Signature</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lignes_tableau}
                        <tr style="font-weight: bold; background-color: #1a365d; color: #fff;">
                            <td colspan="3" style="text-align: right; color: #fff; padding-right: 8px;">Total du Semestre</td>
                            <td style="color: #fff;">{total_coeffs}</td>
                            <td style="color: #fff;">{round(total_points, 1)}</td>
                            <td colspan="3" style="text-align: left; padding-left: 6px; color: #fff;">sur {total_coeffs * 20}</td>
                        </tr>
                        <tr style="font-weight: bold; background-color: #1a365d; color: #fff;">
                            <td colspan="4" style="text-align: right; color: #fff; padding-right: 8px;">Moyenne Semestre Nº2</td>
                            <td colspan="4" style="text-align: left; padding-left: 6px; color: #fff;">-</td>
                        </tr>
                        <tr style="font-weight: bold; background-color: #1a365d; color: #fff;">
                            <td colspan="4" style="text-align: right; color: #fff; padding-right: 8px;">Moyenne Semestre Nº1</td>
                            <td colspan="4" style="text-align: left; padding-left: 6px; color: #fff;">{moyenne_generale} &nbsp; sur 20</td>
                        </tr>
                    </tbody>
                </table>

                <table class="summary-table">
                    <tr>
                        <td width="38%">
                            <b>Travail de la Classe</b><br>
                            Conduite de la classe : 18,00<br>
                            Moyenne de la classe : {moy_classe_val}<br>
                            Plus Forte Moyenne : {max_moy}<br>
                            Plus Faible Moyenne : {min_moy}<br>
                            Nombre de Moyenne : {nb_moy}
                        </td>
                        <td width="30%">
                            <b>Conduite</b><br>
                            <div>☐ Bien</div>
                            <div>☐ Passable</div>
                            <div>☐ Mal</div>
                            <div>☐ Avertissement</div>
                            <div>☐ Blame</div>
                        </td>
                        <td width="17%">
                            <b>Tableau d'honneur</b><br>
                            <div>☐ Inscrit(e)</div>
                            <div>☐ Félicitations</div>
                            <div>☐ Encouragement</div>
                            <div>☐ Non Inscrit(e)</div>
                        </td>
                        <td width="15%">
                            <b>Assiduité-Rétard</b><br><br>
                            <span style="color: red; font-weight: bold; font-size: 12px;">R - A - S</span>
                        </td>
                    </tr>
                </table>

                <div class="footer-section">
                    <div class="footer-box-left">
                        <b>Le Proviseur</b>
                    </div>
                    <div class="footer-box-right">
                        <b>Appréciation des Parents :</b><br><br>
                        ________________________________________________
                    </div>
                </div>
                
                <div class="bottom-address">
                    QUARTIER AEROPORT NIAMEY-NIGER &nbsp;|&nbsp; TEL: 97327752 / 89522398 / 92532710
                </div>
            </div>
        </body>
        </html>
        """
        
        components.html(html_content, height=800, scrolling=True)

    db.close()