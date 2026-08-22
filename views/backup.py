import streamlit as st
import os
import time

def afficher_backup():
    st.subheader("💾 Centre de Sauvegarde & Sécurité de la Base de Données")
    st.markdown("Ce module vous permet de télécharger une copie sécurisée de toute la base de données et de restaurer une version précédente si nécessaire.")
    
    st.markdown("---")

    # Recherche automatique du fichier de base de données SQLite
    db_chemins = ["database.db", "school.db", "data.db", "csp_rahmat.db"]
    # On vérifie aussi dans le dossier 'database/' qui est utilisé dans votre projet
    db_file = next((path for path in db_chemins if os.path.exists(path)), None)
    if not db_file and os.path.exists("database/scolarite.db"):
        db_file = "database/scolarite.db"

    # Recherche dynamique si non trouvé
    if not db_file:
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".db") and "backup" not in root:
                    db_file = os.path.join(root, file)
                    break

    # --- SECTION TÉLÉCHARGEMENT ---
    if db_file and os.path.exists(db_file):
        with open(db_file, "rb") as f:
            bytes_data = f.read()

        nom_sauvegarde = f"backup_csp_rahmat_{time.strftime('%Y-%m-%d_%H-%M-%S')}.db"
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.success("✅ **Statut du système :** La base de données est active et prête.")
            st.info("💡 **Conseil :** Téléchargez régulièrement cette sauvegarde pour protéger vos données contre les réinitialisations du Cloud.")
        
        with col2:
            st.markdown("### Téléchargement")
            st.download_button(
                label="📥 Télécharger la BD (.db)",
                data=bytes_data,
                file_name=nom_sauvegarde,
                mime="application/octet-stream",
                type="primary",
                use_container_width=True
            )
    else:
        st.error("⚠️ Fichier de base de données introuvable.")

    # --- SECTION RESTAURATION ---
    st.markdown("---")
    st.markdown("### 🔄 Restauration de la Base de Données")
    st.warning("⚠️ **Attention :** L'importation d'une base écrasera les données actuelles. Assurez-vous d'avoir bien téléchargé votre travail en cours avant.")
    
    uploaded_file = st.file_uploader("Sélectionnez un fichier de sauvegarde (.db) à restaurer", type=["db"])
    
    if uploaded_file is not None:
        if st.button("🚀 Confirmer l'importation et restaurer"):
            try:
                # Utilise le chemin trouvé plus haut, ou force vers database/scolarite.db
                cible = db_file if db_file else "database/scolarite.db"
                with open(cible, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("✅ Restauration effectuée ! Rafraîchissez la page (F5) pour appliquer.")
            except Exception as e:
                st.error(f"Erreur lors de la restauration : {e}")

    # Footer Sécurité
    st.markdown("---")
    st.markdown("### 🛡️ Sécurité passive intégrée")
    st.write("L'application effectue des copies journalières automatiques dans le dossier `backups/` à chaque démarrage.")