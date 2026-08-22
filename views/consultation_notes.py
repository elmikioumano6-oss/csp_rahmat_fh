import streamlit as st
import streamlit_shadcn_ui as ui
import urllib.parse
from reportlab.pdfgen import canvas
import os

def generer_pdf_notes(matricule, data):
    pdf_file = f"Bulletin_{matricule}.pdf"
    c = canvas.Canvas(pdf_file)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"Bulletin de notes - Élève : {matricule}")
    c.setFont("Helvetica", 12)
    y = 750
    for n in data:
        c.drawString(100, y, f"{n['Matière']} : {n['Note']} - {n['appréciation']}")
        y -= 25
    c.save()
    return pdf_file

def afficher_consultation_notes(niveau_actif):
    st.markdown("### 🎓 Espace Consultation des Notes")
    st.markdown(f"Consultez les notes et les moyennes en temps réel pour le cycle : **{niveau_actif}**.")
    
    matricule = st.text_input("Entrez le Matricule de l'élève", placeholder="Ex: RAHMAT-2026-001")
    
    if matricule:
        st.markdown("---")
        st.markdown("#### 📄 Fiche de l'Élève")
        
        col1, col2 = st.columns(2)
        with col1:
            ui.metric_card(title="Moyenne Trimestrielle", content="14.5 / 20", description="Rang : 3ème / 45", key="eleve_moy")
        with col2:
            ui.metric_card(title="Assiduité", content="0 Absence", description="Comportement exemplaire", key="eleve_abs")
        
        st.markdown("---")
        st.markdown("#### 📊 Dernières Notes Enregistrées")
        
        notes_data = [
            {"Matière": "Mathématiques", "Note": "15/20", "appréciation": "Très bien"},
            {"Matière": "Physique-Chimie", "Note": "14/20", "appréciation": "Bien"},
            {"Matière": "Français", "Note": "13.5/20", "appréciation": "Assez bien"}
        ]
        
        for n in notes_data:
            ui.card(
                title=n["Matière"],
                content=f"Note : {n['Note']}",
                description=f"Appréciation : {n['appréciation']}",
                key=f"note_{n['Matière']}"
            )

        st.markdown("---")
        
        # Bouton d'export PDF
        if st.button("📥 Télécharger le Bulletin PDF"):
            pdf_path = generer_pdf_notes(matricule, notes_data)
            with open(pdf_path, "rb") as f:
                st.download_button("Cliquez pour valider le téléchargement", f, file_name=pdf_path)
            # Optionnel : suppression automatique après un court délai ou laisser l'utilisateur gérer
        
        # Bouton Contact Administration
        email_admin = "direction@rahmat-fh.com"
        subject = f"Question concernant l'élève {matricule}"
        body = "Bonjour, je souhaite avoir des informations concernant le suivi académique de mon enfant."
        mail_url = f"mailto:{email_admin}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        
        st.markdown(
            f'<a href="{mail_url}" style="text-decoration:none;">'
            '<div style="width:100%; padding:10px; text-align:center; background-color:#2563eb; color:white; border-radius:5px; font-weight:bold;">'
            '📧 Contacter l\'Administration</div></a>', 
            unsafe_allow_html=True
        )

    else:
        st.info("💡 Veuillez entrer un matricule valide pour afficher le bulletin de l'élève.")