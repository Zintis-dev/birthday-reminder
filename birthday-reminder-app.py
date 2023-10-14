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

if os.path.exists(conf_path):
    config = configparser.ConfigParser()
    config.read(conf_path)
    db_name = config["setup"]["db_name"]
    db_path += db_name + ".db"
else:
    print("Config file has not been found!")

