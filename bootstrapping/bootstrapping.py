from typing import Sequence, Optional, Iterator
from collections import Counter
import copy

from evidence_modeling.frequency import Frequency
from bootstrapping.contexts import ContextType, Context
from gender import Gender

ALLOWED_CONTEXT_MODELS = [ContextType.LEFT_WHOLE_WORD, ContextType.RIGHT_WHOLE_WORD, ContextType.BILATERAL_WHOLE_WORD,
                          ContextType.LEFT_SUFFIX, ContextType.RIGHT_SUFFIX, ContextType.BILATERAL_SUFFIX]


def is_context_gender_specific(context_frequency: Frequency, fraction_to_allow: float = 0.5) -> Optional[Gender]:
    """
    Defines the condition for filtering, whether the context absolute counts are relevant enough to decide whether the
    context is masculine or feminine.
    :param fraction_to_allow:
    :param context_frequency: Frequency containing absolute counts of the context.
    :return: Specific gender if the counts are relevant enough, or None if we cannot decide.
    """

    # TODO: here are multiple possibilities on the conditions:
    # 1. fem > masc + quest/2, resp. masc > fem + quest/2
    # 2. fem > 0 and masc = 0 (or fem > n and masc = 0)
    # 3. fem > masc

    # We try option number 1, with adjustable weight for the fraction of questionable

    masc = context_frequency.masc
    fem = context_frequency.fem
    quest = context_frequency.quest

    if masc > quest * fraction_to_allow + fem:
        return Gender.MASCULINE
    elif fem > quest * fraction_to_allow + masc:
        return Gender.FEMININE
    else:
        return None


