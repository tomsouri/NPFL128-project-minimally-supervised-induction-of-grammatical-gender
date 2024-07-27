import sys
import os

from seeding.obtain_seeds import obtain_seeds
from config import EN_MASC_SEEDS_FILEPATH, EN_FEM_SEEDS_FILEPATH

from ud_dataset.ud_dataset import UDDataset


def main() -> None:
    # Translation of English seed nouns, removing collisions, no manual check
    masc_seeds, fem_seeds = obtain_seeds(EN_MASC_SEEDS_FILEPATH, EN_FEM_SEEDS_FILEPATH)

    # Initialization of UD datasets, downloads the data if necessary and processes them
    ud = UDDataset()

    # The set of all forms of all Czech nouns  (for simplification and faster computation, we use only the noun forms
    # present in our datasets)
    noun_set = ud.train.get_unique_nouns() | ud.dev.get_unique_nouns() | ud.test.get_unique_nouns()

    unannotated_corpus = ud.train.text


if __name__ == "__main__":
    main()
