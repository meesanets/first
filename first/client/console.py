from client import ChatClient

class ConsoleChat:
    def __init__(self, chat_client: ChatClient):
        self.login: str = ''
        self.password: str = ''
        self.token: str = ''
        self._chat_client: ChatClient = chat_client

    def start(self):
        while True:
            option = input("/register или /login\n")
            if option == "/register":
                self._get_creds()
                self._chat_client.register(self.login, self.password)
                print("Проверьте свой QR код в директории ./qr")
                continue
            elif option == "/login":
                self._get_creds()
                break
            else:
                print("Введите /register или /login")

        self.token = self._chat_client.auth(self.login, self.password)
        counter = 0

        while True:
            if counter >= 3:
                print("Количество попыток исчерпано. Повторите позже.")
                return

            otp = input("Введите ваш OTP код\n")
            check_status = self._chat_client.check_otp(self.login, otp)

            if not check_status:
                print("Неверный OTP код.")
                counter += 1
                continue

            print("OTP код верный.")
            break

        self._chat_client.start_listen_messages(self._message_received)
        self._get_inputs()

    def _get_creds(self):
        while not self.login:
            self.login = input('Введите логин:\n> ')
        while not self.password:
            self.password = input('Введите пароль:\n> ')

    def _message_received(self, message):
        print(f'[{message.author}]: {message.text}')

    def _get_inputs(self):
        try:
            text = input('> ')
            while text != '/quit':
                if text:
                    self._chat_client.send_message(self.login, text)
                text = input('> ')
        except KeyboardInterrupt:
            pass
        self._chat_client.close()