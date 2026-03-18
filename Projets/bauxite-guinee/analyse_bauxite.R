# ==========================================================
# Projet R : Analyse de la production de bauxite en Guinée
# Auteur : Ibrahima Sory Camara
# ==========================================================

# 1. Chargement des données
bauxite <- read.csv("bauxite_guinee.csv")

cat("Aperçu des données :\n")
print(bauxite)

cat("\nStructure du tableau :\n")
str(bauxite)

cat("\nRésumé statistique :\n")
print(summary(bauxite))

# 2. Statistiques descriptives
moyenne <- mean(bauxite$Production)
variance <- var(bauxite$Production)
ecart_type <- sd(bauxite$Production)
minimum <- min(bauxite$Production)
maximum <- max(bauxite$Production)

cat("\nStatistiques descriptives :\n")
cat("Moyenne :", moyenne, "\n")
cat("Variance :", variance, "\n")
cat("Écart-type :", ecart_type, "\n")
cat("Minimum :", minimum, "\n")
cat("Maximum :", maximum, "\n")

# 3. Graphique d'évolution
plot(
  bauxite$Annee,
  bauxite$Production,
  type = "o",
  pch = 16,
  lwd = 2,
  main = "Évolution de la production de bauxite en Guinée",
  xlab = "Année",
  ylab = "Production (millions de tonnes)",
  col = "blue"
)

# 4. Histogramme
hist(
  bauxite$Production,
  main = "Distribution de la production de bauxite",
  xlab = "Production (millions de tonnes)",
  col = "lightblue",
  border = "white"
)

# 5. Boxplot
boxplot(
  bauxite$Production,
  main = "Boîte à moustaches de la production",
  ylab = "Production (millions de tonnes)",
  col = "lightgreen"
)

# 6. Modèle linéaire simple
modele <- lm(Production ~ Annee, data = bauxite)

cat("\nRésumé du modèle linéaire :\n")
print(summary(modele))

# 7. Ajout de la droite de régression
plot(
  bauxite$Annee,
  bauxite$Production,
  pch = 16,
  main = "Production et droite de régression",
  xlab = "Année",
  ylab = "Production (millions de tonnes)",
  col = "darkred"
)
abline(modele, col = "black", lwd = 2)

# 8. Prédiction simple
nouvelles_donnees <- data.frame(Annee = c(2024, 2025, 2026))
predictions <- predict(modele, newdata = nouvelles_donnees)

cat("\nPrédictions pour les années suivantes :\n")
resultats <- data.frame(Annee = nouvelles_donnees$Annee, Production_predite = predictions)
print(resultats)

# 9. Conclusion affichée
cat("\nConclusion :\n")
cat("L'analyse montre une forte augmentation de la production de bauxite en Guinée entre 2010 et 2023.\n")
cat("La tendance générale est croissante, avec une accélération notable à partir de 2016.\n")
cat("Le modèle linéaire permet de représenter cette évolution et de proposer une estimation simple pour les années suivantes.\n")
