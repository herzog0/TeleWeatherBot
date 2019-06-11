from tele_weather_bot.parser.parser import find_hour, find_date, MoreThanFiveDaysException, week_days, \
    find_tag_date_pairs, address
from datetime import datetime, timedelta
from tele_weather_bot.parser.question_keys import WeatherTypes
from tele_weather_bot.google_maps.geocode_functions import set_gmaps_obj
from .mock_classes.mock_geocode_functions import GeoMock, LocationNotFoundException
import pytest


def test_address():
    gmaps = GeoMock()
    assert address("campinas", gmaps) == ("campinas", None)
    assert address({"lat": 20.2, "lng": 30.3}, gmaps) == ("20.2 30.3", None)
    with pytest.raises(LocationNotFoundException):
        address("", gmaps)


def test_find_hour():
    assert find_hour('12') is None
    assert find_hour('23h') == '23'
    assert find_hour('0h') == '0'
    assert find_hour('24h') is None
    assert find_hour('-1h') is None
    assert find_hour('asd') is None
    assert find_hour('asdh') is None


# engloba testes de less_than_five_days

def test_find_date():
    # passando dia do mês cinco dias a frente
    assert find_date(str((datetime.now() + timedelta(days=5)).day)).date() == \
           (datetime.now() + timedelta(days=5)).date()

    # passando dia da semana cinco dias a frente

    wd = (datetime.now().weekday() + 5) % 7
    wd = week_days[wd].get(wd)[0]
    assert find_date(wd).date() == (datetime.now() + timedelta(days=5)).date()

    with pytest.raises(MoreThanFiveDaysException):
        find_date(str((datetime.now() + timedelta(days=6)).day))

    # with pytest.raises(ValueError):
    #     find_date()


def test_find_tag_date_pairs():

    date = datetime.now()
    tag = WeatherTypes.TEMPERATURE

    tag_date_expected_result = [[tag, date], [tag, date], [tag, date]]

    tag_date_origin = [tag, '', date, date, '', tag, '', '', date]

    assert find_tag_date_pairs(tag_date_origin) == tag_date_expected_result
