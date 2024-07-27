import sys
import os

from seeding.obtain_seeds import obtain_seeds
from config import EN_MASC_SEEDS_FILEPATH, EN_FEM_SEEDS_FILEPATH


def main() -> None:
    masc_seeds, fem_seeds = obtain_seeds(EN_MASC_SEEDS_FILEPATH, EN_FEM_SEEDS_FILEPATH)
    print(masc_seeds, fem_seeds)


if __name__ == "__main__":
    main()
