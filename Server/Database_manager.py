import sqlite3


class DBManager:
    dataBase = None
    dataBaseName = None

    def __init__(self, path='tempDB', data_base_name='Users'):
        self.dataBase = sqlite3.connect(path)
        self.dataBaseName = data_base_name
        self.dataBase.execute(f"CREATE TABLE IF NOT EXISTS {self.dataBaseName} "
                              "(username , bio_parameter , PRIMARY KEY(username))")

    def exist(self, username):
        return self.dataBase.execute(f"SELECT EXISTS ("
                                     f"SELECT * FROM {self.dataBaseName} "
                                     f"WHERE username = lower('{username}'))").fetchone()[0]

    def update_user(self, username, new_bio_parameter):
            self.dataBase.execute(f"UPDATE {self.dataBaseName} "
                                  f"SET bio_parameter = '{new_bio_parameter}' "
                                  f"WHERE username = lower('{username}')")
            self.dataBase.commit()

    def get_user(self, username):
        if self.exist(username):
            return self.dataBase.execute(f"SELECT * FROM {self.dataBaseName} "
                                         f"WHERE username = lower('{username}')").fetchone()
        else:
            return None

    def delete_user(self, username):
            self.dataBase.execute(f"DELETE FROM {self.dataBaseName} "
                                  f"WHERE username = lower('{username}')")
            self.dataBase.commit()

    def add_user(self, username, bio_parameter):
            self.dataBase.execute(f"INSERT INTO {self.dataBaseName} "
                                  f"VALUES (lower('{username}'), '{bio_parameter}')")
            self.dataBase.commit()
