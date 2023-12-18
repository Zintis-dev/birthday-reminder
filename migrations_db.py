import logging, logging.config
import yaml
import os
import time
from datetime import datetime
from configparser import ConfigParser
import sqlite3

with open("./logging_migrations_config.yaml", "r") as file:
    logging_config = yaml.safe_load(file)

logging.config.dictConfig(logging_config)

logger = logging.getLogger("root")

logging.info("Loading config values")
try:
    config = ConfigParser()
    config.read("config.conf")
    db_name = config["setup"]["db_name"]
except Exception as e:
    logger.critical("Unable to load config file")
    logger.critical(str(e))
    exit()
logger.info("Done")

logger.info("Creating connection to to database")
try:
    connection = sqlite3.connect(f"{db_name}.db")
    cursor = connection.cursor()
except Exception as e:
    logging.critical("Unable to establish connection to the database")
    logging.critical(str(e))
logger.info("DONE")

def check_if_table_exists(table_name):
    logger.info(f"Checking if table with name = {table_name} exists")
    results = []

    try:
        result = cursor.execute(f"SHOW TABLES LIKE {str(table_name)}")
        results = cursor.fetchall()
    except Exception as e:
        logging.error(f"Unable to show tables like {str(table_name)}")
        logging.error(str(e))
        pass
    logger.info("DONE")
    return results

def create_migrations_table():
    logger.info("Creating migrations table")
    result = []

    try:
        result = cursor.execute("CREATE TABLE IF NOT EXISTS 'migrations'('id' INTEGER PRIMARY KEY AUTOINCREMENT,'name' VARCHAR(255),'exec_ts' INT(10),'exec_dt' VARCHAR(20))")
    except Exception as e:
        logger.error("CREATE TABLE IF NOT EXISTS 'migrations'('id' INTEGER PRIMARY KEY AUTOINCREMENT,'name' VARCHAR(255),'exec_ts' INT(10),'exec_dt' VARCHAR(20))")
        logger.error(str(e))
    logger.info("DONE")
    return result

def check_if_migration_exists(migration_file_name):
    logger.info(f"Checking if migration = {migration_file_name} exists")
    records = []

    try:
        result = cursor.execute(f"SELECT count(*) FROM migrations WHERE 'name' = '{str(migration_file_name)}'")
        records = cursor.fetchall()
    except Exception as e:
        logger.error(f"Unable to verify migration = {migration_file_name} existance")
        logger.error(str(e))
        pass
    logger.info("DONE")
    return records[0][0]

def migration_value_insert(name, exec_ts, exec_dt):
    logger.info("Inserting values into table = migrations")
    try:
        cursor.execute("INSERT INTO 'migrations' ('name', 'exec_ts', 'exec_dt') VALUES (?, ?, ?)", (name, exec_ts, exec_dt))
    except Exception as e:
        logger.error("Unable to insert values into table migrations")
        logger.error(str(e))
        pass

def exec_any_sql(query):
    logger.info(f"Executing query '{query}'")
    status = 0

    try:
        result = cursor.execute(query)
    except Exception as e:
        logger.error(f"Unable to execute query {query}")
        logger.error(str(e))
        status = 1
        pass
    logger.info("DONE")
    return status

create_migrations_table()

migrations_list = []
cur_dir = os.getcwd()
migrations_files_list = os.listdir(cur_dir + "/migrations/")
for file in migrations_files_list:
    if file.endswith(".sql"):
        migrations_list.append(file)

migrations_list.sort(reverse=False)

counter = 0

for migration in migrations_list:
    if check_if_migration_exists(migration) == 0:
        with open(cur_dir + "/migrations/" + migration, "r") as file:
            migration_sql = file.read()
            if exec_any_sql(migration_sql) == 0:
                exec_ts = int(time.time())
                exec_dt = datetime.utcfromtimestamp(exec_ts).strftime("%Y-%m-%d %H:%M:%S")
                migration_value_insert(migration, exec_ts, exec_dt)
                counter += 1
    else:
        logger.error("2")
        break

if counter == 0:
    logger.info("Migrations are up to date!")
else:
    logger.info(f"{counter} migration changes made!")

connection.commit()
cursor.close()
cursor.close()