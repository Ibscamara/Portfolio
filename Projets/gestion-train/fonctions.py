"""
fonctions.py
------------
Fonctions utilitaires : timeout de saisie, validation, lecture/écriture CSV,
filtrage et calculs statistiques sur les trains.
"""

import csv
import logging
import os
import platform
import re
import signal
from collections import defaultdict
from datetime import datetime

from classe import Train

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHAMPS_CSV = ["Date", "Heure", "Num_Train", "Nb_Passager", "Type_Train"]
DELAI_SAISIE = 45

# Logger dédié : les erreurs de données corrompues sont tracées sans
# interrompre le programme.
logging.basicConfig(
    format="%(levelname)s | %(message)s",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)


# ===========================================================================
# Gestion du timeout de saisie
# ===========================================================================

class SaisieExpiree(Exception):
    """Levée par le handler SIGALRM quand le délai de saisie est écoulé."""


def _handler_timeout(signum, frame) -> None:  # noqa: ANN001
    raise SaisieExpiree


def demander_action_apres_timeout() -> str:
    """
    Propose à l'utilisateur de continuer ou de revenir au menu.

    Cette fonction n'a intentionnellement PAS de timeout :
    l'utilisateur vient de manquer sa saisie, lui imposer un second délai
    serait frustrant. On boucle jusqu'à obtenir un choix valide.

    Retourne :
        "continuer" ou "menu"
    """
    while True:
        print("\n  Le temps est écoulé — votre saisie n'a pas été prise en compte.")
        print("  Que souhaitez-vous faire ?")
        print("  1. Réessayer")
        print("  2. Retourner au menu principal")

        choix = input("\n  Votre choix : ").strip()

        if choix == "1":
            return "continuer"
        if choix == "2":
            return "menu"

        print("  Choix invalide, veuillez saisir 1 ou 2.")


def input_avec_timeout(message: str, timeout: int = DELAI_SAISIE) -> str | None:
    """
    Demande une saisie utilisateur avec un délai maximum.

    Comportement selon la plateforme :
    - Linux / macOS : utilise SIGALRM (timeout réel).
    - Windows / Termux : pas de signal, saisie sans limite de temps
      (mode dégradé transparent pour l'utilisateur).

    Retourne :
        La saisie de l'utilisateur, ou None si l'utilisateur demande
        à revenir au menu principal après expiration.
    """
    systeme = platform.system().lower()

    if systeme == "windows":
        # SIGALRM n'existe pas sous Windows — on désactive silencieusement
        # le timeout plutôt que de planter.
        print(f"\n  Veuillez saisir votre réponse puis appuyer sur Entrée.")
        try:
            return input(message)
        except EOFError:
            return None

    # --- Plateforme POSIX (Linux, macOS, Termux) ---
    while True:
        print(f"\n  Vous disposez de {timeout} secondes pour répondre.")

        ancien_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handler_timeout)
        signal.alarm(timeout)

        try:
            valeur = input(message)
            signal.alarm(0)                          # Annule l'alarme dès que c'est saisi
            return valeur

        except SaisieExpiree:
            # L'alarme a déjà expiré — on la remet à 0 par sécurité
            signal.alarm(0)
            action = demander_action_apres_timeout()
            if action == "continuer":
                continue                             # Relance la boucle ENTIÈRE (nouveau timeout)
            return None

        finally:
            # Toujours restaurer le handler d'origine, même en cas d'exception
            # imprévue, pour ne pas laisser le signal corrompu.
            signal.signal(signal.SIGALRM, ancien_handler)


# ===========================================================================
# Validation et normalisation des données
# ===========================================================================

def normaliser_heure(heure_texte: str) -> str:
    """
    Normalise l'heure en minuscules pour accepter '14H00' et '14h00'.

    Le CSV peut contenir des majuscules ('14H00') saisies manuellement —
    cette normalisation évite de silencieusement ignorer ces entrées.
    """
    return heure_texte.strip().lower()


