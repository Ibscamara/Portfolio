# 🪨 Analyse statistique de la production de bauxite en Guinée avec R

> Projet de data science appliqué à l'économie des ressources naturelles.  
> Auteur : **Ibrahima Sory Camara** · Langage : **R (base)** · Données : **USGS 2010–2023**

---

## 📌 Contexte

La Guinée détient les **plus grandes réserves mondiales de bauxite** (7.4 milliards de tonnes)
et est devenue le **premier exportateur mondial** depuis 2023. Ce projet analyse l'évolution
de la production entre 2010 et 2023 à travers une démarche statistique complète, et confronte
les prédictions du modèle aux valeurs réelles observées en 2024 et 2025.

---

## 🎯 Objectifs

- Explorer et visualiser l'évolution de la production de bauxite sur 14 ans
- Calculer les indicateurs statistiques descriptifs clés
- Modéliser la tendance par régression linéaire simple (OLS)
- Évaluer la précision du modèle en le confrontant aux données réelles 2024–2025

---

## 📂 Structure du projet

```
bauxite-guinee/
├── README.md              # Présentation du projet
├── analyse_bauxite.R      # Script R complet (reproductible)
├── bauxite_guinee.csv     # Données officielles USGS 2010–2023
├── resultats.html         # Page de résultats interactive
└── rapport_portfolio.pdf  # Rapport complet mis en forme
```

---

## 📊 Résultats clés

| Indicateur | Valeur |
|---|---|
| Production 2010 | 17.4 Mt |
| Production 2023 | 123.0 Mt |
| Croissance totale | **+607 %** |
| Moyenne sur la période | 50.35 Mt |
| Coefficient de variation | 71.89 % |
| R² du modèle linéaire | **0.894** |
| Pente de régression | +8.18 Mt/an |

### Comparaison prédictions vs réel

| Année | Prédit | Réel | Écart |
|---|---|---|---|
| 2024 | 111.7 Mt | **141.0 Mt** | +26 % |
| 2025 | 119.9 Mt | **182.8 Mt** | +52 % |
| 2026 | 128.1 Mt | ~199+ Mt (estimé) | ~+55 % |

> Le modèle linéaire sous-estime la réalité car la croissance post-2016 suit
> une trajectoire **exponentielle**, amplifiée par l'arrivée de nouveaux opérateurs
> et la demande chinoise record (+26 % en 2025).

---

## 🔧 Outils utilisés

- **Langage** : R 4.3 (base R uniquement, sans package externe)
- **Fonctions** : `plot()`, `hist()`, `boxplot()`, `lm()`, `predict()`, `polygon()`, `abline()`
- **Données** : USGS Minerals Yearbook, GlobalData, Ministère des Mines de Guinée

---

## 🚀 Reproduire l'analyse

```r
# 1. Cloner le repo
# 2. Ouvrir analyse_bauxite.R dans R ou RStudio
# 3. Lancer le script entier (aucun package à installer)

source("analyse_bauxite.R")
```

---

## 📈 Visualisations produites

- **Figure 1** — Courbe d'évolution temporelle (2010–2023) avec aire et point d'inflexion 2016
- **Figure 2** — Histogramme de distribution avec ligne de moyenne
- **Figure 3** — Boîte à moustaches avec annotations Q1 / Médiane / Q3
- **Figure 4** — Droite de régression avec intervalle de confiance 95 %
- **Figure 5** — Comparaison prédictions modèle vs valeurs réelles 2024–2025

---

## 📚 Sources des données

- USGS Minerals Yearbook 2010–2018 : https://pubs.usgs.gov/myb/
- GlobalData Guinea Bauxite Production 2018–2021
- Trade.gov Guinea Mining Report 2022
- African Green Minerals Observatory 2023
- Reuters / Financial Afrik — données 2024 et 2025

---

*Projet réalisé dans le cadre d'un portfolio de Data Science.*  
*Contact : github.com/lbscamara*
