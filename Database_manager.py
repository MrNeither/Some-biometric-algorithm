import sqlite3


class DBManager:
    dataBase = None
    dataBaseName = None

    def __init__(self, path='defDB', dbname='Biousers'):
        self.dataBase = sqlite3.connect(path)
        self.dataBaseName = dbname
        self.dataBase.execute(f"CREATE TABLE IF NOT EXISTS {self.dataBaseName} "
                              "(name , bioparametres , PRIMARY KEY(name))")

    def registration(self, newusername, newuserbio):
        # Done: In: username, bioparams Out: 1) good 2)fail(duplicate)
        # Review : May be input as {name: "NAME", data:" F(bioparameters)}?
        if not (newusername and newuserbio):
            raise Exception("Incorrect name or userbio")
        if not self.exist(newusername):
            self.__add_user(newusername, newuserbio)
            return True
        else:
            raise Exception("User with this name already exists")

    def authentication(self, username, userbio):
        # Done: Input same as registration method , Output: 1)Succces 2)Fail  3) NO
        # Review : May be create field bool"Authsuccess"? This field will allow you not to check the user every time
        if self.exist(username):
            return self.dataBase.execute(f"SELECT * FROM {self.dataBaseName} "
                                         f"WHERE name = lower ('{username}') "
                                         f"AND bioparametres = '{userbio}'").fetchone() is not None
        else:
            raise Exception("User with this name not exist")

    def exist(self, username):
        return self.dataBase.execute(f"SELECT EXISTS ("
                                     f"SELECT * FROM {self.dataBaseName} "
                                     f"WHERE name = lower('{username}'))").fetchone()[0]

    def update_user(self, username, olduserbio, newuserbio):
        # Review: Do I need an old userbio?
        if self.authentication(username, olduserbio) and newuserbio:
            self.dataBase.execute(f"UPDATE {self.dataBaseName} "
                                  f"SET bioparametres = '{newuserbio}' "
                                  f"WHERE name = lower('{username}')")
            self.dataBase.commit()
            return True
        else:
            return False

    def remove_user(self, username, userbio):
        if self.authentication(username, userbio):
            self.__delete_user(username)
            return True
        else:
            return False

    def __get_user(self, username):
        if self.exist(username):
            return self.dataBase.execute(f"SELECT * FROM {self.dataBaseName} "
                                         f"WHERE name = lower('{username}')").fetchone()
        else:
            return None

    def __delete_user(self, username):
            self.dataBase.execute(f"DELETE FROM {self.dataBaseName} "
                                  f"WHERE name = lower('{username}')")
            self.dataBase.commit()

    def __add_user(self, username, userbio):
            self.dataBase.execute(f"INSERT INTO {self.dataBaseName} "
                                  f"VALUES (lower('{username}'), '{userbio}')")
            self.dataBase.commit()

    # Todo If the "Authsuccess" field is created, then you need to implement the "user exit" procedure
    def user_exit(self, username):
        pass
