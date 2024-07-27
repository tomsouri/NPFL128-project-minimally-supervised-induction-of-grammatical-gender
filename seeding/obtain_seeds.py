#!/usr/bin/env python3

from pathlib import Path

from seeding.translate import translate


def load_seeds(filepath: Path) -> list[str]:
    """
    Loads seeds from given file.
    :param filepath: file to load seeds from
    :return: list of seeds
    """
    with open(filepath, "r") as f:
        lines = f.read().splitlines()
    return lines


def detect_translation_gender_collisions(masc_list: list[str], fem_list: list[str]) -> list[str]:
    """
    In two lists of strings, find all words appearing in both lists.
    :param masc_list: first list
    :param fem_list: second list
    :return: list of collisions
    """
    return [masc for masc in masc_list if masc in fem_list]


def filter_phrases(word_list: list[str]) -> list[str]:
    """
    From given list of strings, filters out non-words (empty words, phrases).
    :param word_list: List of strings to be filtered.
    :return: Words from the given list.
    """
    return [word for word in word_list if len(word.split(" ")) == 1]


def obtain_seeds(en_masc_seeds_filepath, en_fem_seeds_filepath) -> tuple[list[str], list[str]]:
    """
    Returns the list of seed nouns for the Czech language, as a tuple of list of masc and fem seed nouns.
    :return: list of masculine seeds, list of feminine seeds
    """
    en_masc_seeds = load_seeds(en_masc_seeds_filepath)
    en_fem_seeds = load_seeds(en_fem_seeds_filepath)

    cz_masc_translated = [translate(en_seed) for en_seed in en_masc_seeds]
    cz_fem_translated = [translate(en_seed) for en_seed in en_fem_seeds]

    cz_masc_filtered = filter_phrases(cz_masc_translated)
    cz_fem_filtered = filter_phrases(cz_fem_translated)

    collisions = detect_translation_gender_collisions(cz_masc_filtered, cz_fem_filtered)

    cz_masc_no_collisions = [w for w in cz_masc_filtered if w not in collisions]
    cz_fem_no_collisions = [w for w in cz_fem_filtered if w not in collisions]

    return (cz_masc_no_collisions, cz_fem_no_collisions)
