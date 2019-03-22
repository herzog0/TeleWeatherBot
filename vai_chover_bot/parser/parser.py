import string


def get_city(text: str):
    city = text.split()[-1]
    city = city.strip(string.punctuation)

    return city
