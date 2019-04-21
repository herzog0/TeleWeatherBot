"""
Definição dos possíveis tipos de questões e o erro associado
"""

from enum import Enum, auto, unique


@unique
class QuestionType(Enum):
    """Tipos de questões dos usuários"""

    # descrições gerais
    WEATHER         = auto()
    # valores numéricos
    TEMPERATURE     = auto()
    HUMIDITY        = auto()
    # limites de valores
    TEMP_VARIATION  = auto()
    # testes de tempo
    IS_RAINY        = auto()
    IS_SUNNY        = auto()
    IS_CLOUDY       = auto()

    SET_ALARM       = auto()
    # origem das informações da última cidade
    #SOURCE          = auto()


class CouldNotUnderstandException(Exception):
    """Exceção de não compreender a questão ou o tipo dela"""
    def __init__(self, source_text: str = None):
        """Pode conter o texto que não foi compreendido"""
        if source_text:
            self.source_text = source_text
