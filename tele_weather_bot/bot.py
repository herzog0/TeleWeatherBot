"""
O bot propriamente
"""

from .weather import WeatherAPI, NotFoundError
from .parser import parser, WeatherTypes, FunctionalTypes, CouldNotUnderstandException, MoreThanFiveDaysException
from .alerts.notification import Notification
from .google_maps.geocode_functions import GoogleGeoCode, LocationNotFoundException
from .database.user_keys import UserStateKeys, UserDataKeys
from .database.user import User
from .database.userDAO import UserDAO
from .parser.parser import address
from datetime import date as date_type

from pyowm import OWM
from pyowm.utils import geo
from pyowm.alertapi30.enums import WeatherParametersEnum, OperatorsEnum, AlertChannelsEnum
from pyowm.alertapi30.condition import Condition

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import datetime, timedelta
import tele_weather_bot.dev_functions as devfunc


class WeatherBot(telepot.Bot):
    """Bot de previsão do tempo"""

    def __init__(self,
                 telegram_token: str,
                 open_weather_token: str,
                 google_maps_token: str,
                 firebase_certificate: dict,
                 password=""):
        """Construído com tokens das APIs do Telegram e do OpenWeatherMap"""
        self.owm_api = WeatherAPI(open_weather_token)
        self.gmaps = GoogleGeoCode(google_maps_token)
        self.repo = UserDAO(firebase_certificate)

        if password == "":
            self.password = False
        else:
            self.password = password

        self.users = {}        

        self.dev_dict = {}

        super().__init__(telegram_token)

    def update_database(self):
        pass

    def on_chat_message(self, msg):

        content_type, _, chat_id = telepot.glance(msg)

        if chat_id not in self.users:
            self.users[chat_id] = User(chat_id)
        else:
            self.users[chat_id].update_user()

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
            qtype, location = parser.parse(self, chat_id, text)

            if not location:
                if qtype is FunctionalTypes.DEV_FUNCTIONS_ON:
                    if self.password:
                        if chat_id in self.dev_dict and self.dev_dict[chat_id]['DEV']:
                            self.markdown_message(chat_id, "*Você já é developer!*")
                        elif devfunc.validate_password(self, msg):
                            devfunc.set_dev_user(self, msg)
                    else:
                        self.markdown_message(chat_id, "*Modo developer não configurado*")

                elif qtype is FunctionalTypes.DEV_FUNCTIONS_OFF:
                    if self.password:
                        devfunc.set_dev_user(self, msg, on=False)
                    else:
                        self.markdown_message(chat_id, "*Modo developer não configurado*")

                elif qtype is FunctionalTypes.DEV_COMMANDS:
                    if self.password:
                        devfunc.list_developer_commands(self, msg)
                    else:
                        self.markdown_message(chat_id, "*Modo developer não configurado*")

                elif qtype is FunctionalTypes.SET_SUBSCRIPTION or isinstance(qtype, UserStateKeys):
                    #
                    self.evaluate_subscription(chat_id, text)

                elif qtype is FunctionalTypes.INITIAL_MESSAGE:
                    self.start(chat_id)

                elif qtype is FunctionalTypes.HELP_REQUEST:
                    #
                    self.help(chat_id, text)

                elif qtype is FunctionalTypes.SET_ALARM:
                    message_id = self.get_message_id(msg)
                    Notification.set_notification_type(self, message_id)

            else:

                full_adress = location[0]
                coords = location[1]
                pairs = qtype
                
                self.markdown_message(chat_id, "*Certo, encontrei este endereço:*")
                self.markdown_message(chat_id, full_adress)

                for pair in pairs:
                    tag = pair[0]
                    tag_date = pair[1]

                    if tag is WeatherTypes.WEATHER:
                        weather = self.owm_api.get_weather_description(coords, tag_date)
                        temp = self.owm_api.get_temperature(coords, tag_date)

                        response = f'{self.date_string(tag_date)}' \
                            f'{weather.capitalize()}\n' \
                            f'Temperatura atual: {temp:.1f}°C' \

                    elif tag is WeatherTypes.TEMPERATURE:
                        temp = self.owm_api.get_temperature(coords, tag_date)
                        t_min, t_max = self.owm_api.get_temp_variation(coords, tag_date)
                        if t_min != t_max:
                            response = f'{self.date_string(tag_date)}' \
                                f'Temperatura mínima: {t_min:.1f}°C\n' \
                                f'Temperatura máxima: {t_max:.1f}°C\n' \
                                f'Temperatura atual: {temp:.1f}°C'
                        else:
                            response = f'Temperatura em torno de {t_max:.1f}°C'

                    elif tag is WeatherTypes.HUMIDITY:
                        self.markdown_message(chat_id, "eh humidade")

                    elif tag is WeatherTypes.IS_RAINY:
                        rainy = self.owm_api.is_rainy(coords, tag_date)
                        response = f'{"Está" if rainy else "Não está"} chovendo lá.'

                    elif tag is WeatherTypes.IS_SUNNY:
                        self.markdown_message(chat_id, "eh sol")

                    elif tag is WeatherTypes.IS_CLOUDY:
                        self.markdown_message(chat_id, "eh nuvem")

                    if response:
                        self.markdown_message(chat_id, response)

        except MoreThanFiveDaysException as e:
            self.markdown_message(chat_id, f'{str(e)}')
        except AssertionError:
            self.markdown_message(chat_id, '*Infelizmente não reconheci o nome do local :(*')
        except CouldNotUnderstandException as e:
            self.markdown_message(chat_id, f'{str(e)}')
        except ValueError as e:
            self.markdown_message(chat_id, f'{str(e)}')
        except NotFoundError:
            self.markdown_message(chat_id, '*Infelizmente não reconheci o nome da cidade :(*')
        except LocationNotFoundException as e:
            self.markdown_message(chat_id, str(e))

    def evaluate_location(self, msg):

        chat_id, message_id = self.get_message_id(msg)
        coords = {'lat': msg['location']['latitude'], 'lng': msg['location']['longitude']}

        if self.users[chat_id].state() is UserStateKeys.SUBSCRIBING_PLACE:
            self.evaluate_subscription(chat_id, f'{coords["lat"]} {coords["lng"]}')

        elif self.users[chat_id].state() is UserStateKeys.SUBSCRIBING_ALERT:
            
            pass

        else:
            # forecast call
            pass

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
                    self.users[message_id[0]].update_user(subscribing_alert=True)
                    values = [3]

                elif info[2] == 'place_name':
                    self.users[message_id[0]].update_user(subscribing_alert=True)
                    values = [4]

                elif info[2] == 'go_back':
                    # todo self.update_user(message_id[0])
                    values = [5]

            elif info[1] == 'get':

                if info[2] == 'cancel':
                    # todo self.update_user(message_id[0])
                    if info[3] == 'by_location':
                        values = [1]
                    elif info[3] == 'by_place_name':
                        values = [1]

            options = {
                "1": "Notification.set_daily_notification(self, message_id)",
                "2": "",
                "3": "Notification.set_daily_notification_by_location(self, message_id)",
                "4": "Notification.set_daily_notification_by_place_name(self, message_id)",
                "5": "Notification.set_notification_type(self, message_id, query_id)",
            }

            for value in values:
                eval(options.get(str(value), "None"))

    @staticmethod
    def date_string(date: date_type, time_set: datetime.hour = None):
        if time_set:
            return str(f'{date.day}/{date.month}/{date.year} às {time_set}'
                       f'\n*----------------------*\n')
        else:
            return str(f'{date.day}/{date.month}/{date.year}'
                       f'\n*----------------------*\n')

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
    
    def evaluate_subscription(self, chat_id, text):
        chat_id = chat_id
        if not self.users[chat_id].state():
            self.users[chat_id].update_user(subscribing_name=True)
            self.markdown_message(chat_id, '*Qual seu nome?*')

        elif self.users[chat_id].state() is UserStateKeys.SUBSCRIBING_NAME:
            self.users[chat_id].update_user(name=text, subscribing_email=True)
            self.markdown_message(chat_id, '*Qual seu e-mail?*')

        elif self.users[chat_id].state() is UserStateKeys.SUBSCRIBING_EMAIL:
            self.users[chat_id].update_user(email=text, subscribing_place=True)
            self.markdown_message(chat_id, '*Qual o seu lugar de cadastro?*\n(Envie um nome ou uma localização')

        elif self.users[chat_id].state() is UserStateKeys.SUBSCRIBING_PLACE:
            adress, coords = None, None
            try:
                adress, coords = self.gmaps.get_user_address_by_name(text)
            except LocationNotFoundException as e:
                self.markdown_message(chat_id, f'*{str(e)}*')
            self.users[chat_id].update_user(place={'adress': adress, 'coords': coords}, subscribed=True)
            self.users[chat_id].subscribed = True
            self.repo.write(self.users[chat_id])
            self.markdown_message(chat_id, f"""
*Parabéns!*
*Agora você possui funcionalidade especiais.*

Você inseriu as informações:
*Nome*: {self.users[chat_id].name}
*Email*: {self.users[chat_id].email}
*Localização*: {self.users[chat_id].place['adress'] or 'Local não informado'}

Caso queira alterar os dados basta recomeçar o cadastro.
Digite "*ajuda cadastro*" para obter mais informações sobre as funcionalidades especiais.

""")
    
    def run_forever(self, *args, **kwargs):
        """Roda o bot, bloqueando a thread"""

        # não usar MessageLoop, pq ele ignora o KeyboardInterrupt

        # MessageLoop(self, self._genHandler()).run_forever(*args, **kwargs)

        MessageLoop(self, {
            'chat': self.on_chat_message,
            'callback_query': self.on_callback_query
        }
                    ).run_forever(*args, **kwargs)

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
