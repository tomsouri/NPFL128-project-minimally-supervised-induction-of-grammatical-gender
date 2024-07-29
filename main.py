import sys
import os

from seeding.obtain_seeds import obtain_seeds
from config import EN_MASC_SEEDS_FILEPATH, EN_FEM_SEEDS_FILEPATH

from ud_dataset.ud_dataset import UDDataset
from gender import Gender
from evidence_modeling.gender_predictor import GenderPredictor


def main() -> None:
    # Translation of English seed nouns, removing collisions, no manual check
    masc_seeds, fem_seeds = obtain_seeds(EN_MASC_SEEDS_FILEPATH, EN_FEM_SEEDS_FILEPATH)

    # Initialization of UD datasets, downloads the data if necessary and processes them
    ud = UDDataset()

    # print(ud.evaluate(ud.test, [Gender.MASCULINE] * len(ud.test)))

    # The set of all forms of all Czech nouns  (for simplification and faster computation, we use only the noun forms
    # present in our datasets)
    noun_set = ud.train.get_unique_nouns() | ud.dev.get_unique_nouns() | ud.test.get_unique_nouns()

    print(f"Total number of nouns in the language: {len(noun_set)}")

    unannotated_corpus = ud.train.text

    gender_predictor = GenderPredictor(masc_seeds=masc_seeds, fem_seeds=fem_seeds, nouns=noun_set,
                                       unannotated_corpus=unannotated_corpus)

    gender_predictor.bootstrap_from_context()

    dataset = ud.dev

    predictions = gender_predictor.predict_gender_for_corpus(dataset.text)

    print(ud.evaluate(dataset, predictions))

    print()
    print("Predictions by chance:")
    print("Predict all fem:")
    print(ud.evaluate(dataset, [Gender.FEMININE] * len(dataset)))
    print("Predict all masc:")
    print(ud.evaluate(dataset, [Gender.MASCULINE] * len(dataset)))


if __name__ == "__main__":
    main()
