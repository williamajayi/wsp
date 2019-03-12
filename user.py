import sqlite3

class User:
    def __init__(self):
        return

    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect("wsp.db")
        cursor = connection.cursor()
        select_query = "SELECT * FROM users WHERE username = ?"
        result = cursor.execute(select_query, (username,))
        row = result.fetchone()
        return row

    @classmethod
    def find_by_userid(cls, userid):
        connection = sqlite3.connect("wsp.db")
        cursor = connection.cursor()
        select_query = "SELECT * FROM users WHERE id = ?"
        result = cursor.execute(select_query, (userid,))
        row = result.fetchone()
        connection.close()
        return row

    @classmethod
    def find_all(cls):
        connection = sqlite3.connect("wsp.db")
        cursor = connection.cursor()
        select_query = "SELECT * FROM users"
        result = cursor.execute(select_query)
        row = result.fetchall()
        connection.close()
        return row

    def register(self, firstname, lastname, email, username, password):
        if self.find_by_username(username):
            return "User already exists in the database"

        connection = sqlite3.connect('wsp.db')
        cursor = connection.cursor()
        query = "INSERT INTO users VALUES (NULL,?, ?, ?, ?, ?, 0, 0)"
        query = cursor.execute(query, (firstname, lastname, email, username, password))
        if query:
            response = "User registration successful"
            connection.commit()
            connection.close()
        else:
            response = "User registration unsuccessful"
        return response

    def login(self, username, password):
        if self.find_by_username(username):
            connection = sqlite3.connect("wsp.db")
            cursor = connection.cursor()
            select_query = "SELECT password FROM users WHERE username = ?"
            result = cursor.execute(select_query, (username,))
            row = result.fetchone()
            if password == row[0]:
                return True
        return False

    def delete(self, username):
        if self.find_by_username(username):
            connection = sqlite3.connect("wsp.db")
            cursor = connection.cursor()
            select_query = "DELETE FROM users WHERE username = ?"
            result = cursor.execute(select_query, (username,))
            if result:
                connection.commit()
                connection.close()
                return True
        return False

    def update(self, username, status, score):
        if self.find_by_username(username):
            connection = sqlite3.connect("wsp.db")
            cursor = connection.cursor()
            select_query = "UPDATE users SET status=?, score=? WHERE username = ?"
            result = cursor.execute(select_query, (status, score, username))
            if result:
                connection.commit()
                connection.close()
                return True
            return False
