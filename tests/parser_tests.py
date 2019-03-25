from vai_chover_bot import parser
import unittest
import re

class ParserTestSuite(unittest.TestCase):
    def __init__(self, methodName):
        self._parser = parser.QuestionParser()
        super().__init__(methodName)


    def test_weather_for_one_word_city_names(self):
        cities = ['Campinas', 'campinas', 'cAmPiNaS', 'Goiania', 'desnomeada']

        for city in cities:
            type, [city_name] = self._parser.parse(city)

            self.assertIs(type, parser.QuestionType.WEATHER)
            self.assertTrue(re.fullmatch(city, city_name, re.IGNORECASE | re.UNICODE))

    def test_weather_for_two_word_city_names(self):
        cities = ['São Paulo', 'belo horizonte', 'sem nome']

        for city in cities:
            type, [city_name] = self._parser.parse(city)

            self.assertIs(type, parser.QuestionType.WEATHER)
            self.assertTrue(re.fullmatch(city, city_name, re.IGNORECASE | re.UNICODE))

    def fail_weather_for_more_words(self):
        cities = ['rio de janeiro', 'são pedro da aldeia', 'são tomé das letras']

        for city in cities:
            with self.assertRaises(parser.CouldNotUnderstandException):
                self._parser.parse(city)
