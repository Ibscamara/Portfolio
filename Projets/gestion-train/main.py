"""
main.py
-------
Interface en ligne de commande (CLI) de l'application de gestion des trains.

Architecture :
    - Ce fichier gère uniquement l'affichage et les interactions utilisateur.
    - La logique métier (validation, calculs, CSV) est dans fonctions.py.
    - Les modèles de données sont dans classe.py.
"""

from pathlib import Path

from classe import Gare, Train
from fonctions import (
    DELAI_SAISIE,
    _label_groupe,
    ajouter_donnee_csv,
    calculer_resume_passagers,
    date_valide,
    filtrer_par_type,
    grouper_trains,
    heure_valide,
    input_avec_timeout,
    lire_fichier_csv,
    normaliser_heure,
    normaliser_type_train,
    numero_train_valide,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
NOM_FICHIER = str(BASE_DIR / "passager-train.csv")

# La gare est initialisée une seule fois au lancement.
# rafraichir_gare() relit le CSV uniquement quand c'est nécessaire
# (retour au menu principal ou après un ajout).
GARE = Gare("Gare principale")


# ===========================================================================
# Outils d'affichage
# ===========================================================================

def afficher_titre(titre: str) -> None:
    """Affiche un titre encadré de séparateurs pour structurer la console."""
    largeur = 70
    print("\n" + "═" * largeur)
    print(titre.center(largeur))
    print("═" * largeur)


def afficher_separateur_leger() -> None:
    print("─" * 70)


def pause() -> None:
    """Attend que l'utilisateur appuie sur Entrée avant de continuer."""
    input("\n  Appuyez sur Entrée pour continuer...")


def retour_menu_principal() -> None:
    print("\n  ↩  Retour au menu principal...")


def rafraichir_gare() -> None:
    """Relit le fichier CSV et met à jour la liste des trains en mémoire."""
    GARE.charger_trains(lire_fichier_csv(NOM_FICHIER))


def afficher_resume(trains: list[Train]) -> None:
    """Affiche les statistiques de fréquentation pour un groupe de trains."""
    resume = calculer_resume_passagers(trains)
    print("\n  ┌─ Résumé " + "─" * 40)
    print(f"  │  Trains          : {resume['total_trains']}")
    print(f"  │  Total passagers : {resume['total_passagers']}")
    print(f"  │  Moyenne         : {resume['moyenne']}")
    print(f"  │  Minimum         : {resume['minimum']}")
    print(f"  │  Maximum         : {resume['maximum']}")
    print("  └" + "─" * 48)


def afficher_liste_trains(trains: list[Train]) -> None:
    """Affiche la liste numérotée des trains."""
    if not trains:
        print("\n  (Aucun train à afficher dans cette catégorie.)")
        return

    for index, train in enumerate(trains, start=1):
        print(f"  {index:>3}. {train}")


def afficher_groupes(groupes: dict[str, list[Train]], periode: str) -> None:
    """
    Affiche les trains regroupés par période avec leur résumé statistique.

    Les clés techniques (ex: '2022-S48') sont converties en libellés
    lisibles (ex: 'Semaine 48 — 2022') grâce à _label_groupe().
    """
    if not groupes:
        print("\n  Aucune donnée disponible.")
        return

    for cle, trains in groupes.items():
        label = _label_groupe(cle, periode)
        print(f"\n  ▶  {label}  ({len(trains)} train(s))")
        afficher_separateur_leger()
        afficher_liste_trains(trains)
        afficher_resume(trains)


# ===========================================================================
# Fonctions de saisie
# ===========================================================================

def saisir_choix(message: str, choix_valides: list[str]) -> str | None:
    """
    Demande un choix parmi une liste de valeurs valides.

    Boucle jusqu'à obtenir un choix valide ou un timeout.
    Retourne None si l'utilisateur demande à revenir au menu.
    """
    while True:
        valeur = input_avec_timeout(f"  {message}", DELAI_SAISIE)

        if valeur is None:
            retour_menu_principal()
            return None

        choix = valeur.strip()

        if choix in choix_valides:
            return choix

        print(f"  ✗  Choix invalide. Valeurs acceptées : {', '.join(choix_valides)}")


def saisir_date() -> str | None:
    """
    Demande une date au format JJ-MM-AAAA.

    Boucle tant que le format est incorrect.
    Retourne None si timeout + retour menu.
    """
    while True:
        valeur = input_avec_timeout(
            "  Date (JJ-MM-AAAA, ex: 15-03-2026) : ", DELAI_SAISIE
        )
        if valeur is None:
            retour_menu_principal()
            return None

        date = valeur.strip()
        if date_valide(date):
            return date

        print("  ✗  Format invalide. Exemple attendu : 15-03-2026")


def saisir_heure() -> str | None:
    """
    Demande une heure au format HHhMM.

    La saisie est normalisée (majuscules acceptées : '14H00' → '14h00').
    Boucle tant que le format est incorrect.
    """
    while True:
        valeur = input_avec_timeout(
            "  Heure (HHhMM, ex: 15h07) : ", DELAI_SAISIE
        )
        if valeur is None:
            retour_menu_principal()
            return None

        heure = normaliser_heure(valeur.strip())
        if heure_valide(heure):
            return heure

        print("  ✗  Format invalide. Exemple attendu : 15h07 ou 09h00")


def saisir_numero_train() -> str | None:
    """
    Demande le numéro du train.

    Le numéro est automatiquement converti en majuscules.
    Format : lettres + chiffres, séparateur optionnel (_ ou -).
    """
    while True:
        valeur = input_avec_timeout(
            "  Numéro du train (ex: TER245 ou TER_245) : ", DELAI_SAISIE
        )
        if valeur is None:
            retour_menu_principal()
            return None

        numero = valeur.strip().upper()
        if numero_train_valide(numero):
            return numero

        print("  ✗  Format invalide. Exemples : TER245, IC-12, TGV_001")


def saisir_nombre_passagers() -> int | None:
    """
    Demande le nombre de passagers (entier positif ou nul).

    Boucle tant que la valeur n'est pas un entier >= 0.
    """
    while True:
        valeur = input_avec_timeout(
            "  Nombre de passagers : ", DELAI_SAISIE
        )
        if valeur is None:
            retour_menu_principal()
            return None

        try:
            nombre = int(valeur.strip())
            if nombre < 0:
                print("  ✗  Le nombre de passagers ne peut pas être négatif.")
            else:
                return nombre
        except ValueError:
            print("  ✗  Veuillez entrer un nombre entier (ex: 347).")


def saisir_type_train() -> str | None:
    """
    Demande le type de train (arrivée ou départ) via un choix numéroté.

    Retourne 'Arrivée', 'Départ', ou None si retour menu.
    """
    print("\n  Type de train :")
    print("  1. Arrivée")
    print("  2. Départ")

    choix = saisir_choix("Votre choix : ", ["1", "2"])
    if choix is None:
        return None

    return "Arrivée" if choix == "1" else "Départ"


# ===========================================================================
# Sous-menu : affichage des trains
# ===========================================================================

def sous_menu_affichage(type_train: str | None = None) -> None:
    """
    Sous-menu permettant de consulter les trains par période.

    type_train : 'Arrivée', 'Départ', ou None (tous les trains).
    """
    # Libellé affiché dans le titre selon le filtre actif
    labels = {
        "Arrivée": "TRAINS EN ARRIVÉE",
        "Départ":  "TRAINS EN DÉPART",
        None:      "TOUS LES TRAINS",
    }
    label = labels.get(type_train, "TOUS LES TRAINS")

    PERIODES = {
        "1": ("semaine", "par semaine"),
        "2": ("mois",    "par mois"),
        "3": ("annee",   "par année"),
        "4": ("total",   "liste totale"),
    }

    while True:
        # On ne relit le CSV qu'au moment d'entrer dans ce menu,
        # pas à chaque tour de boucle.
        rafraichir_gare()
        trains = filtrer_par_type(GARE.tous_les_trains(), type_train)

        afficher_titre(f"AFFICHAGE — {label}")

        for code, (_, texte) in PERIODES.items():
            print(f"  {code}. Afficher {texte}")
        print("  0. Retour au menu principal")

        choix = saisir_choix("Votre choix : ", list(PERIODES.keys()) + ["0"])
        if choix is None or choix == "0":
            return

        if not trains:
            print(f"\n  (Aucun train enregistré dans la catégorie « {label} ».)")
            pause()
            continue

        periode, _ = PERIODES[choix]
        groupes = grouper_trains(trains, periode)
        afficher_groupes(groupes, periode)
        pause()


# ===========================================================================
# Ajout d'un train
# ===========================================================================

def ajouter_train_interactif(type_force: str | None = None) -> None:
    """
    Saisie interactive complète d'un nouveau train.

    Si type_force est fourni (ex: 'Arrivée'), le type n'est pas re-demandé.
    Demande une confirmation avant d'enregistrer.
    """
    afficher_titre("AJOUT D'UN TRAIN")

    # --- Type ---
    type_train = type_force if type_force else saisir_type_train()
    if type_train is None:
        return

    print(f"\n  Type sélectionné : {type_train}")
    print("  Veuillez maintenant saisir les informations du train.\n")

    # --- Champs obligatoires ---
    date = saisir_date()
    if date is None:
        return

    heure = saisir_heure()
    if heure is None:
        return

    numero = saisir_numero_train()
    if numero is None:
        return

    nb_passagers = saisir_nombre_passagers()
    if nb_passagers is None:
        return

    # --- Récapitulatif et confirmation ---
    train = Train(
        date=date,
        heure=heure,
        numero=numero,
        nb_passagers=nb_passagers,
        type_train=type_train,
    )

    print("\n  ┌─ Récapitulatif du train à ajouter " + "─" * 15)
    print(f"  │  {train}")
    print("  └" + "─" * 50)

    print("\n  Confirmez-vous l'ajout de ce train ?")
    print("  1. Oui, enregistrer")
    print("  2. Non, annuler")

    confirmation = saisir_choix("Votre choix : ", ["1", "2"])
    if confirmation != "1":
        print("\n  Ajout annulé.")
        pause()
        return

    # --- Enregistrement ---
    ajouter_donnee_csv(NOM_FICHIER, train)
    GARE.ajouter_train(train)

    print("\n  ✓  Train enregistré avec succès !")
    pause()


# ===========================================================================
# Menu principal
# ===========================================================================

def menu_principal() -> None:
    """
    Boucle principale du programme.

    Le CSV est lu une seule fois au démarrage.
    Il est relu automatiquement lorsqu'on entre dans un sous-menu d'affichage
    (pour prendre en compte les ajouts récents).
    """
    rafraichir_gare()

    CHOIX = {
        "1": ("Afficher les trains en arrivée",   lambda: sous_menu_affichage("Arrivée")),
        "2": ("Afficher les trains en départ",     lambda: sous_menu_affichage("Départ")),
        "3": ("Afficher tous les trains",          lambda: sous_menu_affichage(None)),
        "4": ("Ajouter un train en arrivée",       lambda: ajouter_train_interactif("Arrivée")),
        "5": ("Ajouter un train en départ",        lambda: ajouter_train_interactif("Départ")),
        "6": ("Ajouter un train (choisir le type)", lambda: ajouter_train_interactif()),
        "0": ("Quitter",                           None),
    }

    while True:
        afficher_titre("GESTION DES TRAINS EN GARE")
        print(f"  Gare : {GARE.nom}  |  Trains chargés : {len(GARE)}\n")

        for code, (texte, _) in CHOIX.items():
            prefixe = "  ──" if code == "0" else "  "
            print(f"{prefixe}  {code}.  {texte}")

        choix = saisir_choix("Votre choix : ", list(CHOIX.keys()))

        if choix is None:
            # L'utilisateur a laissé expirer le timeout et choisi de rester
            # → on reboucle simplement sur le menu.
            continue

        if choix == "0":
            afficher_titre("FIN DU PROGRAMME")
            print("  Merci d'avoir utilisé le gestionnaire de trains. À bientôt !")
            print()
            break

        _, action = CHOIX[choix]
        if action:
            action()


# ===========================================================================
# Point d'entrée
# ===========================================================================

def main() -> None:
    menu_principal()


if __name__ == "__main__":
    main()
