from pyowm.caches.lrucache import LRUCache
from pyowm.weatherapi25.weathercoderegistry import WeatherCodeRegistry

from pyowm.weatherapi25.configuration25 import *


cache = LRUCache(cache_max_size=50)

language = 'pt'

weather_code_registry = WeatherCodeRegistry({
    "chuvoso": [{
        "start": 500,
        "end": 531
    },
    {
        "start": 300,
        "end": 321
    }],
    "ensolarado": [{
        "start": 800,
        "end": 800
    }],
    "nublado": [{
        "start": 801,
        "end": 804
    }],
    "com nevoeiro": [{
        "start": 741,
        "end": 741
    }],
    "com neblina": [{
        "start": 721,
        "end": 721
    }],
    "com nevoeiro": [{
        "start": 701,
        "end": 701
    }],
    "nevando": [{
        "start": 600,
        "end": 622
    }],
    "com tornado": [{
        "start": 781,
        "end": 781
    },
    {
        "start": 900,
        "end": 900
    }],
    "em tempestade": [{
        "start": 901,
        "end": 901
    },
    {
        "start": 960,
        "end": 961
    }],
    "com furacão": [{
        "start": 902,
        "end": 902
    },
    {
        "start": 962,
        "end": 962
    }]
})
