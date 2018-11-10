from cryptography.fernet import Fernet
import socket, cv2, json, numpy as np
import Crypto.PublicKey.RSA as RSA


def encryption_sender_decorator_maker(key):
    cipher = Fernet(key)

    def new_decorator(sender, recver):
        def ecnrypt_and_send(open_text: str):
            if isinstance(open_text, str):
                open_text = open_text.encode()
            encrypted_text = cipher.encrypt(open_text)
            return sender(encrypted_text)

        def recv_and_decrypt(buff_size: int):
            cypher_text = recver(buff_size)
            return cipher.decrypt(cypher_text)

        return ecnrypt_and_send, recv_and_decrypt

    return new_decorator


class ClientRequester:
    @staticmethod
    def registration_request(user_id, username, data_size: int, shape: list):
        return f'{{"id" : {user_id}, ' \
               f'"type": "Registration", ' \
               f'"name": "{username}" , ' \
               f'"data_size" : {ClientRequester.load_data_size(user_id, data_size)} , ' \
               f'"shape" : {shape} }}'

    @staticmethod
    def authentication_request(user_id, username, data_size: int, shape: list):
        return f'{{"id" : {user_id}, ' \
               f'"type": "Authentication", ' \
               f'"name": "{username}" , ' \
               f'"data_size" : {ClientRequester.load_data_size(user_id, data_size)} , ' \
               f'"shape" : {shape} }}'

    @staticmethod
    def update_request(user_id, username, data_size: int, shape: list):
        return f'{{"id" : {user_id}, ' \
               f'"type" : "Update" , ' \
               f'"name" : "{username}" , ' \
               f'"data_size" : {ClientRequester.load_data_size(user_id, data_size)} , ' \
               f'"shape" : {shape} }}'

    @staticmethod
    def delete_request(user_id, username):
        return f'{{"id" : {user_id}, "type" : "Delete" ,"name" : "{username}" }}'

    @staticmethod
    def load_data(user_id, data: bytes):
        # return f'{{"id" : {user_id}, "type" : "Load" ,"data" : "{data}" }}'
        return data

    @staticmethod
    def load_data_size(user_id, data_size: int):
        # return len(f'{{"id" : {user_id}, "data" : }}') + data_size + 50
        n = data_size + 1
        return 100 + (n//16)*20 + (n//48)*4

    @staticmethod
    def hello_ack_request(user_id: int, key: bytes):
        return f'{{"id" : {user_id}, ' \
               f'"type" : "HelloACK" , ' \
               f'"session_key" : "{key.decode()}" }}'


class Client:

    sock = None
    RavelPhotoFrame = None
    Shape = None
    user_id = 0

    Answer = None

    def __init__(self):
        self.sock = socket.socket()

    def start_session(self, ip='127.0.0.1', port=2019):
        self.sock.connect((ip, port))
        self.send = self.sock.send
        self.recv = self.sock.recv

        ans = self.recv(1024).decode()
        print(ans)
        answer = json.loads(ans)

        self.user_id = answer['Your new id']
        print(self.user_id)

        # print(answer['public_key'])
        session_key = Fernet.generate_key()

        self.send(ClientRequester.hello_ack_request(self.user_id, session_key).encode())

        decorator = encryption_sender_decorator_maker(session_key)
        self.send, self.recv = decorator(self.send, self.recv)

    def authentication(self, username, faceframe =None):
        if faceframe:
            self.Shape = faceframe.shape
            self.RavelPhotoFrame = faceframe.ravel()
        else:
            self.get_face()
        # Todo size input
        request = ClientRequester.authentication_request(
            self.user_id, username, len(self.RavelPhotoFrame), list(self.Shape))

        self.send(request)
        while not self.load(self.RavelPhotoFrame):
            pass
        self.Answer = self.recv(1024)

    def registration(self, username, faceframe=None):

        if faceframe:
            self.Shape = faceframe.shape
            self.RavelPhotoFrame = faceframe.ravel()
        else:
            self.get_face()

        request = ClientRequester.registration_request(self.user_id, username, len(self.RavelPhotoFrame), list(self.Shape))
        self.send(request)
        while not self.load(self.RavelPhotoFrame):
            pass
        self.Answer = self.recv(1024)

    def load(self, data):
        request = ClientRequester.load_data(self.user_id, bytes(data))

        self.send(request)
        answer = self.recv(1024)
        return True
        # Todo check to good load part

    def change_bio_parameter(self, username, new_faceframe=None):
        if new_faceframe:
            self.Shape = new_faceframe.shape
            self.RavelPhotoFrame = new_faceframe.ravel()
        else:
            self.get_face()
        request = ClientRequester.update_request(self.user_id, username, len(self.RavelPhotoFrame), list(self.Shape))
        self.send(request)
        while not self.load(self.RavelPhotoFrame):
            pass
        self.Answer = self.recv(1024)
        # Todo check server answer for ACK download

    def delete_user(self, username):
        request = ClientRequester.delete_request(self.user_id, username)
        self.send(request)
        self.Answer = self.recv(1024)

    def get_answer(self):
        return self.Answer

    def get_face(self):
        cap = cv2.VideoCapture(0)
        for i in range(15):
            cap.read()

        ret, frame = cap.read()
        while not self.good_photo(frame):
            ret, frame = cap.read()
        print(frame)
        self.Shape = frame.shape
        self.RavelPhotoFrame = frame.ravel()
        cap.release()

    def good_photo(self, frame):
        return True

    def close(self):
        self.sock.close()
