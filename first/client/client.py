import threading
from proto.auth_pb2 import *
from proto.auth_pb2_grpc import *
from proto.messaging_pb2 import *
from proto.messaging_pb2_grpc import *

class ChatClient:
    def __init__(self, port=8000, host='127.0.0.1'):
        self._port = port
        self._host = host
        self._on_message_receive = None
        self._channel = grpc.insecure_channel(f'{self._host}:{self._port}')
        self._msgs_service = MessagingStub(self._channel)
        self._auth_service = AuthStub(self._channel)

    def register(self, login, password):
        resp = self._auth_service.Register(RegisterRequest(login=login, password=password))
        if not resp.success:
            print(f"Ошибка регистрации: {resp.error}")
            return

    def auth(self, login, password):
        login_response = self._auth_service.Login(LoginRequest(login=login, password=password))
        if not login_response.success:
            print(f"Ошибка авторизации: {login_response.error}")
            return
        return login_response.token

    def start_listen_messages(self, message_received):
        self._on_message_receive = message_received
        threading.Thread(target=self._listen_for_messages, daemon=True).start()

    def _listen_for_messages(self):
        for message in self._msgs_service.MessageStream(Empty()):
            self._on_message_receive(message)

    def send_message(self, username, text):
        message = Message()
        message.author = username
        message.text = text
        self._msgs_service.SendMessage(message)

    def close(self):
        self._channel.close()