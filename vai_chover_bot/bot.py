from weather import WeatherAPI, NotFoundError
from parser import get_city

import telepot
from telepot.loop import MessageLoop


class Bot(telepot.Bot):
    def __init__(self, telegram_token: str, open_weather_token: str):
        self._weather_api = WeatherAPI(open_weather_token)
        return super().__init__(telegram_token)

    def sendWeather(self, chat_id, city: str):
        try:
            weather = self._weather_api.getWeather(city)
            self.sendMessage(chat_id, f'Aparentemente, está {weather} em {city}')
        except NotFoundError:
            self.sendMessage(chat_id, f'Não consegui achar a cidade \"{city}\"')

    def _genHandler(self):
        def handler(msg):
            content_type, _, chat_id = telepot.glance(msg)

            if content_type == 'text':
                text = msg['text']
                city = get_city(text)
                self.sendWeather(chat_id, city)

        return handler

    def run_forever(self, *args, **kwargs):
        MessageLoop(self, self._genHandler()).run_forever(*args, **kwargs)

    def run_as_thread(self, *args, **kwargs):
        MessageLoop(self, self._genHandler()).run_as_thread(*args, **kwargs)
