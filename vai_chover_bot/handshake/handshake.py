
from ..database import UserDAO

class Handshake:

    def __init__(self):
        self.subscriptionsState = {}

    def evaluateSubscription(self, currentBot, chat_id, text):
        if not chat_id in self.subscriptionsState:
            self.subscriptionsState[chat_id] = 'nome'
            currentBot.sendMessage(chat_id, 'Qual seu nome?')
            return
        state = self.subscriptionsState[chat_id]
        if state == 'nome':
            self.cadastrarNome(text)
            self.subscriptionsState[chat_id] = 'localidade'
            currentBot.sendMessage(chat_id, 'Qual sua atual localidade?')
        elif state == 'localidade':
            self.cadastrarLocalidade(text)
            del self.subscriptionsState[chat_id]
            currentBot.sendMessage(chat_id, 'Obrigado por se cadastrar!! Aproveite nossas funcionalidades!!')

    def checkHandshakeStatus(self, chat_id):
        return chat_id in self.subscriptionsState

    def cadastrarNome(self, chat_id):
        return None

    def cadastrarLocalidade(self, chat_id):
        return None
