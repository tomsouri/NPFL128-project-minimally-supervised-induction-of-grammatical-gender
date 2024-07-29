from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Sequence

SUFFIX_LENGTH = 1


class ContextType(Enum):
    LEFT_WHOLE_WORD = auto()
    RIGHT_WHOLE_WORD = auto()
    BILATERAL_WHOLE_WORD = auto()
    LEFT_SUFFIX = auto()
    RIGHT_SUFFIX = auto()
    BILATERAL_SUFFIX = auto()


@dataclass(frozen=True)
class Context:
    context_type: ContextType
    left_word: Optional[str] = None
    right_word: Optional[str] = None

    @staticmethod
    def get_from_corpus_index(context_type: ContextType, corpus: Sequence[str], index: int) -> Optional["Context"]:
        if context_type == ContextType.LEFT_WHOLE_WORD:
            if index == 0:
                return None
            else:
                left_word = corpus[index - 1]
                return Context(context_type=context_type, left_word=left_word)

        elif context_type == ContextType.LEFT_SUFFIX:
            if index == 0:
                return None
            else:
                left_word = corpus[index - 1]
                left_suffix = left_word[-SUFFIX_LENGTH:]
                return Context(context_type=context_type, left_word=left_suffix)

        elif context_type == ContextType.BILATERAL_WHOLE_WORD:
            if index == 0 or index == len(corpus) - 1:
                return None
            else:
                left_word = corpus[index - 1]
                right_word = corpus[index + 1]
                return Context(context_type=context_type, left_word=left_word, right_word=right_word)

        elif context_type == ContextType.BILATERAL_SUFFIX:
            if index == 0 or index == len(corpus) - 1:
                return None
            else:
                left_word = corpus[index - 1]
                right_word = corpus[index + 1]
                left_suffix = left_word[-SUFFIX_LENGTH:]
                right_suffix = right_word[-SUFFIX_LENGTH:]
                return Context(context_type=context_type, left_word=left_suffix, right_word=right_suffix)

        elif context_type == ContextType.RIGHT_WHOLE_WORD:
            if index == len(corpus) - 1:
                return None
            else:
                right_word = corpus[index + 1]
                return Context(context_type=context_type, right_word=right_word)

        elif context_type == ContextType.RIGHT_SUFFIX:
            if index == len(corpus) - 1:
                return None
            else:
                right_word = corpus[index + 1]
                right_suffix = right_word[-SUFFIX_LENGTH:]
                return Context(context_type=context_type, right_word=right_suffix)
