# 📚 Tableau de bord interactif d'analyse des inégalités d'accès à l'éducation

---

## 1. 📊 Objectif du tableau de bord

Ce tableau de bord interactif permet d'analyser les inégalités d'accès à l'éducation à partir de données issues de la Banque mondiale (période 2000–2023). Il propose des visualisations dynamiques, des filtres par pays, années et indicateurs, ainsi que des mesures d'inégalités comme l'indice de Gini pour mieux comprendre la dispersion des données éducatives.

---

## 2. ⚖️ Technologies utilisées

- **Python 3.10+**
- **Streamlit** : création d’une interface web interactive et simple d’utilisation
- **Plotly** : génération de graphiques et cartes dynamiques et interactives
- **pandas, numpy** : manipulation et traitement des données
- **wbdata** : extraction d’indicateurs via l’API de la Banque mondiale
- **certifi, ssl** : gestion sécurisée des connexions API

---

## 3. ⚙️ Structure du code principal

### Configuration initiale

- Liste des pays ciblés (principalement Afrique subsaharienne et Asie du Sud)
- Plage temporelle de 2000 à 2023
- Dictionnaire des indicateurs WDI avec noms traduits et lisibles

### Chargement des données

- Tentative de récupération des données via l’API World Bank
- En cas d’échec, chargement depuis un fichier local `education_data_clean.csv`

### Calculs et métriques

- Fonction `gini_coefficient()` pour calculer l’indice de Gini (mesure de dispersion/inégalités)
- Fonction `compute_gini_by_year()` pour suivre l’évolution temporelle des inégalités

### Interface utilisateur (Streamlit)

- Filtres interactifs : choix des pays, années, indicateurs
- Carte choroplèthe statique par pays et année sélectionnés
- Carte animée avec slider temporel pour visualiser l’évolution
- Graphique de l’évolution de l’indice de Gini dans le temps
- Export des données filtrées au format CSV
- Analyse automatique des valeurs extrêmes (max/min) par indicateur

---

## 4. 🔎 Indicateurs clés analysés

| Indicateur                                   | Code WDI           |
|----------------------------------------------|--------------------|
| Taux brut de scolarisation primaire          | `SE.PRM.ENRR`      |
| Ratio filles/garçons à l'école primaire      | `SE.ENR.PRSC.FM.ZS`|
| Taux d'achèvement du primaire                 | `SE.PRM.CMPT.ZS`   |
| Dépenses publiques en éducation (% du PIB)  | `SE.XPD.TOTL.GD.ZS`|
| Durée moyenne de scolarisation                | `SE.SCH.LIFE`      |

---

## 5. 🔧 Instructions d'utilisation

1. **Lancer le tableau de bord :**

```bash
streamlit run education_dashboard_generator.py
