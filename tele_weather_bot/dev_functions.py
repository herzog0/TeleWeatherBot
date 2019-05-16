import telepot


def set_dev_user(dev_dict: dict, chat_id: str, on=True):

    if on:
        dev_dict.update({chat_id: {'DEV': True}})
        return "*Lembre-se de desativar o modo developer quando acabar suas tarefas*"
    else:
        if chat_id in dev_dict:
            if not dev_dict[chat_id]['DEV']:
                return "*Você já não é mais developer*"
            else:
                dev_dict.update({chat_id: {'DEV': False}})
                return "*Agora você não é mais developer*"
        else:
            return "*Você nunca foi developer*"


def validate_password(text: str, password: str):
    if len(text.lower().strip().split()) == 2:
            if text.lower().strip().split()[0] in ['/set_dev_functions_on'] and \
                    text.lower().strip().split()[1] == password:
                return True
            else:
                return '*Você não inseriu a senha correta*'
    else:
        return '*A senha definida não deveria conter mais que uma palavra*'


def list_developer_commands():

    commands = """
*/set_dev_functions_on <senha>* - Iniciar o modo developer.
*/set_dev_functions_off* - Finalizar o modo developer.
*/devhelp* - Mostra esta lista de comandos.    
"""
    return commands
