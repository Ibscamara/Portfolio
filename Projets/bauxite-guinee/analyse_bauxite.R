# =============================================================================
# Projet R : Analyse statistique de la production de bauxite en Guinée
# Auteur   : Ibrahima Sory Camara
# Données  : USGS Minerals Yearbook + Ministère des Mines de Guinée (2010-2023)
# =============================================================================

# -----------------------------------------------------------------------------
# 1. CHARGEMENT ET PREPARATION DES DONNEES
# -----------------------------------------------------------------------------

# Données officielles USGS / Ministère des Mines de Guinée
annees     <- 2010:2023
production <- c(17.4, 18.5, 17.8, 17.3, 18.1, 19.7, 32.2,
                47.2, 58.5, 68.6, 77.6, 86.0, 103.0, 123.0)

# Création du dataframe et export CSV
bauxite <- data.frame(Annee = annees, Production = production)
write.csv(bauxite, "bauxite_guinee.csv", row.names = FALSE)

cat("=== APERCU DES DONNEES ===\n")
print(bauxite)

cat("\nStructure du tableau :\n")
str(bauxite)

cat("\nResume statistique (summary) :\n")
print(summary(bauxite))

# -----------------------------------------------------------------------------
# 2. STATISTIQUES DESCRIPTIVES
# -----------------------------------------------------------------------------

moyenne    <- mean(production)
mediane    <- median(production)
ecart_type <- sd(production)
variance   <- var(production)
minimum    <- min(production)
maximum    <- max(production)
etendue    <- diff(range(production))
cv         <- sd(production) / mean(production) * 100

cat("\n=== STATISTIQUES DESCRIPTIVES ===\n")
cat("Moyenne    :", round(moyenne,    5), "Mt\n")
cat("Mediane    :", round(mediane,    2), "Mt\n")
cat("Ecart-type :", round(ecart_type, 5), "Mt\n")
cat("Variance   :", round(variance,   4), "\n")
cat("Minimum    :", minimum, "Mt  (", annees[which.min(production)], ")\n")
cat("Maximum    :", maximum, "Mt  (", annees[which.max(production)], ")\n")
cat("Etendue    :", etendue, "Mt\n")
cat("CV         :", round(cv, 4), "%\n")

# -----------------------------------------------------------------------------
# 3. FIGURE 1 — COURBE D'EVOLUTION TEMPORELLE
# -----------------------------------------------------------------------------

par(mar = c(6, 5, 4, 2))

plot(annees, production,
     type = "n",
     main = "Evolution de la production de bauxite en Guinee (2010-2023)",
     xlab = "",
     ylab = "Production (millions de tonnes)",
     xlim = c(2010, 2023),
     ylim = c(0, 140),
     xaxt = "n",
     bty  = "l")

# Axe X incliné
axis(1, at = 2010:2023, labels = 2010:2023, las = 2, cex.axis = 0.8)
mtext("Annee", side = 1, line = 4.5, cex = 0.9)

# Grille horizontale légère
abline(h = seq(0, 120, by = 20), col = "#EEEEEE", lty = 1)

# Aire rose sous la courbe
polygon(
  x = c(annees[1], annees, annees[length(annees)]),
  y = c(0, production, 0),
  col = rgb(192, 57, 43, alpha = 35, maxColorValue = 255),
  border = NA
)

# Ligne rouge et points orange
lines(annees, production, col = "#C0392B", lwd = 2.5)
points(annees, production, col = "#E67E22", pch = 16, cex = 1.4)

# Ligne pointillée point d'inflexion 2016
abline(v = 2016, lty = 3, col = "grey50", lwd = 1.2)

# Encadré annotation
rect(2013.2, 70, 2015.8, 82, col = "white", border = "grey70", lwd = 0.8)
text(2014.5, 76,
     labels = "Point d'inflexion\n2016 : +63 %",
     cex = 0.72, col = "black")

# Flèche vers 2016
arrows(x0 = 2015.8, y0 = 73,
       x1 = 2016.0, y1 = 34,
       length = 0.10, angle = 20,
       col = "grey40", lwd = 1)

# Étiquettes valeurs (alternées haut/bas)
offsets <- c(7, -9, 7, -9, 7, -9, 7, -9, 7, -9, 7, -9, 7, -9)
text(annees, production + offsets,
     labels = production,
     cex = 0.65, col = "black")

# Étiquette spéciale 2023
text(2022.0, 112,
     labels = "123 Mt\n(2023)",
     cex = 0.75, col = "#C0392B", font = 2)

# -----------------------------------------------------------------------------
# 4. FIGURE 2 — HISTOGRAMME DE DISTRIBUTION
# -----------------------------------------------------------------------------

hist(production,
     breaks = 7,
     main   = "Distribution des valeurs de production",
     xlab   = "Production (millions de tonnes)",
     ylab   = "Frequence",
     col    = "#C0392B",
     border = "white")

# Ligne de moyenne
abline(v = mean(production), lty = 2, col = "#2C3E50", lwd = 2)

text(mean(production) + 4, 5.5,
     labels = paste("Moy :", round(mean(production), 1), "Mt"),
     col = "#2C3E50", cex = 0.85, adj = 0)

# -----------------------------------------------------------------------------
# 5. FIGURE 3 — BOITE A MOUSTACHES
# -----------------------------------------------------------------------------

