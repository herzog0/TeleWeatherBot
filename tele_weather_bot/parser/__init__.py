"""
Parser das questões do usuário
"""

from .question import WeatherTypes, FunctionalTypes, CouldNotUnderstandException
from .parser import parse, MoreThanFiveDaysException
