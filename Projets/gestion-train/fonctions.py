import csv
import os
import platform
import re
import signal
from collections import defaultdict
from datetime import datetime

from classe import Train

CHAMPS_CSV = ["Date", "Heure", "Num_Train", "Nb_Passager", "Type_Train"]
DELAI_SAISIE = 45


class SaisieExpiree(Exception):
    pass


# =========================
# Gestion du timeout
# =========================

def _handler_timeout(signum, frame):
    raise SaisieExpiree


def demander_action_apres_timeout() -> str:
    while True:
        print("\nLe temps est écoulé, nous n'avons pas compris votre saisie.")
        print("1. Continuer")
        print("2. Retourner au menu principal")

        choix = input(
            "Veuillez saisir 1 pour continuer ou 2 pour revenir au menu principal : "
        ).strip()

        if choix == "1":
            print("Vous avez saisi le choix : 1")
            return "continuer"

        if choix == "2":
            print("Vous avez saisi le choix : 2")
            return "menu"

        print("Choix invalide. Veuillez réessayer.")


def input_avec_timeout(message: str, timeout: int = DELAI_SAISIE) -> str | None:
    """
    Version stable pour Android / Termux.
    Pas de compteur dégressif en direct pour éviter de casser l'affichage.
    """

    systeme = platform.system().lower()

    if systeme == "windows":
        print(f"\nVous disposez de {timeout} secondes pour saisir votre réponse.")
        print("Veuillez saisir votre réponse puis appuyer sur Entrée.")
        try:
            return input(message)
        except EOFError:
            return None

    while True:
        print(f"\nVous disposez de {timeout} secondes pour saisir votre réponse.")
        print("Veuillez saisir votre réponse puis appuyer sur Entrée.")

        ancien_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handler_timeout)
        signal.alarm(timeout)

        try:
            valeur = input(message)
            signal.alarm(0)
            return valeur

        except SaisieExpiree:
            signal.alarm(0)
            action = demander_action_apres_timeout()

            if action == "continuer":
                continue
            return None

        finally:
            signal.signal(signal.SIGALRM, ancien_handler)


# =========================
# Validation et normalisation
# =========================

def normaliser_type_train(type_train: str) -> str:
    valeur = str(type_train).strip().lower()

    if valeur in ["arrivee", "arrivée", "a"]:
        return "Arrivée"

    if valeur in ["depart", "départ", "d"]:
        return "Départ"

    return "Inconnu"


def date_valide(date_texte: str) -> bool:
    try:
        datetime.strptime(date_texte.strip(), "%d-%m-%Y")
        return True
    except ValueError:
        return False


def heure_valide(heure_texte: str) -> bool:
    try:
        datetime.strptime(heure_texte.strip(), "%Hh%M")
        return True
    except ValueError:
        return False


def numero_train_valide(numero: str) -> bool:
    return bool(re.match(r"^[A-Za-z]+[_-]?[0-9]+$", numero.strip()))


def convertir_date(date_texte: str) -> datetime:
    return datetime.strptime(date_texte.strip(), "%d-%m-%Y")


# =========================
# Gestion du fichier CSV
# =========================

def creer_fichier_si_absent(nom_fichier: str) -> None:
    if not os.path.exists(nom_fichier):
        with open(nom_fichier, mode="w", encoding="utf-8", newline="") as fichier:
            ecrivain = csv.DictWriter(fichier, fieldnames=CHAMPS_CSV)
            ecrivain.writeheader()


def lire_fichier_csv(nom_fichier: str) -> list[Train]:
    creer_fichier_si_absent(nom_fichier)
    trains = []

    with open(nom_fichier, mode="r", encoding="utf-8", newline="") as fichier:
        lecteur = csv.DictReader(fichier, skipinitialspace=True)

        for ligne in lecteur:
            if not ligne:
                continue

            date = (ligne.get("Date") or "").strip().strip('"')
            heure = (ligne.get("Heure") or "").strip().strip('"')
            numero = (ligne.get("Num_Train") or "").strip().strip('"').upper()
            nb_passager = (ligne.get("Nb_Passager") or "0").strip().strip('"')
            type_train = normaliser_type_train(ligne.get("Type_Train") or "Inconnu")

            try:
                nb_passager_int = int(nb_passager)
            except ValueError:
                nb_passager_int = 0

            train = Train(
                date=date,
                heure=heure,
                numero=numero,
                nb_passagers=nb_passager_int,
                type_train=type_train,
            )
            trains.append(train)

    return trains


def ajouter_donnee_csv(nom_fichier: str, train: Train) -> None:
    creer_fichier_si_absent(nom_fichier)

    with open(nom_fichier, mode="a", encoding="utf-8", newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=CHAMPS_CSV)
        ecrivain.writerow(train.to_dict())


# =========================
# Traitements sur les trains
# =========================

def filtrer_par_type(trains: list[Train], type_train: str | None = None) -> list[Train]:
    if type_train is None or str(type_train).strip() == "":
        return trains

    type_normalise = normaliser_type_train(type_train)
    return [train for train in trains if train.type_train == type_normalise]


def grouper_trains(trains: list[Train], periode: str) -> dict[str, list[Train]]:
    groupes = defaultdict(list)

    for train in trains:
        date_obj = convertir_date(train.date)

        if periode == "semaine":
            annee, semaine, _ = date_obj.isocalendar()
            cle = f"Semaine {semaine:02d} - {annee}"
        elif periode == "mois":
            cle = date_obj.strftime("%m-%Y")
        elif periode == "annee":
            cle = date_obj.strftime("%Y")
        else:
            cle = "Liste totale"

        groupes[cle].append(train)

    return dict(groupes)


def calculer_resume_passagers(trains: list[Train]) -> dict:
    if len(trains) == 0:
        return {
            "total_trains": 0,
            "total_passagers": 0,
            "moyenne": 0,
            "minimum": 0,
            "maximum": 0,
        }

    nombres = [train.nb_passagers for train in trains]
    total_passagers = sum(nombres)

    return {
        "total_trains": len(trains),
        "total_passagers": total_passagers,
        "moyenne": round(total_passagers / len(trains), 2),
        "minimum": min(nombres),
        "maximum": max(nombres),
    }
