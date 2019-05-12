from ..database import UserDAO, User
from ..database.user_keys import UserStateKeys, UserDataKeys


class Handshake:

    def __init__(self, bot):
        self.repo = UserDAO()
        self.bot = None

    def evaluate_subscription(self, chat_id, text):
        chat_id = str(chat_id)
        if not self.bot.users_dict[chat_id][UserStateKeys.SUBSCRIBING]:
            self.initiate_subscription(chat_id)
            self.bot.markdown_message(chat_id, '*Qual seu nome?*')
            return
        state = self.bot.users_dict[chat_id][UserStateKeys.SUBSCRIBING]

        if state == UserStateKeys.SUBSCRIBING_NAME:
            self.subscribe_name(chat_id, text)
            self.bot.markdown_message(chat_id, '*Qual seu e-mail?*')

        elif state == UserStateKeys.SUBSCRIBING_EMAIL:
            self.subscribe_email(chat_id, text)
            self.bot.markdown_message(chat_id, '*Qual o seu lugar de cadastro?*\n(Envie um nome ou uma localização')
            self.bot.update_user_dict(chat_id, subscribing=True)

        elif state == UserStateKeys.SUBSCRIBING_PLACE:
            self.subscribe_place(chat_id, text)
            self.bot.markdown_message(chat_id, 'Obrigado por se cadastrar!! Aproveite nossas funcionalidades!!')

    def initiate_subscription(self, chat_id):
        self.bot.users_dict[chat_id][UserStateKeys.SUBSCRIBING] = UserStateKeys.SUBSCRIBING_NAME

        self.bot.users_dict[chat_id][UserDataKeys.CHAT_ID] = chat_id

    def subscribe_name(self, chat_id, name):
        self.bot.users_dict[chat_id][UserStateKeys.SUBSCRIBING] = UserStateKeys.SUBSCRIBING_EMAIL
        self.bot.users_dict[chat_id][UserDataKeys.NAME] = name

    def subscribe_email(self, chat_id, email):
        self.bot.users_dict[chat_id][UserStateKeys.SUBSCRIBING] = UserStateKeys.SUBSCRIBING_PLACE
        self.bot.users_dict[chat_id][UserDataKeys.EMAIL] = email

    def subscribe_place(self, chat_id, place):
        self.bot.users_dict[chat_id][UserStateKeys.SUBSCRIBING] = None
        self.bot.users_dict[chat_id][UserDataKeys.PLACE] = place
        self.repo.write(User.from_dict(self.bot.users_dict[chat_id]))
        # deletar de self.userDicts