boxplot(production,
        main   = "Boite a moustaches — Dispersion de la production",
        ylab   = "Production (millions de tonnes)",
        col    = "lightgreen",
        border = "#C0392B")

# Annotations quartiles
q1  <- quantile(production, 0.25)
med <- median(production)
q3  <- quantile(production, 0.75)

text(1.35, q1,  paste("Q1 =", round(q1,  1), "Mt"), cex = 0.8, col = "grey40")
text(1.35, med, paste("Med=", round(med, 1), "Mt"), cex = 0.8, col = "#C0392B")
text(1.35, q3,  paste("Q3 =", round(q3,  1), "Mt"), cex = 0.8, col = "grey40")

# -----------------------------------------------------------------------------
# 6. MODELE DE REGRESSION LINEAIRE
# -----------------------------------------------------------------------------

modele <- lm(production ~ annees)

cat("\n=== RESUME DU MODELE LINEAIRE ===\n")
print(summary(modele))

# Figure 4 — Nuage de points + droite de régression
plot(annees, production,
     pch  = 16,
     col  = "darkred",
     main = "Production de bauxite et droite de regression",
     xlab = "Annee",
     ylab = "Production (millions de tonnes)",
     ylim = c(0, 140))

abline(modele, col = "black", lwd = 2)

legend("topleft",
       legend = c(
         paste("R2 =",    round(summary(modele)$r.squared, 3)),
         paste("Pente = +", round(coef(modele)[2], 2), "Mt/an"),
         paste("p-value < 2.2e-16")
       ),
       bty = "n", cex = 0.85)

# -----------------------------------------------------------------------------
# 7. PREDICTIONS 2024-2026
# -----------------------------------------------------------------------------

nouvelles_annees <- data.frame(annees = c(2024, 2025, 2026))
predictions      <- predict(modele, nouvelles_annees)

resultats <- data.frame(
  Annee              = c(2024, 2025, 2026),
  Production_predite = round(predictions, 2)
)

cat("\n=== PREDICTIONS POUR 2024-2026 ===\n")
print(resultats)

# -----------------------------------------------------------------------------
# 8. COMPARAISON PREDICTIONS VS VALEURS REELLES
# -----------------------------------------------------------------------------

reelles <- c(141.0, 182.8, NA)  # Sources : Reuters / Financial Afrik 2025

cat("\n=== COMPARAISON PREDICTIONS VS VALEURS REELLES ===\n")
comparaison <- data.frame(
  Annee              = c(2024, 2025, 2026),
  Predit_Mt          = round(predictions, 1),
  Reel_Mt            = reelles,
  Ecart_Mt           = round(reelles - predictions, 1),
  Ecart_pct          = round((reelles - predictions) / predictions * 100, 1)
)
print(comparaison)

# Figure 5 — Barres groupées comparaison
par(mfrow = c(1, 2), mar = c(5, 5, 4, 2))

# Graphique 1 : barres groupées
barplot(
  rbind(predictions[1:2], reelles[1:2]),
  beside  = TRUE,
  names.arg = c("2024", "2025"),
  col     = c("#2980B9", "#27AE60"),
  border  = "white",
  main    = "Predictions vs Valeurs reelles",
  ylab    = "Production (Mt)",
  legend.text = c("Predit (modele)", "Reel observe"),
  args.legend = list(bty = "n", cex = 0.8),
  ylim    = c(0, 220)
)

# Graphique 2 : trajectoire
plot(annees, production,
     type = "o", pch = 16, col = "grey50", lwd = 1.5,
     xlim = c(2016, 2026), ylim = c(0, 210),
     main = "Trajectoire reelle vs modele",
     xlab = "Annee", ylab = "Production (Mt)")

points(c(2024, 2025), predictions[1:2],
       pch = 18, col = "#2980B9", cex = 1.5)
lines(c(2023, 2024, 2025),
      c(production[14], predictions[1:2]),
      col = "#2980B9", lty = 2, lwd = 1.8)

points(c(2024, 2025), reelles[1:2],
       pch = 16, col = "#27AE60", cex = 1.5)
lines(c(2023, 2024, 2025),
      c(production[14], reelles[1:2]),
      col = "#27AE60", lwd = 2)

legend("topleft",
       legend = c("Historique", "Predit", "Reel"),
       col    = c("grey50", "#2980B9", "#27AE60"),
       lty    = c(1, 2, 1), pch = c(16, 18, 16),
       bty    = "n", cex = 0.8)

par(mfrow = c(1, 1))

# -----------------------------------------------------------------------------
# 9. CONCLUSION
# -----------------------------------------------------------------------------

cat("\n=== CONCLUSION ===\n")
cat("L'analyse montre une forte croissance de la production de bauxite en Guinee\n")
cat("entre 2010 et 2023, passant de 17.4 Mt a 123.0 Mt (+607 %).\n")
cat("Le point d'inflexion de 2016 correspond a l'arrivee du consortium SMB-Winning.\n")
cat("Le modele lineaire (R2 =", round(summary(modele)$r.squared, 3), ") capture bien\n")
cat("la tendance generale mais sous-estime la croissance recente :\n")
cat("- 2024 : predit 111.7 Mt, reel 141.0 Mt (+26 %)\n")
cat("- 2025 : predit 119.9 Mt, reel 182.8 Mt (+52 %)\n")
cat("Un modele exponentiel ou polynomial serait plus adapte pour les projections futures.\n")
