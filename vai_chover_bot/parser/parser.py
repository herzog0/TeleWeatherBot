"""
O parser propriamente
"""

from .question import QuestionType, CouldNotUnderstandException
import string


def join_city_name(words: list) -> str:
    """Junta um lista de palavras em um nome de uma cidade"""
    # primeiro capitaliza cada palavra
    words = [word.capitalize() for word in words]
    # junta em uma só
    city = ' '.join(words)
    # e remove possíveis pontuações
    city = city.strip(string.punctuation)

    return city


"""Parser das entradas dos usuários"""

# TODO: usar estado interno, talvez com o NLTK


def parse(text: str) -> tuple:
    """Tentar ler a questão do usuário e decidir seu tipo e o que precisa para respondê-lo"""

    # TODO MELHORAR O ENTENDIMENTO DE PERGUNTAS SOBRE O CLIMA

    words = text.lower().strip().split()

    if words[0] in ['/cadastro', 'cadastro', 'cadastrar']:
        return QuestionType.SET_SUBSCRIPTION, ['None']

    if words[0] in ['/start', 'start', 'começar', 'comecar', 'inicio', 'início', 'oi', 'ola']:
        print('entoru')
        return QuestionType.INITIAL_MESSAGE, ['None']

    if words[0] in ['/help', 'help', '/ajuda', 'ajuda', 'socorro']:
        return QuestionType.HELP_REQUEST, ['None']

    for word in words:
        if word in ('alarme', 'alerta', 'aviso', 'avise'):
            return QuestionType.SET_ALARM, ['None']

    if 1 <= len(words) <= 2:
        return QuestionType.WEATHER, [join_city_name(words)]

    # como está [CIDADE](?)
    # descriçao do tempo
    elif words[:2] == ['como', 'está']:
        return QuestionType.WEATHER, [join_city_name(words[2:])]

    # está chuvendo em [CIDADE](?)
    # teste de chuva
    elif words[:3] == ['está', 'chuvendo', 'em']:
        return QuestionType.IS_RAINY, [join_city_name(words[3:])]

    elif words[0] == 'quão':
        if words[1] == 'quente' or words[1] == 'frio':
            # quão [quente|frio] está em [CIDADE](?)
            # temperatura média
            if words[2] == 'está':
                if words[3] == 'em':
                    return QuestionType.TEMPERATURE, [join_city_name(words[4:])]
                else:
                    return QuestionType.TEMPERATURE, [join_city_name(words[3:])]
            # quão [quente|frio] pode ficar em [CIDADE](?)
            # limites de temperatura
            elif words[2] == 'pode':
                if words[3] == 'ficar':
                    if words[4] == 'em':
                        return QuestionType.TEMP_VARIATION, [join_city_name(words[5:])]

    # ainda não consegue compreender outras coisas
    raise CouldNotUnderstandException(text)
