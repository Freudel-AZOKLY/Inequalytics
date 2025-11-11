import collections
import collections.abc
collections.Sequence = collections.abc.Sequence

import os
import pandas as pd
import wbdata
import datetime
import numpy as np
import streamlit as st
import plotly.express as px
import ssl
import certifi

# Fix SSL si nécessaire
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# ------------------------
# 📌 Configuration
# ------------------------

countries = [
    'BF', 'BJ', 'CI', 'CM', 'GN', 'ML', 'NE', 'SN', 'TG',
    'KE', 'UG', 'TZ', 'ZM', 'ET', 'NG',
    'BD', 'IN', 'PK', 'NP', 'LK'
]

data_date = (datetime.datetime(2000, 1, 1), datetime.datetime(2023, 1, 1))

# Dictionnaire code WDI -> nom court lisible
indicators = {
    'SE.PRM.ENRR': 'taux_scolarisation_primaire',
    'SE.ENR.PRSC.FM.ZS': 'ratio_filles_garcons_primaire',
    'SE.PRM.CMPT.ZS': 'taux_achevement_primaire',
    'SE.XPD.TOTL.GD.ZS': 'depenses_education_pib',
    'SE.SCH.LIFE': 'duree_scolarisation_moyenne'
}

# Inverse dict nom court -> code WDI (utile)
indicators_inverse = {v:k for k,v in indicators.items()}

# ------------------------
# 🗕 Chargement des données
# ------------------------

@st.cache_data(ttl=86400, show_spinner=False)
def load_data_from_api():
    df = wbdata.get_dataframe(indicators, countries, data_date)
    df.reset_index(inplace=True)
    df.rename(columns={'country': 'pays', 'date': 'annee'}, inplace=True)
    df['annee'] = pd.to_datetime(df['annee']).dt.year
    # Renommer colonnes code WDI en noms courts pour facilité d’accès
    df.rename(columns=indicators, inplace=True)
    df.to_csv("education_data_clean.csv", index=False)
    return df

def load_data():
    try:
        df = load_data_from_api()
        st.success("Données chargées depuis l'API.")
    except Exception as e:
        st.warning(f"Connexion à l'API échouée : {e}")
        if os.path.exists("education_data_clean.csv"):
            df = pd.read_csv("education_data_clean.csv")
            st.info("Données locales chargées.")
        else:
            st.error("Aucune donnée disponible. Connectez-vous à Internet.")
            st.stop()
    return df

# ------------------------
# 🔢 Gini
# ------------------------

def gini_coefficient(values):
    values = values.dropna().sort_values()
    n = len(values)
    if n == 0:
        return np.nan
    cumvals = np.cumsum(values) / values.sum()
    index = np.arange(1, n + 1)
    gini = 1 - 2 * np.sum((n - index + 0.5) * values.values) / (n * values.sum())
    return gini

def compute_gini_by_year(df, indicator_name):
    gini_data = []
    for year in sorted(df['annee'].dropna().unique()):
        yearly_data = df[df['annee'] == year]
        gini = gini_coefficient(yearly_data[indicator_name])
        gini_data.append({'annee': year, 'gini_education': gini})
    return pd.DataFrame(gini_data)

# ------------------------
# 🚀 Interface Streamlit
# ------------------------

st.set_page_config(page_title="Dashboard Éducation", layout="wide")

with st.spinner("Chargement des données..."):
    df = load_data()

st.title("📚 Inégalités d'accès à l'éducation")
st.markdown("**Visualisation interactive des données de la Banque mondiale (2000–2023).**")

# Filtres avancés
st.sidebar.header("Filtres avancés")

pays_disponibles = df['pays'].dropna().unique().tolist()
selected_countries = st.sidebar.multiselect(
    "Sélectionnez un ou plusieurs pays",
    options=pays_disponibles,
    default=pays_disponibles[:3]
)

selected_years = st.sidebar.slider(
    "Sélectionnez une plage d'années",
    int(df['annee'].min()),
    int(df['annee'].max()),
    value=(2010, 2023)
)

# Selectbox affiche noms courts lisibles, on récupère la sélection
indicator_names = list(indicators.values())
selected_indicator_name = st.sidebar.selectbox(
    "Choisissez un indicateur",
    options=indicator_names
)

# On peut retrouver le code WDI (utile pour autre chose si besoin)
selected_indicator_code = indicators_inverse[selected_indicator_name]

# Filtrage des données
df_filtered = df[
    (df['pays'].isin(selected_countries)) &
    (df['annee'] >= selected_years[0]) &
    (df['annee'] <= selected_years[1])
]

# Calcul dynamique du Gini sur l’indicateur sélectionné (nom court)
gini_df = compute_gini_by_year(df_filtered, selected_indicator_name)

# ------------------------
# 🗽 Carte statique
# ------------------------

st.subheader("Carte de l'indicateur choisi")

df_map = df_filtered[df_filtered['annee'] == selected_years[1]].dropna(subset=[selected_indicator_name])
fig_map = px.choropleth(
    df_map,
    locations="pays",
    locationmode="country names",
    color=selected_indicator_name,
    hover_name="pays",
    color_continuous_scale="Viridis",
    title=f"{selected_indicator_name.replace('_',' ').capitalize()} ({selected_years[1]})"
)
st.plotly_chart(fig_map, use_container_width=True)

# ------------------------
# 🗽 Carte animée
# ------------------------

with st.expander("Visualisation animée"):
    df_anim = df_filtered.dropna(subset=[selected_indicator_name])
    fig_anim = px.choropleth(
        df_anim,
        locations="pays",
        locationmode="country names",
        color=selected_indicator_name,
        animation_frame="annee",
        color_continuous_scale="Viridis",
        title=f"Évolution animée : {selected_indicator_name.replace('_',' ').capitalize()}"
    )
    st.plotly_chart(fig_anim, use_container_width=True)

# ------------------------
# 📊 Gini
# ------------------------

st.subheader("📊 Évolution de l'indice de Gini")
fig_gini = px.line(
    gini_df,
    x="annee",
    y="gini_education",
    markers=True,
    title=f"Inégalités dans {selected_indicator_name.replace('_',' ')}"
)
st.plotly_chart(fig_gini, use_container_width=True)

# ------------------------
# 📜 Données brutes
# ------------------------

with st.expander("📜 Voir les données brutes"):
    df_export = df_filtered[['pays', 'annee', selected_indicator_name]].dropna()
    st.dataframe(df_export, use_container_width=True)
    st.download_button(
        label="📥 Télécharger les données",
        data=df_export.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"{selected_indicator_name}_{selected_years[0]}_{selected_years[1]}.csv",
        mime="text/csv"
    )

# ------------------------
# 🧐 Analyse automatique
# ------------------------

with st.expander("Analyse automatique"):
    latest_year_data = df_filtered[df_filtered["annee"] == selected_years[1]]
    latest_year_data = latest_year_data.dropna(subset=[selected_indicator_name])

    if not latest_year_data.empty:
        min_row = latest_year_data.loc[latest_year_data[selected_indicator_name].idxmin()]
        max_row = latest_year_data.loc[latest_year_data[selected_indicator_name].idxmax()]
        st.markdown(
            f"En {selected_years[1]}, **{min_row['pays']}** avait la **valeur la plus basse** de l’indicateur **{selected_indicator_name.replace('_',' ')}** : {min_row[selected_indicator_name]:.2f}"
        )
        st.markdown(
            f"En {selected_years[1]}, **{max_row['pays']}** avait la **valeur la plus élevée** de l’indicateur **{selected_indicator_name.replace('_',' ')}** : {max_row[selected_indicator_name]:.2f}"
        )
    else:
        st.markdown("⚠️ Aucune donnée exploitable pour l'année sélectionnée et l'indicateur choisi.")
