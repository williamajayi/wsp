import sqlite3

class Admin:
    def __init__(self):
        return

    @classmethod
    def find_admin_by_username(cls, username):
        connection = sqlite3.connect("wsp.db")
        cursor = connection.cursor()
        select_query = "SELECT * FROM admin WHERE username = ?"
        result = cursor.execute(select_query, (username,))
        row = result.fetchone()
        return row

    @classmethod
    def find_all_admin(cls):
        connection = sqlite3.connect("wsp.db")
        cursor = connection.cursor()
        select_query = "SELECT * FROM admin"
        result = cursor.execute(select_query)
        row = result.fetchall()
        connection.close()
        return row

    def register_admin(self, firstname, lastname, email, username, password):
        if self.find_admin_by_username(username):
            return "Admin user already exists in the database"

        connection = sqlite3.connect('wsp.db')
        cursor = connection.cursor()
        query = "INSERT INTO admin VALUES (NULL,?, ?, ?, ?, ?)"
        query = cursor.execute(query, (firstname, lastname, email, username, password))
        if query:
            response = "Admin registration successful"
            connection.commit()
            connection.close()
        else:
            response = "Admin registration unsuccessful"
        return response

    def login_admin(self, username, password):
        if self.find_admin_by_username(username):
            connection = sqlite3.connect("wsp.db")
            cursor = connection.cursor()
            select_query = "SELECT password FROM admin WHERE username = ?"
            result = cursor.execute(select_query, (username,))
            row = result.fetchone()
            if password == row[0]:
                return True
        return False

    def delete_admin(self, username):
        if self.find_admin_by_username(username):
            connection = sqlite3.connect("wsp.db")
            cursor = connection.cursor()
            select_query = "DELETE FROM admin WHERE username = ?"
            result = cursor.execute(select_query, (username,))
            if result:
                connection.commit()
                connection.close()
                return True
        return False

    def update_admin_password(self, username, password):
        if self.find_admin_by_username(username):
            connection = sqlite3.connect("wsp.db")
            cursor = connection.cursor()
            select_query = "UPDATE admin SET password=? WHERE username = ?"
            result = cursor.execute(select_query, (password, username))
            if result:
                connection.commit()
                connection.close()
                return True
            return False
