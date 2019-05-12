"""
Definição dos possíveis tipos de questões e o erro associado
"""

from enum import Enum, auto, unique


@unique
class WeatherTypes(Enum):
    """Tipos de questões dos usuários"""

    # descrições gerais
    WEATHER = ['clima', 'tempo', 'previsao', 'previsão', 'previa', 'provisor', 'prosa']

    # valores numéricos
    TEMPERATURE = ['temperatura', 'calor', 'frio', 'quente']

    HUMIDITY = ['umidade', 'humidade', 'abafado', 'abafar']
    # limites de valores

    TEMP_VARIATION = ['variacao', 'variação', 'variar']
    # testes de tempo

    IS_RAINY = ['chover', 'chuva', 'chove', 'choveu', 'choverá', 'chovera', 'pingar', 'molhar', 'chovendo',
                'chuvendo', 'molhando', 'pingando']

    IS_SUNNY = ['sol']

    IS_CLOUDY = ['nublado', 'nuvem', 'sombra']

    # pergunta critica
    WHEN = ['quando']


@unique
class FunctionalTypes(Enum):

    # criar notificações
    SET_ALARM = ['alarme', 'alerta', 'aviso', 'avise', 'notificacao', 'not', '/alarme', '/notificacao', 'notificação']

    # cadastrar
    SET_SUBSCRIPTION = ['/cadastro', 'cadastro', 'cadastrar']

    # início do bot
    INITIAL_MESSAGE = ['/start', 'start', 'começar', 'comecar', 'inicio', 'início', 'oi', 'ola']

    # pedido de ajuda
    HELP_REQUEST = ['/help', 'help', '/ajuda', 'ajuda', 'socorro']

    DEV_FUNCTIONS_ON = ['/set_dev_functions_on']

    DEV_FUNCTIONS_OFF = ['/set_dev_functions_off']

    DEV_COMMANDS = ['/devhelp']


class CouldNotUnderstandException(Exception):
    """Exceção de não compreender a questão ou o tipo dela"""
    def __init__(self, source_text: str = None):
        """Pode conter o texto que não foi compreendido"""
        if source_text:
            self.source_text = source_text
