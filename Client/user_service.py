import socket


class Client:

    sock = None
    Answer = None

    def __init__(self):
        self.sock = socket.socket()

    def connect(self, ip='127.0.0.1', port=2018):
        self.sock.connect((ip, port))

    def authentication(self, username, bio_parameter):
        request = f'{{ "type": "Authentication", "name": "{username}" , "biometric" : "{bio_parameter}" }}'
        self.sock.send(request.encode())
        self.Answer = self.sock.recv(1024)

    def registration(self, username, bio_parameter):
        request = f'{{ "type": "Registration", "name": "{username}" , "biometric" : "{bio_parameter}" }}'
        self.sock.send(request.encode())
        self.Answer = self.sock.recv(1024)

    def change_bio_parameter(self, username, new_bio_parameter):
        request = f'{{ "type" : "Update" , "name" : "{username}" , "new_biometric" : "{new_bio_parameter}" }}'
        self.sock.send(request.encode())
        self.Answer = self.sock.recv(1024)

    def delete_user(self, username):
        request = f'{{ "type" : "Delete" ,"name" : "{username}" }}'
        self.sock.send(request.encode())
        self.Answer = self.sock.recv(1024)

    def get_answer(self):
        return self.Answer
