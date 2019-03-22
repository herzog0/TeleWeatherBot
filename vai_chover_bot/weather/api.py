from pyowm import OWM


class WeatherAPI:
    def __init__(self, owm_api_key: str):
        self._owm = OWM(owm_api_key, config_module='weather.configuration')

    def getWeather(self, city: str):
        observation = self._owm.weather_at_place(f'{city},BR')
        weather = observation.get_weather()
        status = weather.get_status()

        return status.lower()
