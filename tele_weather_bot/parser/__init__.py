"""
Parser das questões do usuário
"""

from .question import WeatherTypes, FunctionalTypes
from .parser import parse, MoreThanFiveDaysException, CouldNotUnderstandException
