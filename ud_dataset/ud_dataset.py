from typing import TextIO, Sequence
import os
import sys
import urllib.request
from collections import Counter

from config import DATA_DIR
import conllu

from gender import Gender
from typing import Optional
from dataclasses import dataclass


@dataclass
class EvaluationMetric:
    precision: float
    recall: float


class UDDataset:
    _URL: str = "https://raw.githubusercontent.com/UniversalDependencies/UD_Czech-PDT/master/"

    class Dataset:
        def __init__(self, data_file: TextIO, max_tokens: int | None = None) -> None:
            # Load the data
            self._size = 0
            self.forms = []
            self.poss = []
            self.genders = []

            for sentence in conllu.parse_incr(data_file):
                for token in sentence:
                    form = token.get("form")
                    pos = token.get("upostag")
                    gender = None
                    if 'feats' in token and token['feats'] is not None:
                        feats = token['feats']
                        if 'Gender' in feats:
                            gender = feats['Gender']

                            if gender == "Masc":
                                gender = Gender.MASCULINE
                            elif gender == "Fem":
                                gender = Gender.FEMININE
                            else:
                                gender = Gender.OTHER
                    self.forms.append(form)
                    self.poss.append(pos)
                    self.genders.append(gender)
                    self._size += 1
                    if max_tokens is not None and self._size >= max_tokens:
                        break

        def __len__(self) -> int:
            return self._size

        def __getitem__(self, index: int) -> str:
            return self.forms[index]

        @property
        def text(self) -> list[str]:
            """
            Get the unannotated text of the dataset, as a list of tokens.
            :return: The unannotated text.
            """
            return self.forms

        def get_unique_nouns(self) -> set[str]:
            """
            Extracts the set of unique nouns from the dataset.
            :return: The set of unique nouns.
            """
            nouns = [form for (form, pos) in zip(self.forms, self.poss) if pos == "NOUN"]

            # Filter for errors: consider a word to be a noun only if it appears more than 4 times annotated as a NOUN.
            counts = Counter(nouns)
            relevant_nouns = [noun for noun in counts if counts[noun] > 4]
            noun_set = set(relevant_nouns)
            return noun_set

    def __init__(self, max_tokens=None) -> None:
        for dataset_name, dataset in zip(["train-lt", "dev", "test"], ["train", "dev", "test"]):
            # for dataset_name, dataset in zip(["train-ca", "dev", "test"], ["train", "dev", "test"]):
            filename = f"cs_pdt-ud-{dataset_name}.conllu"
            path = DATA_DIR / filename
            if not os.path.exists(path):
                print("Downloading dataset {}...".format(filename), file=sys.stderr)
                urllib.request.urlretrieve(
                    "{}/{}".format(self._URL, filename), filename="{}.tmp".format(path))
                os.rename("{}.tmp".format(path), path)
            with open(path, "r") as dataset_file:
                setattr(self, dataset, self.Dataset(dataset_file, max_tokens=max_tokens))

    train: Dataset
    dev: Dataset
    test: Dataset

    # Evaluation infrastructure.
    @staticmethod
    def evaluate(gold_dataset: "UDDataset.Dataset", predictions: Sequence[Optional[Gender]]) -> EvaluationMetric:
        """
        Evaluate the precision and recall of given predictions on a gold dataset. Predictions on not-noun-words and
        nouns with unknown gold gender are not evaluated.
        :param gold_dataset: The dataset for comparison.
        :param predictions: List of predicted genders.
        :return: Evaluation metric containing the precision and recall values.
        """
        gold_genders = gold_dataset.genders
        poss = gold_dataset.poss

        if len(predictions) != len(gold_genders):
            raise RuntimeError("The predictions contain different number of tokens than gold data: {} vs {}".format(
                len(predictions), len(gold_genders)))

        correct, total, predicted_sth = 0, 0, 0

        for prediction, gold_gender, pos in zip(predictions, gold_genders, poss):

            if pos != "NOUN" or gold_gender is None:
                # not noun or unknown gold gender, no need to evaluate
                continue

            total += 1
            if prediction is not None:
                predicted_sth += 1
                if prediction == gold_gender:
                    correct += 1

        precision = correct / predicted_sth
        recall = predicted_sth / total
        return EvaluationMetric(precision=precision, recall=recall)
