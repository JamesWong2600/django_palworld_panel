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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def download_file_view(request):
    file_name = request.POST['file']
    print("downloaded " +file_name)
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
    print(file_name+ " file name")
    try:
        if os.path.isdir(file_path):
            # Create a zip file of the folder
            zip_file_path = file_path + '.zip'
            shutil.make_archive(file_path, 'zip', file_path)
            return FileResponse(open(zip_file_path, 'rb'), as_attachment=True, filename=os.path.basename(zip_file_path))
        else:
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    except FileNotFoundError:
        raise Http404("File not found")
    except PermissionError:
        return HttpResponse("Permission denied", status=403)