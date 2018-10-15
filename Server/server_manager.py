from Server.Database_manager import DBManager
import json


# Todo Add processing of new types requests
'''
Types request (NEED):
{type: 'Registration', name: NAME, parts : NUM OF PARTS}
{type: 'Authentication', name: NAME, parts : NUM OF PARTS}
{type: 'Data', part: PART, data: DATA}
{type: 'Delete' , name: NAME}
{type: 'Update' , name : NAME , biometric: BIOMETRIC}


Types request (NOW):
{type: 'Registration', name: NAME, biometric : BIOMETRIC}
{type: 'Authentication', name: NAME, parts : BIOMETRIC}
{type: 'Delete' , name: NAME}
{type: 'Update' , name : NAME , biometric: BIOMETRIC}
'''


class Session:

    User = None
    AuthSuccess = None
    Answer = None
    dbManager = None

    def __init__(self, user=None, bio_parameter=None):
        self.AuthSuccess = False
        self.dbManager = DBManager()
        if bio_parameter and user:
            self.authentication(user, bio_parameter)

    def registration(self, username, bio_parameter):
        if not (username and bio_parameter):
            self.Answer = b'{ "type" : "Error" , "info" : "Incorrect name or biometric parameters" }'
            return
        if self.dbManager.exist(username):
            self.Answer = b'{ "type" : "Error", "info" : "User with this name already exists" }'
            return
        self.User = username
        self.dbManager.add_user(username, bio_parameter)
        self.Answer = b'{ "type" : "Success" , "info" : "Registration success"}'

    def authentication(self, username, bio_parameter):
        self.AuthSuccess = False
        if self.dbManager.exist(username):
            # Todo if biometric.auth(bio_parameter,self.dbManager.get_user(name)) :
            if self.dbManager.get_user(username)[1] == bio_parameter:
                self.AuthSuccess = True
                self.User = username
                self.Answer = b'{ "type" : "Success" , "info" : "Auth success" }'
            else:
                self.Answer = b'{ "type" : "Error" , "info" : "Auth bad" }'
        else:
            self.Answer = b'{ "type" : "Error" , "info" : "User with this name not exist" }'

    def update_user(self, username, new_biometric):
        if self.AuthSuccess:
            if self.User == username:
                self.dbManager.update_user(username, new_biometric)
                self.Answer = b'{ "type" : "Success" , "info" : "Update user bio_parameters" }'
            else:
                self.Answer = b'{"type" : "Error" , "info" : " Denied" }'
        else:
            self.Answer = b'{"type" : "Error" , "info" : "Need Authentication" }'

    def delete_user(self, username):
        if self.AuthSuccess:
            if self.User == username:
                self.dbManager.delete_user(username)
                self.Answer = b'{ "type" : "Success" , "info" : "Delete user" }'
                self.AuthSuccess = False
            else:
                self.Answer = b'{"type" : "Error" , "info" : " Denied" }'
        else:
            self.Answer = b'{"type" : "Error" , "info" : "Need Authentication" }'

    def get_answer(self):
        return self.Answer

    def processing_request(self, data):
        request = json.loads(data)
        if request['type'] == 'Registration':
            self.registration(request['name'], request['biometric'])

        if request['type'] == 'Authentication':
            self.authentication(request['name'], request['biometric'])

        if request['type'] == 'Update':
            self.update_user(request['name'], request['new_biometric'])

        if request['type'] == 'Delete':
            self.delete_user(request['name'])
