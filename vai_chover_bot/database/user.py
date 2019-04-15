class User(object):
    def __init__(self, name, cellphone):
        self.name = name
        self.cellphone = cellphone
        

    @staticmethod
    def from_dict(source):
        user = User(source['name'], source['cellphone'])

        return user

    def to_dict(self):
        dest = {
            u'name': self.name,
            u'cellphone': self.cellphone
        }

        return dest

    def __repr__(self):
        return u'User(name={}, cellphone={})'.format(
            self.name, self.cellphone)
