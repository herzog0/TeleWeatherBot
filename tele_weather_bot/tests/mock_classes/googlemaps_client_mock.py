class Client(object):
    def __init__(self, key):
        self.key = key


def geocode(client: Client = None, loc_name: str = "camcinas"):
    loc = [
        {
            "formatted_address": f"end_mock: {loc_name}",
            "geometry": {"location": {"lat": "lat mock", "lng": "lng mock"}}
        }
    ]

    return loc[0]["formatted_address"],  loc[0]["geometry"]["location"]
