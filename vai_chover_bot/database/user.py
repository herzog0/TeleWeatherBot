class User(object):
    def __init__(self, chat_id, name, email, city):
        self.id = chat_id
        self.name = name
        self.email = email
        self.city = city

    @staticmethod
    def from_dict(source):
        user = User(source['id'], source['name'], source['email'], source['city'])
        return user

    def to_dict(self):
        dest = {
            u'id': self.id,
            u'name': self.name,
            u'email': self.email,
            u'city': self.city,
        }
        return dest

    def __repr__(self):
        return u'User(id={}, name={}, email={}, city={})'.format(
                self.id, self.name, self.email, self.city)
