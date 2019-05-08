"""
O parser propriamente
"""

from .question import QuestionType, CouldNotUnderstandException
import string


def address(bot, words):
    location = ' '.join(words)

    full_address, coordinates = bot.gmaps.get_user_address_by_name(location)

    return full_address, coordinates


"""Parser das entradas dos usuários"""

# TODO: usar estado interno, talvez com o NLTK


def parse(bot, text: str) -> tuple:
    """Tentar ler a questão do usuário e decidir seu tipo e o que precisa para respondê-lo"""

    # TODO MELHORAR O ENTENDIMENTO DE PERGUNTAS SOBRE O CLIMA

    words = text.lower().strip().split()

    if words[0] in ['/set_dev_functions_on']:
        return QuestionType.DEV_FUNCTIONS_ON, None

    elif words[0] in ['/set_dev_functions_off']:
        return QuestionType.DEV_FUNCTIONS_OFF, None

    elif words[0] in ['/devhelp']:
        return QuestionType.DEV_COMMANDS, None

    elif words[0] in ['/cadastro', 'cadastro', 'cadastrar']:
        return QuestionType.SET_SUBSCRIPTION, None

    elif words[0] in ['/start', 'start', 'começar', 'comecar', 'inicio', 'início', 'oi', 'ola']:
        return QuestionType.INITIAL_MESSAGE, None

    elif words[0] in ['/help', 'help', '/ajuda', 'ajuda', 'socorro']:
        return QuestionType.HELP_REQUEST, None

    for word in words:
        if word in ('alarme', 'alerta', 'aviso', 'avise'):
            return QuestionType.SET_ALARM, None

    # como está [CIDADE](?)
    # descriçao do tempo
    if words[:2] == ['como', 'está']:
        return QuestionType.WEATHER, address(bot, words[2:])

    # está chuvendo em [CIDADE](?)
    # teste de chuva
    elif words[:3] == ['está', 'chuvendo', 'em']:
        return QuestionType.IS_RAINY, address(bot, words[3:])

    elif words[0] == 'quão':
        if words[1] == 'quente' or words[1] == 'frio':
            # quão [quente|frio] está em [CIDADE](?)
            # temperatura média
            if words[2] == 'está':
                if words[3] == 'em':
                    return QuestionType.TEMPERATURE, address(bot, words[4:])
                else:
                    return QuestionType.TEMPERATURE, address(bot, words[3:])
            # quão [quente|frio] pode ficar em [CIDADE](?)
            # limites de temperatura
            elif words[2] == 'pode':
                if words[3] == 'ficar':
                    if words[4] == 'em':
                        return QuestionType.TEMP_VARIATION, [address(bot, words[5:])]
    else:
        return QuestionType.WEATHER, address(bot, words)

    # ainda não consegue compreender outras coisas
    raise CouldNotUnderstandException(text)
