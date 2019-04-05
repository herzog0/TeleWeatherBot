class User(object):
    def __init__(self, name, cellphone):
        self.name = name
        self.cellphone = cellphone
        

    @staticmethod
    def from_dict(source):
        user = User(source[u'name'], source[u'cellphone'])
        
        return user

    def to_dict(self):
        dest = {
            u'name': self.name,
            u'cellphone': self.cellphone
        }

        return dest

    def __repr__(self):
        return u'City(name={}, cellphone={})'.format(
            self.name, self.cellphone)