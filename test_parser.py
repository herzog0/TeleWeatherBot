from tele_weather_bot.parser.parser import find_hour, find_date, MoreThanFiveDaysException, week_days, \
    find_tag_date_pairs
from datetime import datetime, timedelta
from tele_weather_bot.parser.question_keys import WeatherTypes
import unittest


class TestParser(unittest.TestCase):

    def test_find_hour(self):
        self.assertIsNone(find_hour('12'))
        self.assertEqual(find_hour('23h'), '23')
        self.assertEqual(find_hour('0h'), '0')
        self.assertIsNone(find_hour('24h'))
        self.assertIsNone(find_hour('-1h'))
        self.assertIsNone(find_hour('asd'))
        self.assertIsNone(find_hour('asdh'))

    # engloba testes de less_than_five_days

    def test_find_date(self):

        # passando dia do mês cinco dias a frente
        result = find_date(str((datetime.now() + timedelta(days=5)).day)).date()
        expected = (datetime.now() + timedelta(days=5)).date()
        self.assertEqual(result, expected)

        # passando dia da semana cinco dias a frente
        wd = (datetime.now().weekday() + 5) % 7
        wd = (week_days())[wd].get(wd)[0]
        result = find_date(wd).date()
        expected = (datetime.now() + timedelta(days=5)).date()
        self.assertEqual(result, expected)

        # passando 6 dias do mês a frente
        with self.assertRaises(MoreThanFiveDaysException):
            find_date(str((datetime.now() + timedelta(days=6)).day))

        # with pytest.raises(ValueError):
        #     find_date()

    def test_find_tag_date_pairs(self):

        date = datetime.now()
        tag = WeatherTypes.TEMPERATURE

        tag_date_expected_result = [[tag, date], [tag, date], [tag, date]]

        tag_date_origin = [tag, '', date, date, '', tag, '', '', date]

        self.assertEqual(find_tag_date_pairs(tag_date_origin), tag_date_expected_result)


def test_all():
    unittest.main()


if __name__ == '__main__':
    test_all()