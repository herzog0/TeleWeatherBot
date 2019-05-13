"""
Algumas pequenas mudanças na configuração
"""

from pyowm.caches.lrucache import LRUCache
from pyowm.weatherapi25.weathercoderegistry import WeatherCodeRegistry

from pyowm.weatherapi25.configuration25 import *


# uso de um cache LRU simples pra tentar reduzir os requests no OWM
cache = LRUCache(cache_max_size=50)

# tradução para português
language = 'pt'
