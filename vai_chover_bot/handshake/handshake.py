from ..database import UserDAO, User

class Handshake:

    def __init__(self):
        self.subscriptionsState = {} # dicinario que controla o estado do cadastro para cada chat_id (usuario)
        self.userDicts = [] # vetor para guardar os diversos dicionarios de usuarios que estao sendo criados
        self.repo = UserDAO()

    def evaluateSubscription(self, currentBot, chat_id, text):
        if not chat_id in self.subscriptionsState:
            self.initiateSubscription(chat_id)
            currentBot.sendMessage(chat_id, 'Qual seu nome?')
            return
        state = self.subscriptionsState[chat_id]
        if state == 'nome':
            self.cadastrarNome(chat_id, text)
            currentBot.sendMessage(chat_id, 'Qual seu e-mail?')
        elif state == 'email':
            self.cadastrarEmail(chat_id, text)
            currentBot.sendMessage(chat_id, 'Qual a sua cidade?')
        elif state == 'cidade':
            self.cadastrarCidade(chat_id, text)
            currentBot.sendMessage(chat_id, 'Obrigado por se cadastrar!! Aproveite nossas funcionalidades!!')

    def initiateSubscription(self, chat_id):
        self.subscriptionsState[chat_id] = 'nome'
        self.userDicts.append({'id':chat_id})

    def checkHandshakeStatus(self, chat_id):
        return chat_id in self.subscriptionsState

    def cadastrarNome(self, chat_id, name):
        self.subscriptionsState[chat_id] = 'email'
        list(filter(lambda i: i['id'] == chat_id, self.userDicts))[0]['name'] = name

    def cadastrarEmail(self, chat_id, email):
        self.subscriptionsState[chat_id] = 'cidade'
        list(filter(lambda i: i['id'] == chat_id, self.userDicts))[0]['email'] = email

    def cadastrarCidade(self, chat_id, cidade):
        del self.subscriptionsState[chat_id]
        list(filter(lambda i: i['id'] == chat_id, self.userDicts))[0]['city'] = cidade
        self.repo.write(User.from_dict(list(filter(lambda i: i['id'] == chat_id, self.userDicts))[0]))
        ## deletar de self.userDicts



