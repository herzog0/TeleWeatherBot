"""
O bot propriamente
"""

from .weather import WeatherAPI, NotFoundError
from .parser import QuestionParser, QuestionType, CouldNotUnderstandException
from .handshake import Handshake
from .alerts.notification import Notification

from pyowm import OWM
from pyowm.utils import geo
from pyowm.alertapi30.enums import WeatherParametersEnum, OperatorsEnum, AlertChannelsEnum
from pyowm.alertapi30.condition import Condition

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

    def _get_answer(self, question_type: QuestionType, city):

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

        elif question_type is QuestionType.SET_ALARM:
            return QuestionType.SET_ALARM

        # caso base, questão desconhecida/desentendida
        raise CouldNotUnderstandException

    def parse(self, text: str):
        """Parseia a pergunta e a resposta, cuidando com alguns casos de erro também"""
        try:
            qtype, args = self._question_parser.parse(text)
            return self._get_answer(qtype, *args)

        except CouldNotUnderstandException:
            return 'Putz, não consegui entender o que disse'
        except NotFoundError:
            return 'Vixi, não conheço essa cidade'

    def on_chat_message(self, msg):

        content_type, _, chat_id = telepot.glance(msg)

        # If the message is a text message
        if content_type == 'text':

            # Get its text
            text = msg['text']

            # TODO melhorar a função parse() pra tratar inclusive os casos abaixo.
            #  Cadastro, start e help deveriam ser tipos de pergunta também

            if self.handshakeHandler.check_handshake_status(chat_id) \
                    or text.strip().lower() in ['/cadastro', 'cadastro', 'cadastrar']:
                self.handshakeHandler.evaluate_subscription(self, chat_id, text)

            elif text.strip().lower() in ['/start', 'start', 'começar', 'comecar', 'inicio', 'início', 'oi', 'ola']:
                self.start(chat_id)

            elif text.strip().lower().split()[0] in ['/help', 'help', '/ajuda', 'ajuda', 'socorro']:
                textsplit = text.strip().lower().split()
                self.help(chat_id, textsplit)

            else:
                response = self.parse(text)
                if response:
                    if response is QuestionType.SET_ALARM:
                        Notification.set_notification_type(self, chat_id)
                    else:
                        self.simple_message(chat_id, response)

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        # self.simple_message(from_id, "asdfg")

        if query_data == 'daily':
            self.simple_message(from_id, message="eita deu certo")

        # self.answer_callback_query(query_id, message='got ittt')

    def help(self, chat_id, args):
        main_help_message = u"""
Olá, você está usando o bot TeleWeather!
Usando dados abertos da API do OpenWeather, este bot te dá funcionalidades climáticas como:
*1 - Previsão do tempo*
*2 - Inscrição para notificações programadas*
*3 - Ajuda doméstica ao informar se sua roupa pode ser lavada e quando está seca*
*4 - Informações climáticas diversas*
        
Para saber mais sobre alguma funcionalidade peça ajuda!
ex.: *ajuda 1* (isso dará ajuda sobre a previsão do tempo, pois é o item 1)
ou   *help previsao* (o mesmo que "ajuda 1")
    """

        helptype = None

        if args and len(args) > 1 and ('ajuda' or 'help') in args:
            for arg in args:
                if arg in ['1', 1, 'previsão', 'previsao', 'tempo', 'prever']:
                    helptype = '1'
                elif arg in ['2', 2, 'inscrição', 'inscricao', 'inscriçao', 'inscricão', 'inscrever', 'notificar',
                             'notificação']:
                    helptype = '2'
                elif arg in ['3', 3, 'roupa', 'lavar']:
                    helptype = '3'
                elif arg in ['4', 4, 'informações', 'informaçoes', 'informacões', 'informacoes', 'info', 'infos']:
                    helptype = '4'

        if helptype == '1':
            self.simple_message(chat_id, 'ajuda pro 1')

        elif helptype == '2':
            self.simple_message(chat_id, 'ajuda pro 2')

        elif helptype == '3':
            self.simple_message(chat_id, 'ajuda pro 3')

        elif helptype == '4':
            self.simple_message(chat_id, 'ajuda pro 4')

        else:
            self.markdown_message(chat_id, main_help_message)

        # TODO escrever mensagens de ajuda para cada item especificado

    def start(self, chat_id):
        initial_response_text = """
        Olá!!
        Você está iniciando o TeleWeatherBot!! Bem vindo!!
        Use os seguintes comandos para me pedir algo:
        /help - Lista de comandos disponíveis
        /cadastro - Efetuar cadastro para poder aproveitar mais as funcionalidades
        /clima <Cidade> - Falar como está o clima da Cidade no momento
        """

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Iniciar Cadastro', callback_data='cadastro')],
            [InlineKeyboardButton(text='Exibir comandos disponíveis', callback_data='comandos')]
        ])
        self.simple_message(chat_id, initial_response_text, reply_markup=keyboard)

    def run_forever(self, *args, **kwargs):
        """Roda o bot, bloqueando a thread"""
        # TODO: não usar MessageLoop, pq ele ignora o KeyboardInterrupt

        # MessageLoop(self, self._genHandler()).run_forever(*args, **kwargs)

        MessageLoop(self, {
            'chat': self.on_chat_message,
            'callback_query': self.on_callback_query
        }
                    ).run_forever(*args, **kwargs)

    # def run_as_thread(self, *args, **kwargs):
    #     """Roda o bot em outra thread"""
    #     # TODO: também mudar aqui
    #     MessageLoop(self, self._genHandler()).run_as_thread(*args, **kwargs)
    
    def simple_message(self, chat_id, message, **kwargs):
        self.sendMessage(chat_id, message, **kwargs)

    def markdown_message(self, chat_id, message, **kwargs):
        self.simple_message(chat_id, message, parse_mode="Markdown", **kwargs)

    def html_message(self, chat_id, message, **kwargs):
        self.simple_message(chat_id, message, parse_mode="HTML", **kwargs)

    def inline_keyboard_message(self, chat_id, message, keyboard=None, **kwargs):
        self.simple_message(chat_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)

    def edit_message(self, message_id, message, keyboard=None, **kwargs):
        self.editMessageText(message_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)

    def answer_callback_query(self, query_id, message='', **kwargs):
        self.answerCallbackQuery(query_id, message, **kwargs)
