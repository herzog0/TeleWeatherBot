
"""
Wrapper simples em cima do PyOWM, para simplificar as funcionalidades e reduzir os dicts de json
"""
import os
import dateutil.parser
from datetime import datetime, timedelta

from pyowm import OWM
from pyowm.weatherapi25.weather import Weather
from pyowm.exceptions.api_call_error import APICallError

owm_token = os.environ.get('OWM_TOKEN', None)

__owm = None


def get_weather(coords, date=None) -> Weather:
    """
    Retorna um objeto da PyOWM, para uso interno da classe.
    Pode resultar em um NotFoundError da PyOWM também.
    """
    global __owm
    if not __owm:
        __owm = OWM(
            API_key=owm_token,
            config_module='tele_weather_bot.weather.configuration'
            # essa configuração acima muda a linguagem para 'pt' e
            # adiciona um cache simples pra tentar reduzir os requests
        )

    if not __owm.is_API_online():
        raise APICallError

    if date and (date - datetime.now()) > timedelta(hours=3):
        fc = __owm.three_hours_forecast_at_coords(coords['lat'], coords['lng'])
        observation = fc.get_weather_at(date)
    else:
        observation = __owm.weather_at_coords(coords['lat'], coords['lng']).get_weather()

    return observation


def get_weather_description(coords, date=None) -> str:
    """Busca a descrição do tempo no lugar"""
    weather = get_weather(coords, date)
    status = weather.get_detailed_status()
    return status.lower()


def get_temperature(coords, date=None) -> float:
    """Temperatura média no lugar"""
    weather = get_weather(coords, date)
    temp = weather.get_temperature(unit='celsius')
    return temp['temp']


def get_rain(coords, date=None) -> bool:
    """Teste se está chovendo no lugar"""
    weather = get_weather(coords, date)

    # se o status diz, então tá chuvendo
    if weather.get_status().lower() == 'rain':
        return True
    # mas também está se o volume de chuva recente der maior que zero
    else:
        volume = sum(weather.get_rain().items())
        return volume > 0
        # pode ser trocado por `any(weather.get_rain().items())`


def get_humidity(coords, date=None):
    weather = get_weather(coords, date)
    return weather.get_humidity()


def get_clouds(coords, date=None):
    return get_weather(coords, date).get_clouds()


def get_sunset(coords):
    sunset = dateutil.parser.parse(get_weather(coords, date).get_sunset_time('iso'))
    return sunset.hour-3, sunset.minute, sunset.second


def get_sunrise(coords):
    sunrise = dateutil.parser.parse(get_weather(coords, date).get_sunrise_time('iso'))
    return sunrise.hour-3, sunrise.minute, sunrise.second
