import sqlite3
import os
import configparser
from datetime import date, datetime
import calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging, logging.config
import yaml

# Gets user input for name, lastname, year, month and day. Inserts data into database
def get_birthday_data():
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
            logger.error(str(e))
    add_birthday_to_db(name, lastname, day, month, year)
    print_seperator()

def add_birthday_to_db(name, lastname, day, month, year):
    try:
        logger.info("Adding birthday to the database")
        cursor.execute("INSERT INTO birthdays (name, lastname, day, month, year) VALUES (?, ?, ?, ?, ?)",
                       (name, lastname, day, month, year))
        logger.info("DONE")
    except Exception as e:
        logger.error("Inserting values into table birthdays")
        logger.error(str(e))

# Fetches all birthdays from the database, prints out as tuple
def print_birthdays():
    logger.info("Fetching all birthdays")
    print("ID \tNAME \tLASTNAME \tDAY \tMONTH \tYEAR")
    cursor.execute("SELECT * FROM birthdays")
    results = cursor.fetchall()
    for result in results:
        print(result)
    print_seperator()

def print_main_menu():
    print("""
    \t/Main MENU/\n
    1 - add a new birthday
    2 - remove birthday
    3 - check all birthdays
    4 - exit
    """)
    print_seperator()

# Returns true if year is between MIN_YEAR and MAX_YEAR
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

def is_day_valid(month, year, day):
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
        day_count_dict[2] += day_count_dict[2] + 1

    if day <= day_count_dict[month] and day > 0:
        return True
    print("Invalid day")
    return False

def get_user_day(month, year):
    while True:
        day = parse_to_int(input())
        if is_day_valid(month, year, day):
            break
    return day

# Removes birthday from database by inputing ID
def remove_birthday():
    print_birthdays()
    print("Type ID to delete the birthday")
    print("ID: ")
    id = input()
    try:
        logger.info(f"Deleting birthday with ID {id}")
        cursor.execute("DELETE FROM birthdays WHERE ID = (?)", (id,))
        logger.info("DONE")
    except Exception as e:
        logger.error(f"removing birthday with ID {id}")
        logger.error(str(e))

# Checks if any database entries matches with todays day and month.
def check_birthdays():
    day = str(datetime.today().day)
    month = str(datetime.today().month)

    logger.info(f"Fetching birthdays at {day}, {month}")
    try:
        cursor.execute("SELECT name, lastname FROM birthdays WHERE day = ? AND month = ?;", (day, month))
        results = cursor.fetchall()
        logger.info("DONE")
    except Exception as e:
        logger.error(f"Unable to SELECT {day}, {month} FROM birthdays")
        logger.error(str(e))

    birthdays = []

    # Prints matching results
    if results:
        logger.info("TODAYS BIRTHDAYS:")
        for result in results:
            logger.info(f"{result[0]} {result[1]}")
            birthdays.append(f"{result[0]} {result[1]}")
        send_email(birthdays)

def send_email(birthdays):
    try:
        # Creates Multipurpose Internet Mail Extension
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        final_body = body + " "

        for birthday in birthdays:
            final_body += birthday + ", "

        message.attach(MIMEText(final_body, "plain"))

        logger.info(f"connecting to {smtp_server} with port {smtp_port}")
        # Connects to the SMTP server and sends email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, app_password_email)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)

        logger.info("Email has been sent succesfully")
    except Exception as e:
        logger.critical("Unable to send email")
        logger.critical(str(e))

def is_data_none(name, lastname, day, month, year):
    if name == None or lastname == None or day == None or month == None or year == None:
        logger.error(f"Incomplete information for entry in 'birthdays.csv' - {name}, {lastname}, {day}, {month}, {year}")
        return True
    return False

def is_data_valid(day, month, year):
    if not is_day_valid(month, year, day) and not is_month_valid(month) and not is_year_valid(year):
        logger.error(f"Invalid information day - {day}, month - {month}, year - {year}")
        return False
    return True

def read_birthdays_csv():
    delimiter = ","

    logger.info("Opening 'birthdays.csv'")
    with open("birthdays.csv", "r", encoding="UTF-8") as file:
        next(file)
        for line in file:
            birthday_info = line.split(delimiter)
            name = birthday_info[0].strip()
            lastname = birthday_info[1].strip()
            day = parse_to_int(birthday_info[2].strip())
            month = parse_to_int(birthday_info[3].strip())
            year = parse_to_int(birthday_info[4].strip())

            if is_data_none(name, lastname, day, month, year):
                continue

            if not is_data_valid(day, month, year):
                continue

            if not birthday_in_db(name, lastname, day, month, year):
                add_birthday_to_db(name, lastname, day, month, year)
            logger.info("DONE")

def birthday_in_db(name, lastname, day, month, year):
    result = []

    try:
        cursor.execute(f"SELECT id FROM 'birthdays' WHERE (name, lastname, day, month, year) = ('{name}', '{lastname}', {day}, {month}, {year});")
        result = cursor.fetchone()
    except Exception as e:
        logger.error("Unable to check if birthday is in database!")
        logger.error(str(e))
    return result

def print_seperator():
    print("------------------------------")

def parse_to_int(value):
    try:
        return int(value)
    except:
        return -1

# Closes cursors, connection to the database and saves the altered data
def save_db_info():
    logger.info("Saving information to the database")
    try:
        cursor.close()
        connection.commit()
        connection.close()
        logger.info("DONE")
    except Exception as e:
        logger.critical("Unable to save information to the database!")
        logger.critical(str(e))

if __name__ == "__main__":
    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)

    db_name = None
    db_path = dir_path + "\\"

    with open("./logging_config.yaml", "r") as file:
        logging_config = yaml.safe_load(file)

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger("root")

    conf_name = "config.conf"
    conf_path = dir_path + "\\" + conf_name

    logger.info("Loading config values")
    try:
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
        configure = config["setup"]["configure"].lower().strip()
    except Exception as e:
        logger.critical("Loading config file")
        logger.critical(str(e))
        exit(1)

    # Creates or connects to the SQLITE3 database in current directory
    logger.info("Creating connection to the databae")
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        logger.info("DONE")
    except Exception as e:
        logger.critical("Unable to create connection to the database!")
        logger.critical(str(e))

    # Checks if database contains table=birthdays
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='birthdays'")
    results = cursor.fetchone()

    if not results:
        logger.critical("Database does not contain table = 'birthdays'")
        logger.critical("Run 'migrations_db.py'")
        exit(1)

    read_birthdays_csv()

    # If script is in configure mode, prints main menu in terminal, allows user to interact
    if configure == "yes":
        while True:
            print_main_menu()
            try:
                user_input = int(input())
                if user_input == 1:
                    get_birthday_data()
                if user_input == 2:
                    remove_birthday()
                if user_input == 3:
                    print_birthdays()
                if user_input == 4:
                    print("Bye")
                    break
            except ValueError as e:
                print("Invalid input!")
    # Automatically checks for matching birthdays and sends email to the receiver
    elif configure == "no":
        check_birthdays()
    else:
        logger.error(f"Incorrect value for configure = {configure} in 'config.conf'")
        logger.error("Accepting 'yes' for configuring the application or 'no' for checking for birthdays and sending email!")

    save_db_info()
    logger.info("Closing application")
