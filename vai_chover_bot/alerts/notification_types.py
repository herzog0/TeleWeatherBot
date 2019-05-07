from enum import Enum, auto, unique


class NotificationTypes(Enum):
    """
    Classe enum que contém os tipos de notificações para a inscrição de um usuário
    """
    DAILY_NEWS = auto()
    """
    Notificações diárias com características personalizáveis
    """

    TRIGGER_WARNING = auto()
    """
    Notificações a partir de gatilhos, como temperatura atingida ou chuva iminente
    """
