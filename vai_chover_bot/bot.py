from .weather import WeatherAPI, NotFoundError
from .parser import QuestionParser, QuestionType, NotUnderstandable

import telepot
from telepot.loop import MessageLoop


class Bot(telepot.Bot):
    def __init__(self, telegram_token: str, open_weather_token: str):
        self._weather_api = WeatherAPI(open_weather_token)
        self._question_parser = QuestionParser()

        return super().__init__(telegram_token)


    def _getWeather(self, city: str) -> str:
        weather = self._weather_api.getWeather(city)
        return f'Parece estar {weather} em {city}'

    def _getAnswer(self, question_type: QuestionType, *args) -> str:
        if question_type is QuestionType.WEATHER:
            return self._getWeather(*args)
        else:
            raise NotUnderstandable

    def parse(self, text: str) -> str:
        try:
            type, args = self._question_parser.parse(text)
            return self._getAnswer(type, *args)

        except NotUnderstandable:
            return 'Desculpe, não consegui entender o que disse'
        except NotFoundError:
            return 'Desculpe, não conheço essa cidade'



    def _genHandler(self) -> callable:
        def handler(msg):
            content_type, _, chat_id = telepot.glance(msg)

            if content_type == 'text':
                response = self.parse(msg['text'])
                self.sendMessage(chat_id, response)

        return handler

    def run_forever(self, *args, **kwargs):
        MessageLoop(self, self._genHandler()).run_forever(*args, **kwargs)

    def run_as_thread(self, *args, **kwargs):
        MessageLoop(self, self._genHandler()).run_as_thread(*args, **kwargs)
