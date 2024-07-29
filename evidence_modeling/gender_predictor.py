from gender import Gender
from evidence_modeling.frequency import Frequency
from evidence_modeling.evidence_modeling import get_initial_gender_frequencies
from typing import Optional, Sequence
from bootstrapping.bootstrapping import update_frequencies_by_bootstrapping


class GenderPredictor:
    known_masculines: set[str]
    known_feminines: set[str]
    frequencies: dict[str, Frequency]
    unannotated_corpus: Sequence[str]

    def __init__(self, masc_seeds: set[str], fem_seeds: set[str], nouns: set[str], unannotated_corpus: Sequence[str]):
        self.known_masculines = masc_seeds
        self.known_feminines = fem_seeds
        self.all_nouns = nouns
        self.unannotated_corpus = unannotated_corpus
        self.frequencies = get_initial_gender_frequencies(noun_set=nouns, unannotated_corpus=unannotated_corpus,
                                                          masc_seeds=masc_seeds, fem_seeds=fem_seeds)

    def predict_gender(self, word: str) -> Optional[Gender]:
        """
        Based on its sets of nouns known to be masculine/feminine predicts the gender for a given word. If the word
        is not a noun (based on the set of known nouns), returns None. For nouns outside the sets of nouns with known
        gender, returns None.
        :param word: The string for which to predict the gender.
        :return: The predicted gender, None for not-nouns and not-known gender.
        """
        if word not in self.frequencies:
            return None
        freq = self.frequencies[word]

        # we do not know anything about the word
        if freq.masc == 0 and freq.fem == 0:
            return None

        # we are uncertain about the gender
        if freq.masc == freq.fem:
            return None

        if freq.masc > freq.fem:
            return Gender.MASCULINE
        else:
            return Gender.FEMININE

    def predict_gender_for_corpus(self, corpus: Sequence[str]) -> Sequence[Optional[Gender]]:
        """
        Predict gender for each word from the given corpus.
        :param corpus: Corpus as a sequence of tokens.
        :return: Sequence of predicted genders.
        """
        return [self.predict_gender(word) for word in corpus]

    def bootstrap_from_context(self) -> None:
        """
        Using an unannotated corpus, extend the set of known masculines/feminines of the predictor, with the method
        of context bootstrapping.
        """
        self.known_masculines, self.known_feminines, self.frequencies = update_frequencies_by_bootstrapping(
            masc_seeds=self.known_masculines,
            fem_seeds=self.known_feminines,
            all_nouns=self.all_nouns,
            unannotated_corpus=self.unannotated_corpus,
            original_frequencies=self.frequencies)
