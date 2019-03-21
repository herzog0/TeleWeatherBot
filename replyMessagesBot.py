import sys
import time
import telepot
from telepot.loop import MessageLoop

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg) # glance -> para pegar infos de headline
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        bot.sendMessage(chat_id, "Respondendo a sua mensagem, carissiomo -> " + msg['text'])

#TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot('848892533:AAEBo2WGuR6CrGxJriHqnP2WgWdS09Wxk2Q')
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
