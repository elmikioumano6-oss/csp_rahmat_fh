import io
import pandas as pd
import streamlit as st
from database.db_config import SessionLocal
from database.models import Classe, EcheancePaiement, Eleve
from sqlalchemy import func


@st.cache_data(ttl=300)
def charger_donnees_impayes(niveau_actif):
    db = SessionLocal()
    try:
        eleves = (
            db.query(
                Eleve.id,
                Eleve.matricule,
                Eleve.nom,
                Eleve.prenom,
                Classe.nom.label("classe_nom"),
            )
            .join(Classe)
            .filter(Classe.cycle == niveau_actif)
            .all()
        )

        if not eleves:
            return []

        eleve_ids = [e.id for e in eleves]

        echeances = (
            db.query(
                EcheancePaiement.eleve_id,
                func.sum(EcheancePaiement.montant_total).label("total_dû"),
                func.sum(EcheancePaiement.montant_paye).label("total_payé"),
            )
            .filter(EcheancePaiement.eleve_id.in_(eleve_ids))
            .group_by(EcheancePaiement.eleve_id)
            .all()
        )

        dict_paiements = {
            e.eleve_id: {"du": e.total_dû or 0, "paye": e.total_payé or 0}
            for e in echeances
        }

        data_impayes = []
        for e in eleves:
            paiements = dict_paiements.get(e.id, {"du": 0, "paye": 0})
            reste = paiements["du"] - paiements["paye"]

            if reste > 0:
                data_impayes.append(
                    {
                        "Matricule": e.matricule,
                        "Nom": e.nom,
                        "Prénom": e.prenom,
                        "Classe": e.classe_nom,
                        "Total Dû (FCFA)": paiements["du"],
                        "Déjà Payé (FCFA)": paiements["paye"],
                        "Reste à Payer (FCFA)": reste,
                    }
                )
        return data_impayes
    finally:
        db.close()


def generer_excel_impayes(df, niveau_actif):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Impayés")

        workbook = writer.book
        worksheet = writer.sheets["Impayés"]

        # Formats professionnels
        header_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#D97706",
                "font_color": "white",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        money_format = workbook.add_format(
            {"num_format": "#,##0", "border": 1, "align": "right"}
        )
        cell_format = workbook.add_format({"border": 1, "align": "left"})

        # Application des en-têtes
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Application des formats sur les cellules
        for row_num in range(len(df)):
            for col_num in range(len(df.columns)):
                val = df.iloc[row_num, col_num]
                if col_num >= 4:  # Colonnes financières
                    worksheet.write(row_num + 1, col_num, val, money_format)
                else:
                    worksheet.write(row_num + 1, col_num, val, cell_format)

        # Ajustement automatique de la largeur des colonnes
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 4
            worksheet.set_column(i, i, max_len)

    return output.getvalue()


def afficher_soldes_impayes(niveau_actif):
    st.subheader(f"⚠️ Soldes & Impayés - {niveau_actif}")
    data_impayes = charger_donnees_impayes(niveau_actif)

    if not data_impayes:
        st.success("✅ Aucun impayé détecté pour ce cycle !")
    else:
        df = pd.DataFrame(data_impayes)

        # Formatage pour l'affichage graphique sur l'interface
        df_display = df.copy()
        for col in [
            "Total Dû (FCFA)",
            "Déjà Payé (FCFA)",
            "Reste à Payer (FCFA)",
        ]:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        total_global_impaye = df["Reste à Payer (FCFA)"].sum()
        st.metric(
            "Total des Impayés du cycle", f"{total_global_impaye:,.0f} FCFA"
        )

        # Génération du fichier Excel stylisé
        excel_data = generer_excel_impayes(df, niveau_actif)

        st.download_button(
            label="📥 Télécharger le rapport Excel pro (.xlsx)",
            data=excel_data,
            file_name=f"impayes_{niveau_actif}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )