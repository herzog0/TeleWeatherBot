import googlemaps
from googlemaps.client import geocode, reverse_geocode
from TOKENS_HERE import GOOGLEMAPS_TOKEN

__gmaps = googlemaps.Client(key=GOOGLEMAPS_TOKEN)


def get_user_address_by_coordinates(lat: float, lon: float):
    loc = reverse_geocode(__gmaps, (lat, lon))
    if not loc:
        raise LocationNotFoundException("Essas coordenadas não correspondem a um lugar válido para pesquisa.")
    return loc[0]['formatted_address']


def get_user_address_by_name(loc_name: str):
    loc = geocode(__gmaps, loc_name)
    if not loc:
        raise LocationNotFoundException("Não consegui encontrar nenhum endereço correspondente.")
    return loc[0]['formatted_address'],  loc[0]['geometry']['location']


class LocationNotFoundException(Exception):
    def __init__(self, source_text: str = None):
        if source_text:
            self.source_text = source_text
