import os
from configparser import ConfigParser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def print_seperator():
    print("--------------------")

print("Email sending test")

print_seperator()
print("Checking if config file exists")
assert os.path.isfile("config.conf") == True
print("DONE")
print_seperator()

# Loads config from 'config.conf'
config = ConfigParser()
config.read("config.conf")

print("Checking if config contains necessary SMTP information")
# Checks if config contains option sender_email
assert config.has_option("smtp", "sender_email") == True
# Checks if config contains value for sender_email
assert (config.get("smtp", "sender_email") != "") == True

assert config.has_option("smtp", "app_password_email") == True
assert (config.get("smtp", "app_password_email") != "") == True

assert config.has_option("smtp", "receiver_email") == True
assert (config.get("smtp", "receiver_email") != "") == True

assert config.has_option("smtp", "smtp_server") == True
assert (config.get("smtp", "smtp_server") != "") == True

assert config.has_option("smtp", "smtp_port") == True
assert (config.get("smtp", "smtp_port") != "") == True

print("DONE")
print_seperator()

print("Checking if server and port are working ")
smtp_server = config.get("smtp", "smtp_server")
smtp_port = config.get("smtp", "smtp_port")
with smtplib.SMTP(smtp_server, smtp_port) as server:
    print("DONE")
    print_seperator()

    print("Checking if server supports TLS")
    # Tries to start TLS for email server
    assert server.starttls() == True
    print("DONE")

    print_seperator()
    print("Checking if login is successfull")
    sender_email = config.get("smtp", "sender_email")
    app_password_email = config.get("smtp", "app_password_email")
    assert server.login(sender_email, app_password_email) == True
    print("DONE")

    # Create Multi Part object for email
    message = MIMEMultipart()
    message["From"] = "root"
    message["To"] = config.get("smtp", "receiver_email")
    message["Subject"] = "This is a test message!"
    message.attach(MIMEText("Test message", "plain"))

    print_seperator()
    print("Sending email")
    receiver_email = config.get("smtp", "receiver_email")
    text = message.as_string()
    # Sends email
    assert server.sendmail(sender_email, receiver_email, text) == True
    print("DONE")
    print_seperator()
