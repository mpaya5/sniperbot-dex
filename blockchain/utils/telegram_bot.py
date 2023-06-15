import requests

import os
from dotenv import load_dotenv
load_dotenv()


class TelegramBot:
    def __init__(self, idGrupo, token):
        self.idGrupo = os.getenv('TELEGRAM_GROUP_ID')
        self.token = os.getenv('TOKEN_TELEGRAM_BOT')

    def bot_send_text(self, message):
        send_text = 'https://api.telegram.org/bot' + self.token + '/sendMessage?chat_id=' + self.idGrupo + '&parse_mode=Markdown&text=' + message

        response = requests.get(send_text)

        return response

