from enum import Enum, auto, unique


@unique
class QuestionType(Enum):
    WEATHER         = auto()
    TEMPERATURE     = auto()
    HUMIDITY        = auto()

    TEMP_VARIATION  = auto()

    IS_RAINY        = auto()
    IS_SUNNY        = auto()
    IS_CLOUDY       = auto()

    SOURCE          = auto()


class NotUnderstandable(Exception):
    def __init__(self, source_text: str = None):
        if source_text:
            self.source_text = source_text
