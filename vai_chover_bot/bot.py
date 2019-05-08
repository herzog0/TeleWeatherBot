"""
O bot propriamente
"""

from .weather import WeatherAPI, NotFoundError
from .parser import parser, QuestionType, CouldNotUnderstandException
from .handshake import Handshake
from .alerts.notification import Notification

from pyowm import OWM
from pyowm.utils import geo
from pyowm.alertapi30.enums import WeatherParametersEnum, OperatorsEnum, AlertChannelsEnum
from pyowm.alertapi30.condition import Condition

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import datetime, timedelta
import vai_chover_bot.dev_functions as devfunc


class WeatherBot(telepot.Bot):
    """Bot de previsão do tempo"""

    def __init__(self, telegram_token: str, open_weather_token: str, password=""):
        """Construído com tokens das APIs do Telegram e do OpenWeatherMap"""
        self._weather_api = WeatherAPI(open_weather_token)
        self.handshakeHandler = Handshake()
        self.subscriptionsState = {}
        if password == "":
            self.password = False
        else:
            self.password = password

        self.delta_counter = datetime.now()

        # Dicionário contendo os dicionários de cada usuário
        self.user_dict = {'SETTING_NOTIFICATION': False, 'FORECAST': False, 'SUBSCRIBING': False, 'msg_time_delta': ""}
        
        self.users_dict = {}

        self.dev_dict = {}

        super().__init__(telegram_token)

    def update_user_dict(self, chat_id, setting_notification=False, forecast=False, subscribing=False,
                         only_delta_time_update=True):
        if chat_id not in self.users_dict:
            self.users_dict[chat_id] = self.user_dict
            self.users_dict[chat_id]['msg_time_delta'] = datetime.now()

        if not only_delta_time_update:
            self.users_dict[chat_id]['SETTING_NOTIFICATION'] = setting_notification
            self.users_dict[chat_id]['FORECAST'] = forecast
            self.users_dict[chat_id]['SUBSCRIBING'] = subscribing
        self.users_dict[chat_id]['msg_time_delta'] = datetime.now() - self.users_dict[chat_id]['msg_time_delta']

    def update_database(self):
        pass

    def get_user_state(self, chat_id, key=""):
        assert self.users_dict[chat_id][key] is bool
        return self.users_dict[chat_id][key]

    def on_chat_message(self, msg):

        content_type, _, chat_id = telepot.glance(msg)

        # If the message is a text message
        if content_type == 'text':
            self.evaluate_text(msg)

        elif content_type == 'location':
            self.evaluate_location(msg)

    def evaluate_text(self, msg):
        content_type, _, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
        text = msg['text']
        response = None

        try:
            qtype, city = parser.parse(text)
            city = city[0]

            if qtype is QuestionType.DEV_FUNCTIONS_ON:
                if self.password:
                    if chat_id in self.dev_dict and self.dev_dict[chat_id]['DEV']:
                        self.markdown_message(chat_id, "*Você já é developer!*")
                    elif devfunc.validate_password(self, msg):
                        devfunc.set_dev_user(self, msg)
                else:
                    self.markdown_message(chat_id, "*Modo developer não configurado*")

            elif qtype is QuestionType.DEV_FUNCTIONS_OFF:
                if self.password:
                    devfunc.set_dev_user(self, msg, on=False)
                else:
                    self.markdown_message(chat_id, "*Modo developer não configurado*")

            elif qtype is QuestionType.DEV_COMMANDS:
                if self.password:
                    devfunc.list_developer_commands(self, msg)
                else:
                    self.markdown_message(chat_id, "*Modo developer não configurado*")

            elif qtype is QuestionType.SET_SUBSCRIPTION \
                    or self.handshakeHandler.checkHandshakeStatus(chat_id):
                #
                self.handshakeHandler.evaluateSubscription(self, chat_id, text)

            elif qtype is QuestionType.INITIAL_MESSAGE:
                self.update_user_dict(chat_id)
                self.start(chat_id)

            elif qtype is QuestionType.HELP_REQUEST:
                #
                self.help(chat_id, text)

            elif qtype is QuestionType.SET_ALARM:
                message_id = self.get_message_id(msg)
                Notification.set_notification_type(self, message_id)

            elif qtype is QuestionType.WEATHER:
                weather = self._weather_api.getWeatherDescription(city)
                response = f'Parece estar {weather} em {city}'

            elif qtype is QuestionType.IS_RAINY:
                rainy = self._weather_api.isRainy(city)
                response = f'Tá chovendo em {city} {"sim" if rainy else "não"}'

            elif qtype is QuestionType.TEMPERATURE:
                temp = self._weather_api.getTemperature(city)
                response = f'Acho que tá {temp:.1f}°C  lá em {city}'

            elif qtype is QuestionType.TEMP_VARIATION:
                t_min, t_max = self._weather_api.getTempVariation(city)
                if t_min != t_max:
                    response = f'Aqui diz: mínima de {t_min:.1f}°C e máxima de {t_max:.1f}°C'
                else:
                    response = f'Nem sei, mas deve ficar perto de {t_max:.1f}°C'

            if response:
                self.simple_message(chat_id, response)

        except CouldNotUnderstandException:
            self.markdown_message(chat_id, '*Desculpe, mas não entendi*')
        except NotFoundError:
            self.markdown_message(chat_id, '*Infelizmente não reconheci o nome da cidade :(*')

    def evaluate_location(self, msg):

        chat_id, message_id = self.get_message_id(msg)

        if self.get_user_state(chat_id, key="SETTING_NOTIFICATION"):

            pass

        elif self.get_user_state(chat_id, key="SUBSCRIBING"):
            pass

        else:
            # forecast call
            pass

    @staticmethod
    def get_message_id(msg):
        try:
            message_id = telepot.message_identifier(msg)
        except ValueError:
            message_id = (msg['message']['chat']['id'], msg['message']['message_id'])

        return message_id

    def help(self, chat_id, text):

        args = text.lower().strip().split()

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

        if args and len(args) > 1 and ('ajuda' in args or 'help' in args):
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

    def on_callback_query(self, callback_query):
        query_id, from_id, query_data = telepot.glance(callback_query, flavor='callback_query')

        # Build message identification
        message_id = self.get_message_id(callback_query)

        # Navigate the callback if it came from the notifications setter
        if query_data.split('.')[0] == 'notification':

            info = query_data.split('.')
            values = [0]
            if info[1] == 'type':

                if info[2] == 'daily':
                    values = [1]

                elif info[2] == 'trigger':
                    values = [2]

            elif info[1] == 'set':

                if info[2] == 'location':
                    self.update_user_dict(message_id[0], setting_notification=True)
                    values = [3]

                elif info[2] == 'city':
                    self.update_user_dict(message_id[0], setting_notification=True)
                    values = [4]

                elif info[2] == 'go_back':
                    self.update_user_dict(message_id[0])
                    values = [5]

            elif info[1] == 'get':

                if info[2] == 'cancel':
                    self.update_user_dict(message_id[0])
                    if info[3] == 'by_location':
                        values = [1]

            options = {
                "1": "Notification.set_daily_notification(self, message_id)",
                "2": "",
                "3": "Notification.set_daily_notification_by_location(self, message_id)",
                "4": "Notification.set_daily_notification_by_city(self, message_id)",
                "5": "Notification.set_notification_type(self, message_id, query_id)",
            }

            for value in values:
                eval(options.get(str(value), "None"))

    def simple_message(self, chat_id, message, **kwargs):
        return self.sendMessage(chat_id, message, **kwargs)

    def markdown_message(self, chat_id, message, **kwargs):
        return self.simple_message(chat_id, message, parse_mode="Markdown", **kwargs)

    def html_message(self, chat_id, message, **kwargs):
        return self.simple_message(chat_id, message, parse_mode="HTML", **kwargs)

    def inline_keyboard_message(self, chat_id, message, keyboard=None, **kwargs):
        return self.simple_message(chat_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)

    def edit_message(self, message_id, message, keyboard=None, **kwargs):
        return self.editMessageText(message_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)

    def answer_callback_query(self, query_id, message='', **kwargs):
        return self.answerCallbackQuery(query_id, message, **kwargs)

    def delete_message(self, message_id):
        return self.deleteMessage(message_id)