def update_frequencies_by_bootstrapping(masc_seeds: set[str], fem_seeds: set[str], all_nouns: set[str],
                                        unannotated_corpus: Sequence[str],
                                        original_frequencies: dict[str, Frequency]) -> \
        tuple[set[str], set[str], dict[str, Frequency]]:
    """
    Perform context bootstrapping to get new almost-surely masculine/feminine nouns.
    :param masc_seeds: Nouns that have surely masculine gender (seeds).
    :param fem_seeds: Nouns that have surely feminine gender (seeds).
    :param all_nouns: Set of all strings from the language to be considered nouns.
    :param unannotated_corpus: Corpus consisting of tokens, unannotated for any linguistic information.
    :param original_frequencies: The original frequency counts before bootstrapping. The given frequencies are expected
    to correspond to the counts in the given unannotated corpus and to the sets of feminine/masculine seeds.
    :return: all masculine nouns, all feminine nouns and updated frequencies.
    """
    all_masc_nouns = masc_seeds.copy()
    all_fem_nouns = fem_seeds.copy()

    new_masc_nouns = masc_seeds.copy()
    new_fem_nouns = fem_seeds.copy()
    noun_frequencies = copy.deepcopy(original_frequencies)

    # Initialize for bootstrapping:
    context_frequencies = get_initial_gender_frequencies_of_contexts(unannotated_corpus=unannotated_corpus,
                                                                     allowed_context_types=ALLOWED_CONTEXT_MODELS)

    iteration_no = 0
    all_new_contexts = set()

    # Repeat until no update is performed:
    while new_masc_nouns | new_fem_nouns:
        print(f"Bootstrapping: iteration no. {iteration_no} is running...")
        iteration_no += 1

        updated_contexts = set()
        all_new_nouns = new_masc_nouns | new_fem_nouns

        # Go through the corpus, and on every newly added noun update the counts of the corresponding contexts
        for current_word, context in iterate_over_words_and_contexts(corpus=unannotated_corpus,
                                                                     context_types=ALLOWED_CONTEXT_MODELS):
            if current_word in all_new_nouns:
                context_frequency = context_frequencies[context]
                context_frequency.quest -= 1
                if current_word in new_masc_nouns:
                    context_frequency.masc += 1
                else:
                    context_frequency.fem += 1
                updated_contexts.add(context)

        # Filter for relevant contexts:
        new_masc_contexts = set()
        new_fem_contexts = set()

        # Iteratively decrease the weight determining which contexts will be considered relevant, until at least one
        # relevant context is found.
        fraction_to_allow = 0.5
        added = False
        while not added:
            for context in updated_contexts:
                gender = is_context_gender_specific(context_frequencies[context], fraction_to_allow=fraction_to_allow)
                if gender == Gender.MASCULINE:
                    new_masc_contexts.add(context)
                    added = True
                elif gender == Gender.FEMININE:
                    new_fem_contexts.add(context)
                    added = True

            # decrease the weight a little bit
            fraction_to_allow /= 1.2

            # stop if too many iterations
            if fraction_to_allow < 0.1:
                break

        print(f"Newly added {len(new_masc_contexts)} contexts to MASC")
        print(f"Newly added {len(new_fem_contexts)} contexts to FEM")

        # Now, go through all the words and if their context has been added to some gender, update their counts.
        all_new_contexts |= new_masc_contexts | new_fem_contexts
        updated_words = set()

        for word, context in iterate_over_words_and_contexts(corpus=unannotated_corpus,
                                                             context_types=ALLOWED_CONTEXT_MODELS):
            if context in all_new_contexts and word in all_nouns:
                noun_frequency = noun_frequencies[word]
                noun_frequency.quest -= 1
                if context in new_masc_contexts:
                    noun_frequency.masc += 1
                else:
                    noun_frequency.fem += 1
                updated_words.add(word)

        # from the set of updated words, remove those that were already decided
        updated_words -= all_fem_nouns | all_masc_nouns

        # Now, filter for relevant nouns
        new_masc_nouns = set()
        new_fem_nouns = set()

        fraction_to_allow = 0.5
        while not new_fem_nouns | new_masc_nouns:
            for word in updated_words:
                gender = is_context_gender_specific(noun_frequencies[word], fraction_to_allow=fraction_to_allow)
                if gender == Gender.MASCULINE:
                    new_masc_nouns.add(word)
                elif gender == Gender.FEMININE:
                    new_fem_nouns.add(word)

            fraction_to_allow /= 1.2

            # stop if too many iterations
            if fraction_to_allow < 0.1:
                break

        # update lists of all fem/masc nouns
        all_fem_nouns |= new_fem_nouns
        all_masc_nouns |= new_masc_nouns

        print(f"Newly added {len(new_masc_nouns)} nouns to MASC (total masc nouns = {len(all_masc_nouns)})")
        print(new_masc_nouns)
        print(f"Newly added {len(new_fem_nouns)} nouns to FEM  (total fem nouns = {len(all_fem_nouns)})")
        print(new_fem_nouns)

    print(f"Total number of MASC nouns: {len(all_masc_nouns)} (cf. #masc seeds={len(masc_seeds)})")
    print(f"Total number of FEM nouns: {len(all_fem_nouns)} (cf. #fem seeds={len(fem_seeds)})")
    print(f"Nouns with unknown gender: {len(all_nouns - all_masc_nouns - all_fem_nouns)}")

    return all_masc_nouns, all_fem_nouns, noun_frequencies


def iterate_over_words_and_contexts(
        corpus: Sequence[str],
        context_types: Sequence[ContextType]) -> Iterator[tuple[str, Context]]:
    """
    For given corpus and set of context types, iterate over all pairs (word, context of the word).
    """
    for i in range(len(corpus)):
        for context_type in context_types:
            context = Context.get_from_corpus_index(context_type=context_type, corpus=corpus, index=i)
            word = corpus[i]
            if context is not None:
                yield word, context


def get_initial_gender_frequencies_of_contexts(
        unannotated_corpus: Sequence[str],
        allowed_context_types: Sequence[ContextType]) -> dict[Context, Frequency]:
    """
    For a given unannotated corpus and allowed types of contexts, extract all contexts present in the unannotated corpus
    and initialize their counts.
    :param allowed_context_types:
    :param unannotated_corpus: Unannotated corpus for computing the absolute counts.
    :return: Dictionary of frequencies.
    """
    all_contexts = [Context.get_from_corpus_index(context_type=context_type, corpus=unannotated_corpus, index=i) for
                    context_type in allowed_context_types for i in range(len(unannotated_corpus))]

    context_counts = Counter(all_contexts)

    frequencies = dict()

    for context in context_counts:
        count = context_counts[context]
        frequency = Frequency(quest=count, masc=0, fem=0)
        frequencies[context] = frequency

    return frequencies
