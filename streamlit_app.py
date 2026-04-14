import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Mini Data App", layout="wide")

st.title("Explorateur de données (version traditionnelle mais efficace)")

st.sidebar.header("Paramètres")

uploaded_file = st.sidebar.file_uploader("Importer un fichier CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Aperçu des données")
    st.dataframe(df.head())

    st.subheader("Résumé statistique")
    st.write(df.describe(include="all"))

    st.sidebar.subheader("Sélection des colonnes")

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    all_cols = df.columns.tolist()

    x_axis = st.sidebar.selectbox("Axe X", all_cols)
    y_axis = st.sidebar.selectbox("Axe Y (optionnel)", [None] + all_cols)

    chart_type = st.sidebar.selectbox("Type de graphique", ["Line", "Bar", "Scatter"])

    st.subheader("Visualisation")

    if y_axis and y_axis in numeric_cols:
        data = df[[x_axis, y_axis]].dropna()

        if chart_type == "Line":
            st.line_chart(data.set_index(x_axis))
        elif chart_type == "Bar":
            st.bar_chart(data.set_index(x_axis))
        elif chart_type == "Scatter":
            st.scatter_chart(data.set_index(x_axis))

    else:
        st.info("Sélectionne une colonne Y numérique pour visualiser.")

else:
    st.info("Charge un fichier CSV pour commencer. Les données ne viennent pas par magie (pas encore).")

st.markdown("---")
st.caption("App Streamlit simple — extensible vers ML, dashboards ou pipelines.")