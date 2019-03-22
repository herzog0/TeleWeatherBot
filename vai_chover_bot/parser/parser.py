from .question import QuestionType, NotUnderstandable

import string

def get_city(words: list) -> str:
    city = ' '.join(map(lambda s: s.capitalize(), words))
    return city.strip(string.punctuation)

class QuestionParser:
    def parse(self, text: str) -> str:
        words = text.lower().split()
        if 1 <= len(words) <= 2:
            return QuestionType.WEATHER, [get_city(words)]

        elif words[:3] == ['como', 'está']:
            return QuestionType.WEATHER, [get_city(words[3:])]

        elif words[:3] == ['está', 'chuvendo', 'em']:
            return QuestionType.IS_RAINY, [get_city(words[3:])]

        elif words[0] == 'quão':
            if words[1] == 'quente' or words[1] == 'frio':
                if words[2] == 'está':
                    if words[3] == 'em':
                        return QuestionType.TEMPERATURE, [get_city(words[4:])]
                    else:
                        return QuestionType.TEMPERATURE, [get_city(words[3:])]
                elif words[2] == 'pode':
                    if words[3] == 'ficar':
                        if words[4] == 'em':
                            return QuestionType.TEMP_VARIATION, [get_city(words[5:])]


        raise NotUnderstandable(text)
