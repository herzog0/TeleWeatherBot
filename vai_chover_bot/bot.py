"""
O bot propriamente
"""

from .weather import WeatherAPI, NotFoundError
from .parser import QuestionParser, QuestionType, CouldNotUnderstandException
from .handshake import Handshake

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


class WeatherBot(telepot.Bot):
    """Bot de previsão do tempo"""

    def __init__(self, telegram_token: str, open_weather_token: str):
        """Construído com tokens das APIs do Telegram e do OpenWeatherMap"""
        self._weather_api = WeatherAPI(open_weather_token)
        self._question_parser = QuestionParser()
        self.handshakeHandler = Handshake()
        self.subscriptionsState = {}

        super().__init__(telegram_token)


    def _getAnswer(self, question_type: QuestionType, city):
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

    def parse(self, text: str):
        """Parseia a pergunta e a resposta, cuidando com alguns casos de erro também"""
        try:
            type, args = self._question_parser.parse(text)
            return self._getAnswer(type, *args)

        except CouldNotUnderstandException:
            return 'Putz, não consegui entender o que disse'
        except NotFoundError:
            return 'Vixi, não conheço essa cidade'

    def firstMessage(self):
        message = """
            Olá!!
            Você está iniciando o TeleWeatherBot!! Bem vindo!!
            Use os seguintes comandos para me pedir algo:
                /help -> lista de comandos disponíveis
                /cadastro -> efetuar cadastro para poder aproveitar mais as funcionalidades
                /clima <Cidade> -> falar como está o clima da Cidade no momento
        """
        return message

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        self.answerCallbackQuery(query_id, text='Got it')

    def start(self, chat_id):
        initialResponseText = self.firstMessage()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Iniciar Cadastro', callback_data='cadastro')],
            [InlineKeyboardButton(text='Exibir comandos disponíveis', callback_data='comandos')]
        ])
        self.sendMessage(chat_id, initialResponseText, reply_markup=keyboard)

    def on_chat_message(self, msg):
        content_type, _, chat_id = telepot.glance(msg)
        if content_type == 'text':
            text = msg['text']
            if self.handshakeHandler.checkHandshakeStatus(chat_id) or text.strip().lower() in ['/cadastro']:
                #self.evaluateSubscription(chat_id, text)
                self.handshakeHandler.evaluateSubscription(self, chat_id, text)
            elif text.strip().lower() in ['/start']:
                self.start(chat_id)
            else:
                response = self.parse(text)
                if response:
                    self.sendMessage(chat_id, response)

    def run_forever(self, *args, **kwargs):
        """Roda o bot, bloqueando a thread"""
        # TODO: não usar MessageLoop, pq ele ignora o KeyboardInterrupt
        #MessageLoop(self, self._genHandler()).run_forever(*args, **kwargs)
        MessageLoop(self, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query }).run_forever(*args, **kwargs)

    # def run_as_thread(self, *args, **kwargs):
    #     """Roda o bot em outra thread"""
    #     # TODO: também mudar aqui
    #     MessageLoop(self, self._genHandler()).run_as_thread(*args, **kwargs)
