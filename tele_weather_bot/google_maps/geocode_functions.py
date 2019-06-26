import googlemaps
import os
from googlemaps.client import geocode, reverse_geocode


def get_user_address_by_coordinates(lat: float, lon: float):
    loc = reverse_geocode(googlemaps.Client(key=os.environ.get('GOOGLEMAPS_TOKEN', None)), (lat, lon))
    if not loc:
        raise LocationNotFoundException("Essas coordenadas não correspondem a um lugar válido para pesquisa.")
    return loc[0]['formatted_address']


def get_user_address_by_name(loc_name):
    if isinstance(loc_name, dict):
        loc_name = f'{loc_name["lat"]} {loc_name["lng"]}'
    loc = geocode(googlemaps.Client(key=os.environ.get('GOOGLEMAPS_TOKEN', None)), loc_name)

    if not loc:
        raise LocationNotFoundException("Não consegui encontrar nenhum endereço correspondente.")
    return loc[0]['formatted_address'],  loc[0]['geometry']['location']


class LocationNotFoundException(Exception):
    def __init__(self, source_text: str = None):
        if source_text:
            self.source_text = source_text
