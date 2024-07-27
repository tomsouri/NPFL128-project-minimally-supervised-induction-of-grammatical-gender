from dataclasses import dataclass


@dataclass
class Distribution:
    masc: float
    fem: float


@dataclass
class Frequency:
    quest: int
    masc: int
    fem: int

    def get_distribution(self):
        return Distribution(masc=self.masc / (self.masc + self.fem), fem=self.fem / (self.masc + self.fem))

    @property
    def total_count(self):
        return self.quest + self.masc + self.fem
