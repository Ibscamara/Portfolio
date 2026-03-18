from pathlib import Path

from classe import Gare, Train
from fonctions import (
    DELAI_SAISIE,
    ajouter_donnee_csv,
    calculer_resume_passagers,
    date_valide,
    filtrer_par_type,
    grouper_trains,
    heure_valide,
    input_avec_timeout,
    lire_fichier_csv,
    normaliser_type_train,
    numero_train_valide,
)

BASE_DIR = Path(__file__).resolve().parent
NOM_FICHIER = str(BASE_DIR / "passager-train.csv")
GARE = Gare("Gare principale")


# =========================
# Outils affichage
# =========================

def afficher_titre(titre: str) -> None:
    print("\n" + "=" * 70)
    print(titre.center(70))
    print("=" * 70)


def pause() -> None:
    input("\nAppuyez sur Entrée pour continuer...")


def retour_menu_principal() -> None:
    print("Retour au menu principal...")


def rafraichir_gare() -> None:
    GARE.charger_trains(lire_fichier_csv(NOM_FICHIER))


def afficher_resume(trains: list[Train]) -> None:
    resume = calculer_resume_passagers(trains)
    print("\n--- Résumé ---")
    print(f"Nombre total de trains : {resume['total_trains']}")
    print(f"Nombre total de passagers : {resume['total_passagers']}")
    print(f"Moyenne des passagers : {resume['moyenne']}")
    print(f"Minimum de passagers : {resume['minimum']}")
    print(f"Maximum de passagers : {resume['maximum']}")


def afficher_liste_trains(trains: list[Train]) -> None:
    if not trains:
        print("Aucun train à afficher.")
        return

    for index, train in enumerate(trains, start=1):
        print(f"{index}. {train.afficher()}")


def afficher_groupes(groupes: dict[str, list[Train]]) -> None:
    if not groupes:
        print("Aucune donnée à afficher.")
        return

    for cle, trains in groupes.items():
        print(f"\n>>> {cle}")
        afficher_liste_trains(trains)
        afficher_resume(trains)


# =========================
# Saisies
# =========================

def saisir_choix(message: str, choix_valides: list[str]) -> str | None:
    while True:
        valeur = input_avec_timeout(message, DELAI_SAISIE)
        if valeur is None:
            retour_menu_principal()
            return None

        choix = valeur.strip()

        if choix in choix_valides:
            print(f"Vous avez saisi le choix : {choix}")
            return choix

        print("Choix invalide. Veuillez réessayer.")


def saisir_date() -> str | None:
    while True:
        valeur = input_avec_timeout("Entrez la date (jj-mm-aaaa) : ", DELAI_SAISIE)
        if valeur is None:
            retour_menu_principal()
            return None

        date = valeur.strip()
        if date_valide(date):
            return date

        print("Format invalide. Exemple attendu : 15-12-2025")


def saisir_heure() -> str | None:
    while True:
        valeur = input_avec_timeout("Entrez l'heure (hhHMM, ex: 15h07) : ", DELAI_SAISIE)
        if valeur is None:
            retour_menu_principal()
            return None

        heure = valeur.strip()
        if heure_valide(heure):
            return heure

        print("Format invalide. Exemple attendu : 15h07")


def saisir_numero_train() -> str | None:
    while True:
        valeur = input_avec_timeout("Entrez le numéro du train (ex: TER245) : ", DELAI_SAISIE)
        if valeur is None:
            retour_menu_principal()
            return None

        numero = valeur.strip().upper()
        if numero_train_valide(numero):
            return numero

        print("Numéro invalide. Exemple : TER245 ou TER_245")


def saisir_nombre_passagers() -> int | None:
    while True:
        valeur = input_avec_timeout("Entrez le nombre de passagers : ", DELAI_SAISIE)
        if valeur is None:
            retour_menu_principal()
            return None

        try:
            nombre = int(valeur.strip())
            if nombre < 0:
                print("Le nombre de passagers doit être positif.")
            else:
                return nombre
        except ValueError:
            print("Veuillez entrer un nombre entier valide.")


