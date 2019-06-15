import json

# variáveis globais
text = ''
c_type = ''
lat = ''
lon = ''
callback_query_data = ''


class Event:

    is_json = True

    def __init__(self, text_p=None, c_type_p=None, lat_p=None, lon_p=None, callback_query_data_p=None):
        self.text = text_p
        self.c_type = c_type_p
        self.lat = lat_p
        self.lon = lon_p
        self.callback_query_data = callback_query_data_p

    @staticmethod
    def get_json():
        return json.loads(Event.create_fake_message(Event()))

    def create_fake_message(self):

        msg = '{"update_id": 123456789, "message": {"message_id": 1234, "from": {' \
              '"id": 123456789, "is_bot": false, "first_name": "Name1", "last_nam' \
              'e": "Name2", "username": "Username", "language_code": "pt-br"}, "c' \
              'hat": {"id": 123456789, "first_name": "Name1", "last_name": "Name2' \
              '", "username": "Username", "type": "private"}, "date": 1559334712,' \
              ' "text": "' + self.text + '"}}'

        location = '{"update_id": 123456789, "message": {"mes' \
                   'sage_id": 1234, "from": {"id": "123456789", "is_bot": false, "f' \
                   'irst_name": "Name1", "last_name": "Name2", "username": "Usern' \
                   'ame", "language_code": "pt-br"}, "chat": {"id": "123456789", "f' \
                   'irst_name": "Name1", "last_name": "Name2", "username": "Usern' \
                   'ame", "type": "private"}, "date": 1559334712, "location": {"l' \
                   'atitude": ' + str(self.lat) + ', "longitude": ' + str(self.lon) + '}}}'

        callback_qury = '{"update_id": 1234567' \
                        '89, "callback_query": {"id": "665226510977244812", "from' \
                        '": {"id": 123456789, "is_bot": false, "first_name": "Nam' \
                        'e1", "last_name": "Name2", "username": "Username", "lang' \
                        'uage_code": "pt-br"}, "message": {"message_id": 2747, "f' \
                        'rom": {"id": 855226901, "is_bot": true, "first_name": "B' \
                        'ot", "username": "bot"}, "chat": {"id": 123456789, "firs' \
                        't_name": "Name1", "last_name": "Name2", "username": "Use' \
                        'rname", "type": "private"}, "date": 1558119911, "edit_da' \
                        'te": 1558119913, "text": "callback_query", "entities": [' \
                        '{"offset": 0, "length": 14, "type": "bold"}]}, "chat_ins' \
                        'tance": "77480181923962338", "data": "' + self.callback_query_data + '"}}'

        if self.c_type == 'message':
            return msg
        elif self.c_type == 'location':
            return location
        else:
            return callback_qury