def normaliser_type_train(type_train: str) -> str:
    """
    Normalise le type de train quelle que soit la casse ou l'orthographe.

    Accepte : 'a', 'arrivee', 'arrivée', 'Arrivée', 'd', 'depart', 'départ'…
    Retourne : 'Arrivée', 'Départ', ou 'Inconnu'.
    """
    valeur = str(type_train).strip().lower()

    if valeur in {"arrivee", "arrivée", "a"}:
        return "Arrivée"
    if valeur in {"depart", "départ", "d"}:
        return "Départ"

    return "Inconnu"


def date_valide(date_texte: str) -> bool:
    """Vérifie que la date respecte le format JJ-MM-AAAA."""
    try:
        datetime.strptime(date_texte.strip(), "%d-%m-%Y")
        return True
    except ValueError:
        return False


def heure_valide(heure_texte: str) -> bool:
    """
    Vérifie que l'heure respecte le format HHhMM (ex: 15h07).

    La normalisation en minuscules est appliquée avant le test,
    ce qui rend '14H00' valide.
    """
    try:
        datetime.strptime(normaliser_heure(heure_texte), "%Hh%M")
        return True
    except ValueError:
        return False


def numero_train_valide(numero: str) -> bool:
    """
    Vérifie que le numéro de train respecte le format attendu.

    Format : lettres (obligatoires) + séparateur optionnel (_ ou -) + chiffres.
    Exemples valides : TER245, TER_245, IC-12
    """
    return bool(re.match(r"^[A-Za-z]+[_-]?[0-9]+$", numero.strip()))


def convertir_date(date_texte: str) -> datetime:
    """
    Convertit une chaîne JJ-MM-AAAA en objet datetime.

    Lève ValueError si le format est incorrect — l'appelant doit gérer
    cette exception (les données CSV peuvent être corrompues).
    """
    return datetime.strptime(date_texte.strip(), "%d-%m-%Y")


# ===========================================================================
# Gestion du fichier CSV
# ===========================================================================

def creer_fichier_si_absent(nom_fichier: str) -> None:
    """Crée le fichier CSV avec son en-tête s'il n'existe pas encore."""
    if not os.path.exists(nom_fichier):
        with open(nom_fichier, mode="w", encoding="utf-8", newline="") as fichier:
            ecrivain = csv.DictWriter(fichier, fieldnames=CHAMPS_CSV)
            ecrivain.writeheader()


def lire_fichier_csv(nom_fichier: str) -> list[Train]:
    """
    Lit le fichier CSV et retourne la liste des trains valides.

    Gestion des données corrompues :
    - Les lignes avec une date invalide sont ignorées (et tracées en warning).
    - Les nombres de passagers non convertibles sont remplacés par 0.
    - Les heures en majuscules ('14H00') sont normalisées.
    - Les types inconnus sont normalisés en 'Inconnu'.

    Cela permet au programme de continuer même si le CSV contient des
    entrées partiellement corrompues.
    """
    creer_fichier_si_absent(nom_fichier)
    trains = []
    lignes_ignorees = 0

    with open(nom_fichier, mode="r", encoding="utf-8", newline="") as fichier:
        lecteur = csv.DictReader(fichier, skipinitialspace=True)

        for numero_ligne, ligne in enumerate(lecteur, start=2):
            if not ligne:
                continue

            # --- Extraction et nettoyage de chaque champ ---
            date      = (ligne.get("Date")       or "").strip().strip('"')
            heure     = (ligne.get("Heure")      or "").strip().strip('"')
            numero    = (ligne.get("Num_Train")   or "").strip().strip('"').upper()
            nb_str    = (ligne.get("Nb_Passager") or "0").strip().strip('"')
            type_brut = (ligne.get("Type_Train")  or "Inconnu")

            # --- Validation de la date (champ critique) ---
            if not date_valide(date):
                logger.warning(
                    "Ligne %d ignorée : date invalide ou absente (%r).",
                    numero_ligne, date,
                )
                lignes_ignorees += 1
                continue

            # --- Normalisation de l'heure (accepte majuscules) ---
            heure = normaliser_heure(heure)

            # --- Conversion du nombre de passagers ---
            try:
                nb_passagers = int(nb_str)
                if nb_passagers < 0:
                    logger.warning(
                        "Ligne %d : nombre de passagers négatif (%d), corrigé à 0.",
                        numero_ligne, nb_passagers,
                    )
                    nb_passagers = 0
            except ValueError:
                logger.warning(
                    "Ligne %d : nombre de passagers non convertible (%r), remplacé par 0.",
                    numero_ligne, nb_str,
                )
                nb_passagers = 0

            # --- Normalisation du type ---
            type_train = normaliser_type_train(type_brut)

            trains.append(Train(
                date=date,
                heure=heure,
                numero=numero,
                nb_passagers=nb_passagers,
                type_train=type_train,
            ))

    if lignes_ignorees:
        logger.warning(
            "%d ligne(s) du fichier CSV ont été ignorées (données invalides).",
            lignes_ignorees,
        )

    return trains


