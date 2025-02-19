import mysql.connector
from django.conf import settings
from configparser import ConfigParser
import os

def get_config_data():
    config = ConfigParser()
    config.read(os.path.join(settings.CONFIG, 'mysql', 'sql_config.ini'))
    print("runned sucessfully")
    db_config = {
        'host': config.get('database', 'host'),
        'user': config.get('database', 'user'),
        'password': config.get('database', 'password'),
        'database': config.get('database', 'database')
    }
    mydb = mysql.connector.connect(**db_config)
    print("runned sucessfully")
    return mydb
          
def read_all_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def read_all_text(file_path):
    with open(file_path, 'w') as file:
        return file.write()


