"""
O bot propriamente
"""

from .weather import WeatherAPI, NotFoundError
from .parser import parser, WeatherTypes, FunctionalTypes, CouldNotUnderstandException, MoreThanFiveDaysException
from .alerts.notification import Notification
from .google_maps.geocode_functions import LocationNotFoundException, get_user_address_by_name
from .database.user_keys import UserStateKeys, UserDataKeys
from .database.userDAO import update, state, remove_key, name, email, subscribed_coords, last_update
from datetime import date as date_type


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
                 password=""):
        """Construído com tokens das APIs do Telegram e do OpenWeatherMap"""
        self.owm_api = WeatherAPI(open_weather_token)

        if password == "":
            self.password = False
        else:
            self.password = password

        self.dev_dict = {}

        super().__init__(telegram_token)

    def on_chat_message(self, msg):

        content_type, _, chat_id, _, message_id = telepot.glance(msg, long=True)
        # - long: (content_type, msg["chat"]["type"], msg["chat"]["id"], msg["date"], msg["message_id"])
        chat_id = str(chat_id)

        # apagar estados do usuário se ele ficou inativo por mais de 40 segundos
        if last_update(chat_id) and \
                datetime.now() - datetime.fromtimestamp(float(last_update(chat_id))) >= timedelta(seconds=40):
            remove_key(chat_id, UserDataKeys.STATE)

        # If the message is a text message
        if content_type == 'text':
            response = self.evaluate_text(msg["text"], chat_id, message_id)
            if isinstance(response, str):
                self.markdown_message(chat_id, response)

        elif content_type == 'location':
            self.evaluate_location(msg)

    def evaluate_text(self, text: str, chat_id: str, message_id: int):
        response = None

        try:
            qtype, location = parser.parse(chat_id, text)

            if not location:
                if qtype is FunctionalTypes.DEV_FUNCTIONS_ON:
                    self.delete_message((chat_id, message_id))

                    if self.password:
                        if chat_id in self.dev_dict and self.dev_dict[chat_id]["DEV"]:
                            return "*Você já é developer!*"
                        else:
                            result = devfunc.validate_password(text, self.password)
                            if result is True:
                                return devfunc.set_dev_user(self.dev_dict, chat_id)
                            return result

                    else:
                        return "*Modo developer não configurado*"

                elif qtype is FunctionalTypes.DEV_FUNCTIONS_OFF:
                    if self.password:
                        return devfunc.set_dev_user(self.dev_dict, chat_id, on=False)
                    else:
                        return "*Modo developer não configurado*"

                elif qtype is FunctionalTypes.DEV_COMMANDS:
                    if self.password:
                        return devfunc.list_developer_commands()
                    else:
                        return "*Modo developer não configurado*"

                elif qtype is FunctionalTypes.SET_SUBSCRIPTION or isinstance(qtype, UserStateKeys):
                    if qtype is UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE or \
                            qtype is UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE:
                        self.set_alert_location(chat_id, text)
                    else:
                        self.evaluate_subscription(chat_id, text)

                elif qtype is FunctionalTypes.INITIAL_MESSAGE:
                    #
                    self.start(chat_id)

                elif qtype is FunctionalTypes.HELP_REQUEST:
                    #
                    self.help(chat_id, text)

                elif qtype is FunctionalTypes.SET_ALARM:
                    Notification.set_notification_type(self, (chat_id, message_id))

            else:

                full_adress = location[0]
                coords = location[1]
                pairs = qtype

                self.markdown_message(chat_id, "*Certo, encontrei este endereço:*")
                self.markdown_message(chat_id, full_adress)

                for pair in pairs:
                    tag = pair[0]
                    tag_date = pair[1]

                    # todo incluir checagem se api openweather tá online

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

                    return response

        except MoreThanFiveDaysException as e:
            return f'{str(e)}'
        except AssertionError:
            return '*Infelizmente não reconheci o nome do local :(*'
        except CouldNotUnderstandException as e:
            return f'{str(e)}'
        except ValueError as e:
            return f'{str(e)}'
        except NotFoundError:
            return '*Infelizmente não reconheci o nome da cidade :(*'
        except LocationNotFoundException as e:
            return str(e)

    def evaluate_location(self, msg):

        chat_id, message_id = self.get_message_id(msg)
        coords = {"lat": msg["location"]["latitude"], "lng": msg["location"]["longitude"]}

        if state(chat_id) is UserStateKeys.SUBSCRIBING_PLACE:
            self.evaluate_subscription(chat_id, f'{coords["lat"]} {coords["lng"]}')

        elif state(chat_id) is UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE or \
                state(chat_id) is UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE:
            self.delete_message((chat_id, message_id))
            print("setou")
            self.set_alert_location(chat_id, coords)

        else:
            # forecast call
            pass

    def set_alert_location(self, chat_id, location):
        """
        :param chat_id: the chat_id talking to the bot
        :param location: the location sent, may be a dictionary with 'lat' and 'lng' keys or a string
        :return: None

        This method's ethos is to ensure that the user sends a valid location to the alerts subscribing system.

        """
        try:
            address, coords = get_user_address_by_name(location)
            update(chat_id, UserDataKeys.NOTIFICATION_COORDS, coords)
            self.markdown_message(chat_id, f"""
Certo, o local configurado para receber notificações é:
*{address}*
Envie *ok* para confirmar ou um uma outra localização para corrigir esta. 
""")
        except LocationNotFoundException:
            self.markdown_message(chat_id, "Insira um local válido")

    def on_callback_query(self, callback_query):
        query_id, from_id, query_data = telepot.glance(callback_query, flavor='callback_query')

        # Build message identification
        message_id = self.get_message_id(callback_query)
        chat_id = str(message_id[0])
        query_id = str(query_id)

        # Navigate the callback if it came from the notifications setter
        if query_data.split('.')[0] == 'notification':

            info = query_data.split('.')
            values = [0]
            if info[1] == 'type':

                if info[2] == 'daily':
                    update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE)
                    values = [1]

                elif info[2] == 'trigger':
                    update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE)
                    values = [2]

            elif info[1] == 'set':

                if info[2] == 'use_subscribed_place':
                    self.set_alert_location(chat_id, subscribed_coords(chat_id))

                elif info[2] == 'go_back':
                    remove_key(chat_id, UserDataKeys.STATE)
                    values = [5]

            options = {
                "1": "Notification.set_notification_location(self, message_id)",
                "2": "Notification.set_notification_location(self, message_id, by_trigger=True)",
                "3": "",
                "4": "",
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
            message_id = (msg["message"]["chat"]["id"], msg["message"]["message_id"])

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
        if not state(chat_id):
            update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_NAME)
            self.markdown_message(chat_id, '*Qual seu nome?*')

        elif state(chat_id) is UserStateKeys.SUBSCRIBING_NAME:
            update(chat_id, UserDataKeys.NAME, text)
            update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_EMAIL)
            self.markdown_message(chat_id, '*Qual seu e-mail?*')

        elif state(chat_id) is UserStateKeys.SUBSCRIBING_EMAIL:
            update(chat_id, UserDataKeys.EMAIL, text)
            update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_PLACE)
            self.markdown_message(chat_id, '*Qual o seu lugar de cadastro?*\n(Envie um nome ou uma localização')

        elif state(chat_id) is UserStateKeys.SUBSCRIBING_PLACE:
            address = None
            try:
                address, coords = get_user_address_by_name(text)
                update(chat_id, UserDataKeys.SUBSCRIBED_COORDS, coords)
            except LocationNotFoundException as e:
                remove_key(chat_id, UserDataKeys.SUBSCRIBED_COORDS)
                self.markdown_message(chat_id, f'*{str(e)}*')
            remove_key(chat_id, UserDataKeys.STATE)
            self.markdown_message(chat_id, f"""
*Parabéns!*
*Agora você possui funcionalidade especiais.*

Você inseriu as informações:
*Nome*: {name(chat_id)}
*Email*: {email(chat_id)}
*Localização*: {address or 'Local não informado'}

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
        return self.answerCallbackQuery(query_id, text=message, **kwargs)

    def delete_message(self, message_id):
        return self.deleteMessage(message_id)
