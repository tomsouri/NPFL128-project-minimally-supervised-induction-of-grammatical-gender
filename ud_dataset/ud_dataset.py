from typing import TextIO
import os
import sys
import urllib.request

from config import DATA_DIR


def is_comment_line(line: str) -> bool:
    return len(line) > 0 and line[0] == "#"


class UDDataset:
    _URL: str = "https://raw.githubusercontent.com/UniversalDependencies/UD_Czech-PDT/master/"

    class Dataset:
        def __init__(self, data_file: TextIO, max_tokens: int | None = None) -> None:
            # Load the data
            self._size = 0
            self.forms = []
            self.poss = []
            self.genders = []

            for line in data_file:
                line = line.strip()
                if line:
                    if not is_comment_line(line):
                        columns = line.split("\t")
                        form = columns[1]
                        pos = columns[3]
                        if columns[4] == "_":
                            pos = None
                            gender = None
                        else:
                            gender = columns[4][2]
                            if gender == "I":
                                # ignore animate/inanimate distinction
                                gender = "M"
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
            noun_set = set(nouns)
            return noun_set

    def __init__(self, max_tokens=None):
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
    def evaluate(gold_dataset: "UDDataset.Dataset", predictions: list[str]) -> float:
        gold_genders = gold_dataset.genders
        gold_poss = gold_dataset.poss

        if len(predictions) != len(gold_genders):
            raise RuntimeError("The predictions contain different number of tokens than gold data: {} vs {}".format(
                len(predictions), len(gold_genders)))

        correct, total = 0, 0

        for line, gold_gender, gold_pos in zip(predictions, gold_genders, gold_poss):

            if gold_pos != "NOUN":
                # not noun, no need to evaluate
                continue

            prediction = line.rstrip("\n")
            total += 1
            if prediction == gold_gender:
                correct += 1

        return correct / total

    @staticmethod
    def evaluate_file(gold_dataset: "UDDataset.Dataset", predictions_file: TextIO) -> float:
        predictions = predictions_file.readlines()
        return UDDataset.evaluate(gold_dataset, predictions)
