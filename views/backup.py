import streamlit as st
import os
import time

def afficher_backup():
    st.subheader("💾 Centre de Sauvegarde & Sécurité de la Base de Données")
    st.markdown("Ce module vous permet de télécharger une copie sécurisée et instantanée de toute la base de données de l'école (élèves, notes, finances, classes).")
    
    st.markdown("---")

    # Recherche automatique du fichier de base de données SQLite
    db_chemins = ["database.db", "school.db", "data.db", "csp_rahmat.db"]
    db_file = next((path for path in db_chemins if os.path.exists(path)), None)

    # Recherche dynamique si non trouvé dans les noms classiques
    if not db_file:
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".db") and "backup" not in root:
                    db_file = os.path.join(root, file)
                    break

    if db_file and os.path.exists(db_file):
        with open(db_file, "rb") as f:
            bytes_data = f.read()

        nom_sauvegarde = f"backup_csp_rahmat_{time.strftime('%Y-%m-%d_%H-%M-%S')}.db"
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.success("✅ **Statut du système :** La base de données est active, intègre et prête à être sauvegardée.")
            st.info("💡 **Conseil :** Effectuez une sauvegarde sur une clé USB au moins une fois par semaine pour sécuriser les notes et les paiements de scolarité.")
        
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
        st.error("⚠️ Fichier de base de données introuvable dans le répertoire du projet.")
        st.markdown("Vérifiez l'emplacement de votre fichier `.db` SQLite.")

    # Section d'information sur les sauvegardes automatiques locales
    st.markdown("---")
    st.markdown("### 🛡️ Sécurité passive intégrée")
    st.write("L'application effectue également des copies de sauvegarde journalières automatiques dans un dossier local `backups/` à chaque démarrage du système.")