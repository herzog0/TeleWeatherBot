class User(object):
    """
    Classe User, responsável por definir um usuário a ser referenciado no banco de dados.
    """

    def __init__(self, chat_id, name=None, email=None, city=None):
        """
        :param chat_id: o id do chat do telegram com o usuário
        :type chat_id: str

        :param name: o nome da pessoa que está conversando com o bot
        :type name: str

        :param email: o email da pessoa
        :type email: str

        :param city: a cidade da pessoa
        :type city: str

        """
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
