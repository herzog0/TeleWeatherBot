"""
O bot propriamente
"""

from .weather import WeatherAPI, NotFoundError
from .parser import QuestionParser, QuestionType, CouldNotUnderstandException

import telepot
from telepot.loop import MessageLoop


class WeatherBot(telepot.Bot):
    """Bot de previsão do tempo"""

    def __init__(self, telegram_token: str, open_weather_token: str):
        """Construído com tokens das APIs do Telegram e do OpenWeatherMap"""
        self._weather_api = WeatherAPI(open_weather_token)
        self._question_parser = QuestionParser()

        return super().__init__(telegram_token)


    def _getAnswer(self, question_type: QuestionType, city) -> str:
        """Busca uma descrição do tempo em uma cidade pela API do OWM e coloca em uma string"""

        # testa os tipos de questão já adicionados
        if question_type is QuestionType.WEATHER:
            weather = self._weather_api.getWeatherDescription(city)
            return f'Parece estar {weather} em {city}'

        elif question_type is QuestionType.IS_RAINY:
            rainy = self._weather_api.isRainy(city)
            return f'Tá chovendo em {city} {"sim" if rainy else "não"}'

        elif question_type is QuestionType.TEMPERATURE:
            temp = self._weather_api.getTemperature(city)
            return f'Acho que tá {temp:.1f}°C  lá em {city}'

        elif question_type is QuestionType.TEMP_VARIATION:
            t_min, t_max = self._weather_api.getTempVariation(city)
            if t_min != t_max:
                return f'Aqui diz: mínima de {t_min:.1f}°C e máxima de {t_max:.1f}°C'
            else:
                return f'Nem sei, mas deve ficar perto de {t_max:.1f}°C'

        # caso base, questão desconhecida/desentendida
        raise CouldNotUnderstandException

    def parse(self, text: str) -> str:
        """Parseia a pergunta e a resposta, cuidando com alguns casos de erro também"""
        try:
            type, args = self._question_parser.parse(text)
            return self._getAnswer(type, *args)

        except CouldNotUnderstandException:
            return 'Putz, não consegui entender o que disse'
        except NotFoundError:
            return 'Vixi, não conheço essa cidade'



    def _genHandler(self) -> callable:
        """Gerador das callbacks para tratar as mensagens do bot"""
        def callback(msg):
            content_type, _, chat_id = telepot.glance(msg)

            if content_type == 'text':
                text = msg['text']
                response = self.parse(text)
                self.sendMessage(chat_id, response)

        return callback

    def run_forever(self, *args, **kwargs):
        """Roda o bot, bloqueando a thread"""
        # TODO: não usar MessageLoop, pq ele ignora o KeyboardInterrupt
        MessageLoop(self, self._genHandler()).run_forever(*args, **kwargs)

    def run_as_thread(self, *args, **kwargs):
        """Roda o bot em outra thread"""
        # TODO: também mudar aqui
        MessageLoop(self, self._genHandler()).run_as_thread(*args, **kwargs)
