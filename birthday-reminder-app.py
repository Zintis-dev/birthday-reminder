import sqlite3
import os
import configparser
from datetime import date, datetime
import calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Adds birthday to the database
def add_new_birthday():
    while True:
        try:
            print("NAME: ")
            name = input()
            print("LASTNAME: ")
            lastname = input()
            print("YEAR: ")
            year = get_user_year()
            print("MONTH: ")
            month = get_user_month()
            print("DAY: ")
            day = get_user_day(month, year)
            break
        except Exception as e:
            print(e)
    birthday = f"{year}-{month}-{day}"
    cursor.execute("INSERT INTO birthdays (name, lastname, birthday) VALUES (?, ?, ?)", (name, lastname, birthday))
    print("Birthday added successfully")


# Fetches all birthdays from the database, prints out tuple
def print_birthdays():
    print("Fetching all birthdays")
    print("ID, NAME, LASTNAME, BIRTHDAY")
    cursor.execute("SELECT * FROM birthdays")
    results = cursor.fetchall()
    for result in results:
        print(result)


def print_main_menu():
    print("""
    /Main MENU/
    1 - add a new birthday
    2 - remove birthday
    3 - check all birthdays
    4 - exit
    """)


def is_year_valid(year):
    MIN_YEAR = 1900
    MAX_YEAR = date.today().year

    if year < MIN_YEAR or year > MAX_YEAR:
        return False
    return True

def get_user_year():
    while True:
        year = parse_to_int(input())
        if isinstance(year, int) and is_year_valid(year):
            break
        print("year not valid")
    return year

def is_month_valid(month):
    if month < 1 or month > 12:
        return False
    return True

def get_user_month():
    while True:
        month = parse_to_int(input())
        if isinstance(month, int) and is_month_valid(month):
            break
        print("Invalid month")
    return month

#TODO: Need to seperate safety checks for day input and add isInstance(day, int)
def get_user_day(month, year):
    day_count_dict = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    MAX_DAY = day_count_dict.get(month)
    THIS_YEAR = datetime.year
    IS_LEAP_YEAR = calendar.isleap(year)

    if IS_LEAP_YEAR:
        day_count_dict[2] += feb_day_count + 1

    while True:
        day = parse_to_int(input())
        if day <= day_count_dict[month] and day > 0:
            break
        print("Invalid day")
    return day


def remove_birthday():
    print_birthdays()
    print("--------------------")
    print("Type ID to delete the birthday")
    print("ID: ")
    id = input()
    cursor.execute("DELETE FROM birthdays WHERE ID = (?)", (id,))
    print("Removed")


#TODO: Fix the incorrect year
def check_birthdays():
    DATE_TODAY = str(datetime.today().date())
    cursor.execute("SELECT * FROM birthdays WHERE birthday = (?)", (DATE_TODAY,))
    results = cursor.fetchall()
    if results:
        print("Todays birthdays: ")
        for result in results:
            name = result[1]
            lastname = result[2]
            print(f"{result[1]} {result[2]}")
            send_email(name, lastname)


def send_email(name, lastname):
    # Create the MIME object
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Attach the body to the email
    message.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Use TLS for secure connection
        server.login(sender_email, app_password_email)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)

    print('Email sent successfully!')


def parse_to_int(value):
    try:
        return int(value)
    except:
        pass


file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)

conf_name = "config.conf"
conf_path = dir_path + "\\" + conf_name

db_name = None
db_path = dir_path + "\\"

# If config exists, reads the config's values
if os.path.exists(conf_path):
    config = configparser.ConfigParser()
    config.read(conf_path)
    db_name = config["setup"]["db_name"]
    db_path += db_name + ".db"
    sender_email = config["smtp"]["sender_email"]
    app_password_email = config["smtp"]["app_password_email"]
    receiver_email = config["smtp"]["receiver_email"]
    smtp_server = config["smtp"]["smtp_server"]
    smtp_port = config["smtp"]["smtp_port"]
    subject = config["email"]["subject"]
    body = config["email"]["body"]
else:
    print("Config file has not been found!")
    exit()

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='birthdays'")
results = cursor.fetchone()

#TODO: add this to DB migrations file
if not results:
    cursor.execute("""CREATE TABLE IF NOT EXISTS birthdays (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               lastname TEXT NOT NULL,
               birthday DATE NOT NULL );
    """)
    print("Created table birthdays")

check_birthdays()

while True:
    print_main_menu()
    try:
        user_input = int(input())
        if user_input == 1:
            add_new_birthday()
        if user_input == 2:
            remove_birthday()
        if user_input == 3:
            print_birthdays()
        if user_input == 4:
            print("Bye")
            break
    except ValueError as e:
        print("Invalid input!")

cursor.close()
connection.commit()
connection.close()
