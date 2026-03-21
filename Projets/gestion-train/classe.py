"""
classe.py
---------
Définition des modèles de données : Train et Gare.
"""

from dataclasses import dataclass


@dataclass
class Train:
    """Représente un enregistrement de passage de train en gare."""

    date: str          # Format attendu : JJ-MM-AAAA
    heure: str         # Format attendu : HHhMM  (ex: 15h07)
    numero: str        # Ex: TER245, TER_002
    nb_passagers: int  # Doit être >= 0
    type_train: str    # "Arrivée" ou "Départ"

    def to_dict(self) -> dict:
        """Sérialise le train en dictionnaire pour l'écriture CSV."""
        return {
            "Date": self.date,
            "Heure": self.heure,
            "Num_Train": self.numero,
            "Nb_Passager": self.nb_passagers,
            "Type_Train": self.type_train,
        }

    def __str__(self) -> str:
        """
        Représentation lisible du train.
        Utilisée directement par print() — plus idiomatique que afficher().
        """
        return (
            f"Date : {self.date} | Heure : {self.heure} | "
            f"Train : {self.numero} | Passagers : {self.nb_passagers} | "
            f"Type : {self.type_train}"
        )

    def afficher(self) -> str:
        """Alias de __str__ pour la compatibilité avec le reste du code."""
        return str(self)


class Gare:
    """
    Conteneur principal représentant une gare.

    Centralise la liste des trains chargés en mémoire et expose
    des méthodes de filtrage simples.

    Note : l'attribut interne _trains est protégé pour éviter
    les modifications accidentelles depuis l'extérieur.
    """

    def __init__(self, nom: str) -> None:
        self.nom = nom
        self._trains: list[Train] = []

    # ------------------------------------------------------------------
    # Gestion de la liste
    # ------------------------------------------------------------------

    def charger_trains(self, trains: list[Train]) -> None:
        """Remplace la liste en mémoire par une nouvelle liste."""
        self._trains = list(trains)

    def ajouter_train(self, train: Train) -> None:
        """Ajoute un train en mémoire (sans écrire dans le fichier CSV)."""
        self._trains.append(train)

    # ------------------------------------------------------------------
    # Accès et filtrage
    # ------------------------------------------------------------------

    def tous_les_trains(self) -> list[Train]:
        """Retourne une copie de la liste complète des trains."""
        return list(self._trains)

    def filtrer(self, type_train: str | None = None) -> list[Train]:
        """
        Retourne les trains correspondant au type demandé.

        Si type_train est None ou vide, retourne tous les trains.
        Remplace les anciennes méthodes trains_arrivee() / trains_depart()
        qui dupliquaient inutilement la logique de filtrage.
        """
        if not type_train:
            return self.tous_les_trains()
        return [t for t in self._trains if t.type_train == type_train]

    def __len__(self) -> int:
        return len(self._trains)

    def __repr__(self) -> str:
        return f"Gare(nom={self.nom!r}, nb_trains={len(self._trains)})"
