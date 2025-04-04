from typing import Sequence

from evidence_modeling.frequency import Frequency
from collections import Counter


def get_initial_gender_frequencies(noun_set: set[str], unannotated_corpus: Sequence[str], masc_seeds: set[str],
                                   fem_seeds: set[str]) -> dict[str, Frequency]:
    """
    For a set of nouns, compute initial frequencies, based on the given seed lists of masculine and feminine nouns.
    :param noun_set: Set of all nouns of the language.
    :param unannotated_corpus: Unannotated corpus for computing the absolute counts.
    :param masc_seeds: Set of masculine noun seeds.
    :param fem_seeds:Set of feminine noun seeds.
    :return: Dictionary of frequencies.
    """
    counts = Counter(unannotated_corpus)
    frequencies = dict()

    for noun in noun_set:
        count = counts[noun]
        if noun in masc_seeds:
            frequency = Frequency(quest=0, masc=count, fem=0)
        elif noun in fem_seeds:
            frequency = Frequency(quest=0, masc=0, fem=count)
        else:
            frequency = Frequency(quest=count, masc=0, fem=0)
        frequencies[noun] = frequency

    return frequencies
