import sqlite3
from sqlite3 import Error as sqlError


def sql_connection(name):
    try:
        connection = sqlite3.connect(name)
        print("Connection is done")
        return connection
    except sqlError:
        print(sqlError)


def sql_table(connection):
    cursorObj = connection.cursor()
    try:
        cursorObj.execute(
            "CREATE TABLE employees(id integer PRIMARY KEY, text text)")
        connection.commit()
    except Exception:
        print("CREATE TABLE error sql_table")


connection = sql_connection("main_base.db")
sql_table(connection)


def sql_insert(con, text,):
    cursorObj = con.cursor()
    try:
        cursorObj.executemany("INSERT INTO employees(text) VALUES(?, ?)",
                              tuple(text))
        con.commit()
    except Exception:
        print("INSERT error уже существует такая запись sql_insert")
