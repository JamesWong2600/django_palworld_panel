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
import stat


conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)

def read_all_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def write_all_text(file_path):
    with open(file_path, 'w') as file:
        return file.write()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def edit_file_view(request):
    file_name = request.POST['file']
    ip = get_client_ip(request)
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    print(username+ " name")
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    for rowrow in server_cursor.fetchall():
        server_id = rowrow[0]
        servername = rowrow[1]
    file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, file_name)
    content = read_all_text(file_path)
    return render(request, 'edit_file_view.html', {'file_name': file_name, 'content': content})


def save_edit(request):
    file_name = request.POST['file_name']
    content = request.POST['content']
    ip = get_client_ip(request)
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    print(username+ " name")
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    for rowrow in server_cursor.fetchall():
        server_id = rowrow[0]
        servername = rowrow[1]
    if not file_name.endswith('.txt'):
        new_file_name = file_name + '.txt'
        old_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, file_name)
        new_file_name = os.path.join(settings.MEDIA_ROOT, server_id, servername, new_file_name)
        os.rename(old_file_path, new_file_name)
        with open(new_file_name, 'w') as file:
            file.write(content)
        with open(new_file_name, 'r') as file:
            print(file.read())
        os.rename(new_file_name, old_file_path)    
    else:
        with open(new_file_name, 'w') as file:
            file.write(content)
        with open(new_file_name, 'r') as file:
            print(file.read())
    return redirect('file_uploaded')