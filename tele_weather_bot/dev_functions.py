import telepot


def set_dev_user(bot, msg, on=True):
    _, _, chat_id = telepot.glance(msg)

    if on:
        bot.dev_dict[chat_id] = {}
        bot.dev_dict[chat_id]['DEV'] = True
        bot.markdown_message(chat_id, "*Lembre-se de desativar o modo developer quando acabar suas tarefas*")
        return True
    else:
        if chat_id in bot.dev_dict:
            if not bot.dev_dict[chat_id]['DEV']:
                bot.markdown_message(chat_id, "*Você já não é mais developer*")
            else:
                bot.dev_dict[chat_id]['DEV'] = False
                bot.markdown_message(chat_id, "*Agora você não é mais developer*")
        else:
            bot.markdown_message(chat_id, "*Você nunca foi developer*")
        return False


def validate_password(bot, msg):
    content_type, _, chat_id = telepot.glance(msg)
    message_id = bot.get_message_id(msg)

    bot.delete_message(message_id)

    try:
        if content_type == 'text':
            if len(msg['text'].lower().strip().split()) == 2 and \
                    msg['text'].lower().strip().split()[0] in ['/set_dev_functions_on'] and \
                    msg['text'].lower().strip().split()[1] == bot.password:
                return True
            else:
                raise ValueError('*Você não inseriu a senha correta*')
        else:
            raise TypeError('*Você não inseriu a senha da forma como deveria*')
    except ValueError as e:
        bot.markdown_message(chat_id, str(e))
        return False
    except TypeError as e:
        bot.markdown_message(chat_id, str(e))
        return False


def list_developer_commands(bot, msg):
    _, _, chat_id = telepot.glance(msg)

    commands = """
*/set_dev_functions_on <senha>* - Iniciar o modo developer.
*/set_dev_functions_off* - Finalizar o modo developer.
*/devhelp* - Mostra esta lista de comandos.    
"""
    bot.markdown_message(chat_id, commands)
