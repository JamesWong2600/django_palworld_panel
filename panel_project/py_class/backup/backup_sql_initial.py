from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.http import HttpResponse, Http404
import zipfile
import os
from django.conf import settings
import random
import string
import redis
import shutil
import ast
import sqlite3

"""servers_backup = sqlite3.connect('servers_backup.db', check_same_thread=False)

def servers_backup_create_table():
    user_account_conn = sqlite3.connect('servers_backup.db', check_same_thread=False)
    cursor = user_account_conn.cursor()
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS servers_backup(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    server_id TEXT NOT NULL,
    server_name TEXT NOT NULL,
    time_created TEXT NOT NULL     
    )
    ''')"""