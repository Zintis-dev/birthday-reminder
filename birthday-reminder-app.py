import sqlite3
import os
import configparser
from datetime import date, datetime, timedelta

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
               id SERIAL PRIMARY KEY NOT NULL,
               name TEXT NOT NULL,
               lastname TEXT NOT NULL,
               birthday DATE NOT NULL );
    """)
    print("Created table birthdays")

print("""
    /Main MENU/
    1 - add a new birthday
    2 - remove birthday
    3 - check all birthdays
""")

cursor.close()
connection.commit()
connection.close()