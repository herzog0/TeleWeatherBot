from .question import QuestionType, NotUnderstandable

import string


class QuestionParser:
    def parse(self, text: str) -> str:
        text = text.split()
        if len(text) == 1:
            city = text[0].strip(string.punctuation)
            return QuestionType.WEATHER, [city]

        raise NotUnderstandable(text)
