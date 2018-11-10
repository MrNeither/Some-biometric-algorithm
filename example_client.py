from Client.user_service import Client

session = Client()

session.start_session('127.0.0.1', 2019)
while True:
    res = input("1 - registration , 2 - authentication , 3- Update, 4-delete, 5-ext")

    if res == '5':
        break
    user = input('Name = ')
    if res == '4':
        session.delete_user(user)
        continue
    if res == '3':
        session.change_bio_parameter(user)
    if res == '2':
        session.authentication(user)
    if res == '1':
        session.registration(user)

    print("Server answer = ", session.get_answer())
session.close()

