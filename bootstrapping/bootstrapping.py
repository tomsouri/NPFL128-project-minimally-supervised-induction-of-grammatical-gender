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

    # if masc > fem:
    #     return Gender.MASCULINE
    # elif fem > masc:
    #     return Gender.FEMININE
    # else:
    #     return None
    #
    # if masc > 0 and fem == 0:
    #     return Gender.MASCULINE
    # elif fem > 0 and masc == 0:
    #     return Gender.FEMININE
    # else:
    #     return None


def extract_relevant_contexts(
        updated_contexts: set[Context],
        context_frequencies: dict[Context, Frequency]) -> tuple[set[Context], set[Context]]:
    """
    Extract relevant contexts by iteratively descreasing the treshold until some contexts are considered relevant.
    :param updated_contexts: Contexts that have been updated in the last run.
    :param context_frequencies:
    :return:
    """
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
    print(new_masc_contexts)
    print(f"Newly added {len(new_fem_contexts)} contexts to FEM")
    print(new_fem_contexts)

    return new_masc_contexts, new_fem_contexts


def update_frequencies_and_get_updated_contexts(
        context_frequencies: dict[Context, Frequency],
        all_new_nouns: set[str],
        new_masc_nouns: set[str]
) -> set[Context]:
    """
    Go through the corpus, and on every newly added noun update the counts of the corresponding contexts. Modifies the
    given context frequencies dictionary.
    :param new_masc_nouns:
    :param all_new_nouns:
    :param context_frequencies:
    :return: The set of updated contexts.
    """

    updated_contexts = set()
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

    return updated_contexts


def extract_relevant_masc_fem_nouns(updated_words: set[str], noun_frequencies: dict[str, Frequency]) -> tuple[
    set[str], set[str]]:
    """
    Extract relevant masculine and feminine nouns.
    :param updated_words:
    :param noun_frequencies:
    :return:
    """
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

    return new_masc_nouns, new_fem_nouns

def update_noun_frequencies_and_get_updated_words(
        unannotated_corpus: Sequence[str],
        all_new_contexts: set[Context],
        all_nouns: set[str],
        noun_frequencies: dict[str, Frequency],
        new_masc_contexts: set[Context]
        ) -> set[str]:
    """
    Updates the noun frequencies, based on new contexts.
    :param unannotated_corpus: Sequence of words, unannotated corpus.
    :param all_new_contexts: All new contexts (fem and masc)
    :param all_nouns: Set of all tokens considered to be nouns.
    :param noun_frequencies: Is modified in place.
    :param new_masc_contexts: New masc contexts.
    :return: set of updated words
    """
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

    return updated_words


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
    to correspond to the counts in the given unannotated corpus and to the sets of feminine/masculine seeds. The
    original frequencies are not modified, new frequencies are returned as the third return value.
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

        all_new_nouns = new_masc_nouns | new_fem_nouns

        updated_contexts = update_frequencies_and_get_updated_contexts(context_frequencies=context_frequencies,
                                                                       all_new_nouns=all_new_nouns,
                                                                       new_masc_nouns=new_masc_nouns)

        # Filter for relevant contexts:
        new_masc_contexts, new_fem_contexts = extract_relevant_contexts(updated_contexts=updated_contexts,
                                                                        context_frequencies=context_frequencies)

        # Now, go through all the words and if their context has been added to some gender, update their counts.
        all_new_contexts |= new_masc_contexts | new_fem_contexts

        updated_words = update_noun_frequencies_and_get_updated_words(
            unannotated_corpus=unannotated_corpus,
            all_new_contexts=all_new_contexts,
            all_nouns=all_nouns,
            noun_frequencies=noun_frequencies,
            new_masc_contexts=new_masc_contexts
        )

        # from the set of updated words, remove those that were already decided
        updated_words -= all_fem_nouns | all_masc_nouns

        new_masc_nouns, new_fem_nouns = extract_relevant_masc_fem_nouns(updated_words=updated_words,
                                                                        noun_frequencies=noun_frequencies)

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
