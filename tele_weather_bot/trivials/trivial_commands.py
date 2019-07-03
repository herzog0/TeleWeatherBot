from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from tele_weather_bot.communication.send_to_user import simple_message, markdown_message


def call_help(chat_id, text):

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
        simple_message(chat_id, 'ajuda pro 1')

    elif helptype == '2':
        simple_message(chat_id, 'ajuda pro 2')

    elif helptype == '3':
        simple_message(chat_id, 'ajuda pro 3')

    elif helptype == '4':
        simple_message(chat_id, 'ajuda pro 4')

    else:
        markdown_message(chat_id, main_help_message)

    # TODO escrever mensagens de ajuda para cada item especificado


def start(chat_id):
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
    simple_message(chat_id, initial_response_text, reply_markup=keyboard)
