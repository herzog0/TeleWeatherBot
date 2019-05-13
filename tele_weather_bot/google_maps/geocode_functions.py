import googlemaps
from googlemaps.client import geocode, reverse_geocode


__gmaps = None


def init_gmaps(google_api_token: str):
    __gmaps = googlemaps.Client(key=google_api_token)


def get_user_address_by_coordinates(self, lat: float, lon: float):
    loc = reverse_geocode(self.gmaps, (lat, lon))
    if not loc:
        raise LocationNotFoundException("Essas coordenadas não correspondem a um lugar válido para pesquisa.")
    return loc[0]['formatted_address']


def get_user_address_by_name(self, loc_name: str):
    loc = geocode(self.gmaps, loc_name)
    if not loc:
        raise LocationNotFoundException("Não consegui encontrar nenhum endereço correspondente.")
    return loc[0]['formatted_address'],  loc[0]['geometry']['location']


class LocationNotFoundException(Exception):
    def __init__(self, source_text: str = None):
        if source_text:
            self.source_text = source_text