def ajouter_donnee_csv(nom_fichier: str, train: Train) -> None:
    """Ajoute un train à la fin du fichier CSV (mode append)."""
    creer_fichier_si_absent(nom_fichier)

    with open(nom_fichier, mode="a", encoding="utf-8", newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=CHAMPS_CSV)
        ecrivain.writerow(train.to_dict())


# ===========================================================================
# Traitements statistiques sur les trains
# ===========================================================================

def filtrer_par_type(trains: list[Train], type_train: str | None = None) -> list[Train]:
    """
    Filtre la liste par type de train.

    Si type_train est None ou vide, retourne tous les trains sans modification.
    """
    if not type_train:
        return trains

    type_normalise = normaliser_type_train(type_train)
    return [t for t in trains if t.type_train == type_normalise]


def grouper_trains(trains: list[Train], periode: str) -> dict[str, list[Train]]:
    """
    Groupe les trains par période (semaine, mois, annee, ou total).

    Les groupes sont triés chronologiquement pour un affichage cohérent.
    Les trains avec une date invalide sont ignorés avec un avertissement
    (données corrompues dans le CSV).

    Retourne un dict ordonné chronologiquement.
    """
    groupes: dict[str, list[Train]] = defaultdict(list)

    for train in trains:
        try:
            date_obj = convertir_date(train.date)
        except ValueError:
            logger.warning(
                "Train %r ignoré lors du groupement : date invalide (%r).",
                train.numero, train.date,
            )
            continue

        if periode == "semaine":
            annee, semaine, _ = date_obj.isocalendar()
            cle = f"{annee}-S{semaine:02d}"          # Format triable : "2022-S48"
        elif periode == "mois":
            cle = date_obj.strftime("%Y-%m")         # Format triable : "2022-11"
        elif periode == "annee":
            cle = date_obj.strftime("%Y")
        else:
            cle = "Liste totale"

    # Tri chronologique des clés (fonctionne naturellement avec les formats
    # YYYY-Sxx et YYYY-MM car ils sont lexicographiquement ordonnés).
        groupes[cle].append(train)

    return dict(sorted(groupes.items()))


def _label_groupe(cle: str, periode: str) -> str:
    """
    Convertit une clé technique (ex: '2022-S48') en libellé lisible
    (ex: 'Semaine 48 — 2022').

    Séparé de grouper_trains pour que l'affichage reste dans main.py.
    """
    if periode == "semaine" and "-S" in cle:
        annee, sem = cle.split("-S")
        return f"Semaine {sem} — {annee}"
    if periode == "mois" and len(cle) == 7:
        MOIS_FR = {
            1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
            5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
            9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
        }
        try:
            dt = datetime.strptime(cle, "%Y-%m")
            return f"{MOIS_FR[dt.month]} {dt.year}"
        except ValueError:
            return cle
    return cle


def calculer_resume_passagers(trains: list[Train]) -> dict:
    """
    Calcule les statistiques de fréquentation pour une liste de trains.

    Retourne un dictionnaire avec :
        total_trains, total_passagers, moyenne, minimum, maximum.

    Si la liste est vide, toutes les valeurs numériques sont à 0.
    """
    if not trains:
        return {
            "total_trains": 0,
            "total_passagers": 0,
            "moyenne": 0.0,
            "minimum": 0,
            "maximum": 0,
        }

    nombres = [t.nb_passagers for t in trains]
    total = sum(nombres)

    return {
        "total_trains": len(trains),
        "total_passagers": total,
        "moyenne": round(total / len(trains), 2),
        "minimum": min(nombres),
        "maximum": max(nombres),
    }
