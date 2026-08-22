import streamlit as st
import os
import time
from sync import effectuer_sauvegarde_locale

def afficher_backup():
    st.subheader("💾 Centre de Sauvegarde & Sécurité")
    st.markdown("Gérez la sécurité de vos données : sauvegardes locales, téléchargements et restaurations.")
    
    st.markdown("---")

    # --- SECTION 1 : SAUVEGARDE LOCALE AUTOMATISÉE ---
    st.markdown("### 🛡️ Sauvegarde Locale (Système)")
    st.write("Cette action crée une copie horodatée dans votre dossier `sauvegardes_locales/`.")
    if st.button("🚀 Lancer la sauvegarde sécurisée locale", type="primary"):
        try:
            effectuer_sauvegarde_locale()
            st.success("✅ Sauvegarde locale effectuée avec succès !")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde locale : {e}")

    st.markdown("---")

    # --- DÉTECTION DU FICHIER BD ---
    db_chemins = ["database.db", "school.db", "data.db", "csp_rahmat.db", "database/scolarite.db"]
    db_file = next((path for path in db_chemins if os.path.exists(path)), None)

    # --- SECTION 2 : TÉLÉCHARGEMENT ---
    if db_file and os.path.exists(db_file):
        try:
            with open(db_file, "rb") as f:
                bytes_data = f.read()

            nom_sauvegarde = f"backup_csp_rahmat_{time.strftime('%Y-%m-%d_%H-%M-%S')}.db"
            
            st.markdown("### 📥 Exportation")
            st.download_button(
                label="Télécharger la BD actuelle (.db)",
                data=bytes_data,
                file_name=nom_sauvegarde,
                mime="application/octet-stream"
            )
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier de base de données : {e}")
    else:
        st.info("ℹ️ Aucun fichier de base de données SQLite local détecté (mode Cloud / Supabase actif).")

    # --- SECTION 3 : RESTAURATION ---
    st.markdown("---")
    st.markdown("### 🔄 Restauration")
    st.warning("⚠️ **Attention :** L'importation écrasera les données actuelles.")
    
    uploaded_file = st.file_uploader("Choisir un fichier de sauvegarde (.db) à restaurer", type=["db"])
    
    if uploaded_file is not None:
        if st.button("🚀 Confirmer l'importation et restaurer"):
            try:
                cible = db_file if db_file else "database/scolarite.db"
                os.makedirs(os.path.dirname(cible), exist_ok=True)
                with open(cible, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("✅ Restauration réussie ! Rafraîchissez la page (F5).")
            except Exception as e:
                st.error(f"Erreur lors de la restauration : {e}")