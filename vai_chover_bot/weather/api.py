"""
Wrapper simples em cima do PyOWM, para simplificar as funcionalidades e reduzir os dicts de json
"""

from pyowm import OWM
from pyowm.weatherapi25.weather import Weather



class WeatherAPI:
    """Interface de uso da API do OpenWeatherMap"""
    def __init__(self, owm_api_key: str):
        """Precisa de uma chave/token da API"""
        self._owm = OWM(
            API_key = owm_api_key,
            config_module = 'vai_chover_bot.weather.configuration'
            # essa configuração acima muda a linguagem para 'pt' e
            # adiciona um cache simples pra tentar reduzir os requests
        )


    def _getWeather(self, coords) -> Weather:
        """
        Retorna um objeto da PyOWM, para uso interno da classe.
        Pode resultar em um NotFoundError da PyOWM também.
        """
        observation = self._owm.weather_at_coords(coords['lat'], coords['lng'])
        return observation.get_weather()

    def getWeatherDescription(self, coords) -> str:
        """Busca a descrição do tempo da cidade"""
        weather = self._getWeather(coords)
        status = weather.get_detailed_status()
        return status.lower()

    def getTemperature(self, coords) -> float:
        """Temperatura média da cidade"""
        weather = self._getWeather(coords)
        temp = weather.get_temperature(unit='celsius')
        return temp['temp']

    def getTempVariation(self, coords) -> tuple:
        """Limites de temperatura da cidade"""
        weather = self._getWeather(coords)
        temp = weather.get_temperature(unit='celsius')
        return temp['temp_min'], temp['temp_max']

    def isRainy(self, coords) -> bool:
        """Teste se está chuvendo na cidade"""
        weather = self._getWeather(coords)

        # se o status diz, então tá chuvendo
        if weather.get_status().lower() == 'rain':
            return True
        # mas também está se o volume de chuva recente der maior que zero
        else:
            volume = sum(weather.get_rain().items())
            return volume > 0
            # pode ser trocado por `any(weather.get_rain().items())`
