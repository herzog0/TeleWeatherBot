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
            API_key=owm_api_key,
            config_module='tele_weather_bot.weather.configuration'
            # essa configuração acima muda a linguagem para 'pt' e
            # adiciona um cache simples pra tentar reduzir os requests
        )

    def get_weather(self, coords, date) -> Weather:
        """
        Retorna um objeto da PyOWM, para uso interno da classe.
        Pode resultar em um NotFoundError da PyOWM também.
        """
        observation = self._owm.weather_at_coords(coords['lat'], coords['lng'])
        return observation.get_weather()

    def get_weather_description(self, coords, date) -> str:
        """Busca a descrição do tempo no lugar"""
        weather = self.get_weather(coords, date)
        status = weather.get_detailed_status()
        return status.lower()

    def get_temperature(self, coords, date) -> float:
        """Temperatura média no lugar"""
        weather = self.get_weather(coords, date)
        temp = weather.get_temperature(unit='celsius')
        return temp['temp']

    def get_temp_variation(self, coords, date) -> tuple:
        """Limites de temperatura no lugar"""
        weather = self.get_weather(coords, date)
        temp = weather.get_temperature(unit='celsius')
        return temp['temp_min'], temp['temp_max']

    def is_rainy(self, coords, date) -> bool:
        """Teste se está chovendo no lugar"""
        weather = self.get_weather(coords, date)

        # se o status diz, então tá chuvendo
        if weather.get_status().lower() == 'rain':
            return True
        # mas também está se o volume de chuva recente der maior que zero
        else:
            volume = sum(weather.get_rain().items())
            return volume > 0
            # pode ser trocado por `any(weather.get_rain().items())`
