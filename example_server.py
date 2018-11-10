from Server.server_manager import start_session
import Crypto.PublicKey.RSA as RSA
import threading
import socket
from Biometric.FaceDetection import FaceDetection
# Done Handling multiple connections via threads.

'''
password = "MySuperSecretKey"
key = RSA.generate(2048)

encrypted_key = key.exportKey(
    passphrase=password,
    pkcs=8,
    protection="scryptAndAES128-CBC"
)

with open('PRIVATE.bin', 'wb') as f:
    f.write(encrypted_key)

with open('PUBLIC.pem', 'wb') as f:
    f.write(key.publickey().exportKey())
'''


Test_DIR = '/home/mr_neither/Work/PycharmProjects/Some-biometric-algorithm/Biometric'
# Todo Sasha
classifier = FaceDetection(Test_DIR)


serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_sock.bind(('', 2019))
serv_sock.listen(10)

print("Server Up")

while True:
    try:
        conn, addr = serv_sock.accept()
        th = threading.Thread(target=start_session, args=(conn, addr, classifier))
        th.start()

        print('Connected by', addr)

    except Exception as e:
        print(e)
        print("Server stoppped!!")
        break

serv_sock.close()
