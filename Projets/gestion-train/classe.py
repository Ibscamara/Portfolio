from dataclasses import dataclass


@dataclass
class Train:
    date: str
    heure: str
    numero: str
    nb_passagers: int
    type_train: str

    def to_dict(self) -> dict:
        return {
            "Date": self.date,
            "Heure": self.heure,
            "Num_Train": self.numero,
            "Nb_Passager": self.nb_passagers,
            "Type_Train": self.type_train,
        }

    def afficher(self) -> str:
        return (
            f"Date : {self.date} | Heure : {self.heure} | "
            f"Train : {self.numero} | Passagers : {self.nb_passagers} | "
            f"Type : {self.type_train}"
        )


class Gare:
    def __init__(self, nom: str):
        self.nom = nom
        self.trains: list[Train] = []

    def charger_trains(self, trains: list[Train]) -> None:
        self.trains = trains

    def ajouter_train(self, train: Train) -> None:
        self.trains.append(train)

    def trains_arrivee(self) -> list[Train]:
        return [train for train in self.trains if train.type_train == "Arrivée"]

    def trains_depart(self) -> list[Train]:
        return [train for train in self.trains if train.type_train == "Départ"]

    def tous_les_trains(self) -> list[Train]:
        return self.trains.copy()