def saisir_type_train() -> str | None:
    print("\nType de train :")
    print("1. Arrivée")
    print("2. Départ")

    choix = saisir_choix("Votre choix : ", ["1", "2"])
    if choix is None:
        return None

    return "Arrivée" if choix == "1" else "Départ"


# =========================
# Affichage trains
# =========================

def sous_menu_affichage(type_train: str | None = None) -> None:
    while True:
        rafraichir_gare()
        trains = filtrer_par_type(GARE.tous_les_trains(), type_train)

        label = "TOUS LES TRAINS"
        if normaliser_type_train(type_train or "") == "Arrivée":
            label = "TRAINS EN ARRIVÉE"
        elif normaliser_type_train(type_train or "") == "Départ":
            label = "TRAINS EN DÉPART"

        afficher_titre(f"AFFICHAGE - {label}")
        print("1. Afficher par semaine")
        print("2. Afficher par mois")
        print("3. Afficher par année")
        print("4. Afficher la liste totale")
        print("0. Retour au menu principal")

        choix = saisir_choix("Votre choix : ", ["1", "2", "3", "4", "0"])
        if choix is None or choix == "0":
            return

        if not trains:
            print("\nAucune donnée disponible pour cette catégorie.")
            pause()
            continue

        if choix == "1":
            groupes = grouper_trains(trains, "semaine")
        elif choix == "2":
            groupes = grouper_trains(trains, "mois")
        elif choix == "3":
            groupes = grouper_trains(trains, "annee")
        else:
            groupes = grouper_trains(trains, "total")

        afficher_groupes(groupes)
        pause()


# =========================
# Ajout trains
# =========================

def ajouter_train_interactif(type_force: str | None = None) -> None:
    afficher_titre("AJOUT D'UN TRAIN")

    if type_force is None:
        type_train = saisir_type_train()
    else:
        type_train = type_force

    if type_train is None:
        return

    print("\nVeuillez saisir les informations du train.")

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

    train = Train(
        date=date,
        heure=heure,
        numero=numero,
        nb_passagers=nb_passagers,
        type_train=type_train,
    )

    ajouter_donnee_csv(NOM_FICHIER, train)
    GARE.ajouter_train(train)

    print("\nTrain ajouté avec succès.")
    print(train.afficher())
    pause()


def sous_menu_ajout() -> None:
    while True:
        afficher_titre("AJOUT INTERACTIF D'UN TRAIN")
        print("1. Ajouter un train en arrivée")
        print("2. Ajouter un train en départ")
        print("3. Choisir le type pendant la saisie")
        print("0. Retour au menu principal")

        choix = saisir_choix("Votre choix : ", ["1", "2", "3", "0"])
        if choix is None or choix == "0":
            return

        if choix == "1":
            ajouter_train_interactif("Arrivée")
        elif choix == "2":
            ajouter_train_interactif("Départ")
        else:
            ajouter_train_interactif()


# =========================
# Menu principal
# =========================

def menu_principal() -> None:
    rafraichir_gare()

    while True:
        afficher_titre("GESTION DES TRAINS EN GARE")
        print("1. Afficher la liste des trains en arrivée")
        print("2. Afficher la liste des trains en départ")
        print("3. Afficher la liste complète de tous les trains")
        print("4. Ajouter un train en arrivée")
        print("5. Ajouter un train en départ")
        print("6. Ajouter un train de façon interactive")
        print("0. Quitter")

        choix = saisir_choix("Votre choix : ", ["1", "2", "3", "4", "5", "6", "0"])
        if choix is None:
            continue

        if choix == "1":
            sous_menu_affichage("Arrivée")
        elif choix == "2":
            sous_menu_affichage("Départ")
        elif choix == "3":
            sous_menu_affichage(None)
        elif choix == "4":
            ajouter_train_interactif("Arrivée")
        elif choix == "5":
            ajouter_train_interactif("Départ")
        elif choix == "6":
            sous_menu_ajout()
        else:
            afficher_titre("FIN DU PROGRAMME")
            print("Merci d'avoir utilisé le programme de gestion des trains.")
            break


def main() -> None:
    menu_principal()


if __name__ == "__main__":
    main()
