import requests


class TelegramBot:
    def __init__(self, idGrupo, token):
        self.idGrupo = "-967218093"
        self.token = "6037793943:AAHTTYIeUkOfRb6_SUpqtN2GdfTdbSbuz50"

    def bot_send_text(self, message):
        send_text = 'https://api.telegram.org/bot' + self.token + '/sendMessage?chat_id=' + self.idGrupo + '&parse_mode=Markdown&text=' + message

        response = requests.get(send_text)

        return response

