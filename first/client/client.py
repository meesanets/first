import threading
from proto.auth_pb2 import *
from proto.auth_pb2_grpc import *
from proto.messaging_pb2 import *
from proto.messaging_pb2_grpc import *
from proto.otp_pb2 import *
from proto.otp_pb2_grpc import *
import qrcode

class ChatClient:
    def __init__(self, port=8000, host='127.0.0.1'):
        self._port = port
        self._host = host
        self._on_message_receive = None
        self._channel = grpc.insecure_channel(f'{self._host}:{self._port}')
        self._msgs_service = MessagingStub(self._channel)
        self._auth_service = AuthStub(self._channel)
        self._otp_service = OtpStub(self._channel)

    def register(self, login, password):
        resp = self._auth_service.Register(RegisterRequest(login=login, password=password))
        if not resp.success:
            print(f"{resp.error}")
            return
        resp_otp = self._otp_service.InitOtp(RequestInitOtp(login=login))
        if resp_otp.error:
            print(f"{resp_otp.error}")
            return
        if resp_otp.secret == "":
            print("Empty OTP secret")
            return
        img = qrcode.make(resp_otp.secret)
        img.save("./qr/my_secret.png")

    def auth(self, login, password):
        response = self._auth_service.Login(LoginRequest(login=login, password=password))
        if not response.success:
            print(f"Ошибка авторизации: {response.error}")
            return
        return response.token

    def check_otp(self, login, otp):
        otp_response = self._otp_service.CheckOtp(RequestCheckOtp(login=login, otp=otp))
        if otp_response.error:
            print(f"{otp_response.error}")
            return None
        return otp_response.valid

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