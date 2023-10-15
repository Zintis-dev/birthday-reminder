import sqlite3
import os
import configparser
from datetime import date, datetime, timedelta
import smtpd

file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)

conf_name = "config.conf" 
conf_path = dir_path + "\\" + conf_name

db_name = None
db_path = dir_path + "\\"

#If config exists, reads the config's values
if os.path.exists(conf_path):
    config = configparser.ConfigParser()
    config.read(conf_path)
    db_name = config["setup"]["db_name"]
    db_path += db_name + ".db"
else:
    print("Config file has not been found!")

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='birthdays'")
reults = cursor.fetchone()

#Checks if database is empty, if it is - creates table birthdays
if not reults:
    cursor.execute("""CREATE TABLE IF NOT EXISTS birthdays (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               lastname TEXT NOT NULL,
               birthday DATE NOT NULL );
    """)
    print("Created table birthdays")

def print_main_menu():
    print("""
    /Main MENU/
    1 - add a new birthday
    2 - remove birthday
    3 - check all birthdays
    4 - exit
    """)

#Adds birthday to the database, safety checks are not yet implemented 
def add_new_birthday():
    try:
        while True:
            print("NAME: ")
            name = input()
            print("LASTNAME: ")
            lastname = input()
            print("BIRTHDAY(YYYY-MM-DD): ")
            birthday = input()
            break
        cursor.execute(f"INSERT INTO birthdays (name, lastname, birthday) VALUES (?, ?, ?)", (name, lastname, birthday))
        print("Birthday has been added successfuly")
    except Exception as e:
        print(e)

#Fetches all birthdays from the database, prints out tuple
def check_birthdays():
    print("Fetching all birthdays")
    cursor.execute("SELECT * FROM birthdays")
    results = cursor.fetchall()
    for result in results:
        print(result)

while True:
    print_main_menu()
    try:
        user_input = int(input())
        if user_input == 1:
            add_new_birthday()
            break
        if user_input == 2:
            print("remove birthday")
            break
        if user_input == 3:
            check_birthdays()
            break
        if user_input == 4:
            print("exit the application")
            break
    except ValueError as e:
        print("Invalid input!")

cursor.close()
connection.commit()
connection.close()