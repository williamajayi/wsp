import sqlite3

connection = sqlite3.connect("wsp.db")
cursor = connection.cursor()

query = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, firstname varchar(128), lastname varchar(128), email varchar(256), username varchar(30), password varchar(50), status int default 0, score int default 0)"
query2 = "CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY, firstname varchar(128), lastname varchar(128), email varchar(256), username varchar(30), password varchar(50))"
cursor.execute(query)
cursor.execute(query2)

connection.commit()
connection.close()
