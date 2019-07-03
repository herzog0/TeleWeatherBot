"""
Definição dos possíveis tipos de questões e o erro associado
"""

from enum import Enum, unique


@unique
class WeatherTypes(Enum):
    """Tipos de questões dos usuários"""

    # descrições gerais
    WEATHER = ['clima', 'tempo', 'previsao', 'previsão', 'previa', 'provisor', 'prosa']

    # valores numéricos
    TEMPERATURE = ['temperatura', 'calor', 'frio', 'quente', 'variacao', 'variação', 'variar']

    HUMIDITY = ['umidade', 'humidade', 'abafado', 'abafar']
    # limites de valores

    # testes de tempo

    RAIN = ['chover', 'chuva', 'chove', 'choveu', 'choverá', 'chovera', 'pingar', 'molhar', 'chovendo',
                'chuvendo', 'molhando', 'pingando']

    SKY_COVERAGE = ['nublado', 'nuvem', 'sombra', 'céu', 'ceu']

    SUNSET = ['por', 'pôr']

    SUNRISE = ['nascer']

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

    # cancelar envio de localização para cadastro
    CANCEL = ['cancelar', 'cancel', '/cancelar']
