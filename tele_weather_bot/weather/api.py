
"""
Wrapper simples em cima do PyOWM, para simplificar as funcionalidades e reduzir os dicts de json
"""
import os

from pyowm import OWM
from pyowm.weatherapi25.weather import Weather


owm_token = os.environ.get('OWM_TOKEN', None)

__owm = None


def get_weather(coords, date) -> Weather:
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
    observation = __owm.weather_at_coords(coords['lat'], coords['lng'])
    return observation.get_weather()


def get_weather_description(coords, date) -> str:
    """Busca a descrição do tempo no lugar"""
    weather = get_weather(coords, date)
    status = weather.get_detailed_status()
    return status.lower()


def get_temperature(coords, date) -> float:
    """Temperatura média no lugar"""
    weather = get_weather(coords, date)
    temp = weather.get_temperature(unit='celsius')
    return temp['temp']


def get_temp_variation(coords, date) -> tuple:
    """Limites de temperatura no lugar"""
    weather = get_weather(coords, date)
    temp = weather.get_temperature(unit='celsius')
    return temp['temp_min'], temp['temp_max']


def is_rainy(coords, date) -> bool:
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
