from dataclasses import dataclass


@dataclass
class BinaryDistribution:
    """
    For modeling the probabilistic distribution.
    """
    masc: float
    fem: float


@dataclass
class Distribution:
    """
    For modeling the probabilistic distribution in the morphological trie.
    """
    quest: float
    masc: float
    fem: float

    def to_binary_distribution(self) -> BinaryDistribution:
        return BinaryDistribution(masc=self.masc / (self.masc + self.fem), fem=self.fem / (self.masc + self.fem))


@dataclass
class Frequency:
    quest: int
    masc: int
    fem: int

    @property
    def total(self) -> int:
        return self.quest + self.masc + self.fem

    def to_distribution(self) -> Distribution:
        return Distribution(quest=self.quest / self.total, masc=self.masc / self.total, fem=self.fem / self.total)
