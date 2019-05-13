from datetime import datetime
from ..database.user_keys import UserStateKeys
import json


class User(object):
    """
    Classe User, responsável por definir um usuário a ser referenciado no banco de dados.
    """

    def __init__(self,
                 chat_id,
                 name=None,
                 email=None,
                 notification_coords=None,

                 user_state: UserStateKeys = None
                 ):

        self.__chat_id = str(chat_id)
        self.__name = name
        self.__email = email
        self.__place = {'adress': None, 'coords': None}
        self.__notification_coords = notification_coords

        self.__user_state = user_state

        self.__last_update_time = datetime.now()

    def user_id(self):
        return self.__chat_id

    def name(self):
        return self.__name

    def email(self):
        return self.__email

    def place(self):
        return self.__place

    def notf_coords(self):
        return self.__notification_coords

    def last_update(self):
        return self.__last_update_time

    def state(self):
        return self.__user_state

    def to_dict(self):
        if self.state():
            user_state = str(self.state().name)
        else:
            user_state = None

        dest = {
            self.__chat_id: {
                u'name': self.__name,
                u'email': self.__email,
                u'place': self.__place,
                u'last_update_time': self.__last_update_time,
                u'notification_coords': self.__notification_coords,
                u'state': user_state,
            }
        }
        return dest

    def update_user(self,
                    name=None,
                    email=None,
                    place=None,
                    notification_coords=None,

                    clear_state=False,

                    user_state: UserStateKeys = None,
                    ):

        if name is not None:
            self.__name = name

        if email is not None:
            self.__email = email

        if place is not None:
            self.__place['adress'] = place['adress']
            self.__place['coords'] = place['coords']

        if notification_coords:
            self.__notification_coords = notification_coords

        if user_state:
            self.__user_state = user_state

        if clear_state:
            self.__user_state = None

        self.__last_update_time = datetime.now()

        write_user(self)

    def __repr__(self):
        
        user_string = f"""
name: {self.__name}
email: {self.__email}
place: {self.__place}
last_update_time: {self.__last_update_time}
notification_coords: {self.__notification_coords}
state: {self.state()}
"""
        
        return user_string


def write_user(user: User):
    with open('users.json', 'w') as outfile:
        json.dump(user.to_dict(), outfile)


def read_users():
    try:
        with open('users.json') as infile:
            users = json.load(infile)
            return users
    except IOError:
        return 'O arquivos users.json não existe'
