from Server.Database_manager import DBManager
from cryptography.fernet import Fernet
import json, socket, random, numpy as np
import Crypto.PublicKey.RSA as RSA

# Todo Add processing of new types requests
# Todo problem with specifying the size of the buffer to load the file. When encrypted, it increases
# bug for some errors the server falls. To make the error handler


def encryption_sender_decorator_maker(key):
    cipher = Fernet(key)

    def new_decorator(sender, recver):
        def ecnrypt_and_send(open_text):
            if isinstance(open_text, str):
                open_text = open_text.encode()
            encrypted_text = cipher.encrypt(open_text)
            return sender(encrypted_text)

        def recv_and_decrypt(buff_size: int):
            cypher_text = recver(buff_size)
            return cipher.decrypt(cypher_text)

        return ecnrypt_and_send, recv_and_decrypt

    return new_decorator


class ServerResponder:
    @staticmethod
    def hello(data: str, new_id: int):
        return f'{{"type" : "Hello" , "Your new id" : "{new_id}" , "public_key" : "{data.encode()}" }}'.encode()

    @staticmethod
    def error(info: str):
        return ServerResponder.respond_template("Error", info)

    @staticmethod
    def success(info: str):
        return ServerResponder.respond_template("Success", info)

    @staticmethod
    def respond_template(type_r, info):
        return f'{{ "type" : "{type_r}" , "info" : "{info}" }}'


class Session:
    user_id = None
    Username = None
    AuthSuccess = None
    Answer = None
    dbManager = None

    send = recv = lambda: None

    # Review Need this fields?
    PredictPhoto = None
    public_key = None
    private_key = None

    def __init__(self, classifier):
        self.AuthSuccess = False
        self.dbManager = DBManager()
        self.public_key = open('PUBLIC.pem').read()
        self.private_key = open('PRIVATE.bin').read()
        self.classifier = classifier

    def start_session(self, conn: socket.socket, addr: tuple):
        try:
            self.user_id = random.randint(10, 100)
            self.send = conn.send
            self.recv = conn.recv

            self.send(
                ServerResponder.hello(
                    self.public_key, self.user_id))

            request = self.recv(1024).decode()
            print(request)
            self.processing_request(request)
            self.work()
        except Exception as e:
            print(e)
            raise e

    def work(self):
        try:
            while True:
                data = self.recv(1024)
                print(data)
                self.processing_request(data)
                self.send(self.get_answer())
        except Exception as e:
            print(e)
            raise e

    def registration(self, username: str):

        if not (username and self.check_photo()):
            self.Answer = ServerResponder.error("Incorrect name or Photo")
            return

        if self.dbManager.exist(username):
            self.Answer = ServerResponder.error("User with this name already exists")
            return

        self.Username = username
        # Done self.PredictPhoto must contains vecotr<256> after calling CNN-method
        self.dbManager.add_user(username, self.PredictPhoto)
        self.Answer = ServerResponder.success("Registration success")

    def check_photo(self):
        return True

    def authentication(self, username: str):
        self.AuthSuccess = False

        if self.dbManager.exist(username):
            # Todo Sasha if biometric.auth(bio_parameter,self.dbManager.get_user(name)) :
            # review : self.dbMan return tuple => using [1] . its bad
            if self.classifier.compare(
                    self.PredictPhoto, self.dbManager.get_user(username)[1]):

                self.AuthSuccess = True
                self.Username = username
                self.Answer = ServerResponder.success("Auth success")
            else:
                self.Answer = ServerResponder.error("Auth bad")
        else:
            self.Answer = ServerResponder.error("User with this name not exist")

    # Done new_Photo must be vector<256>
    def update_user(self, username):
        if self.AuthSuccess:
            if self.Username == username:
                self.dbManager.update_user(username, self.PredictPhoto)
                self.Answer = ServerResponder.success("Update user Photo")
            else:
                self.Answer = ServerResponder.error("Denied")
        else:
            self.Answer = ServerResponder.error("Need Authentication")

    def delete_user(self, username):
        if self.AuthSuccess:
            if self.Username == username:
                self.dbManager.delete_user(username)
                self.Answer = ServerResponder.success("Delete user")
                self.AuthSuccess = False
            else:
                self.Answer = ServerResponder.error("Denied")
        else:
            self.Answer = ServerResponder.error("Need Authentication")

    def get_answer(self):
        return self.Answer

    def set_encrypted_session(self, key: bytes):
        decorator = encryption_sender_decorator_maker(key)
        self.send, self.recv = decorator(self.send, self.recv)

    def processing_request(self, data):
        request = json.loads(data)
        if request['id'] != self.user_id:
            self.Answer = ServerResponder.error("Its not you")

        if request['type'] == 'HelloACK':
            self.set_encrypted_session(request['session_key'])

        elif request['type'] == 'Registration':
            if self.download(request['data_size'], request['shape']):
                self.registration(request['name'])

        elif request['type'] == 'Authentication':
            if self.download(request['data_size'], request['shape']):
                self.authentication(request['name'])

        elif request['type'] == 'Update':
            if self.download(request['data_size'], request['shape']):
                self.update_user(request['name'])

        elif request['type'] == 'Delete':
            self.delete_user(request['name'])
        else:
            self.Answer = ServerResponder.error("Bad request")

    def download(self, data_size: int, shape: tuple):
        req = self.recv(data_size)
        try:
            pref_photo = np.frombuffer(req, dtype=np.uint8).reshape(shape)
            # Todo Sasha
            self.PredictPhoto = self.classifier.predict(pref_photo)
        except Exception:
            self.Answer = ServerResponder.error("Bad Photo")
            return False
        # Todo change send to success  and fail download
        self.send(b'Good')
        return True


def start_session(conn: socket.socket, addr: tuple, classifier=None):
    session = Session(classifier)
    try:
        session.start_session(conn, addr)
    except Exception as e:
        print(e)
        print('Session closed')
        conn.close()
        return
