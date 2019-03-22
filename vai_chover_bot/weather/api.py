from pyowm import OWM
from pyowm.weatherapi25.weather import Weather


class WeatherAPI:
    def __init__(self, owm_api_key: str):
        self._owm = OWM(owm_api_key, config_module='vai_chover_bot.weather.configuration')

    def getWeather(self, city: str) -> Weather:
        observation = self._owm.weather_at_place(f'{city},BR')
        return observation.get_weather()

    def getWeatherDescription(self, city: str) -> str:
        weather = self.getWeather(city)
        status = weather.get_detailed_status()
        return status.lower()

    def getTemperature(self, city: str) -> float:
        weather = self.getWeather(city)
        temp = weather.get_temperature(unit='celsius')
        return temp['temp']

    def getTempVariation(self, city: str) -> tuple:
        weather = self.getWeather(city)
        temp = weather.get_temperature(unit='celsius')
        return temp['temp_min'], temp['temp_max']

    def isRainy(self, city: str) -> bool:
        weather = self.getWeather(city)

        if weather.get_status().lower() == 'rain':
            return True
        else:
            volume = sum(weather.get_rain().items())
            return volume > 0
