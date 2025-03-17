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
from io import BytesIO
from zipfile import ZipFile

conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)

# get the client ip address
# 獲取用戶端IP地址
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# users can download the files from the file explorer
# 用戶可以下載文件
def download_file_view(request):
    file_name = request.POST['file']
    ip = get_client_ip(request)
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    for rowrow in server_cursor.fetchall():
        server_id = rowrow[0]
        servername = rowrow[1]
    file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, file_name)
    try:
        if os.path.isdir(file_path):
            # Create a zip file of the folder
            #zip_file_path = file_path + '.zip'
            #print(" file name "+file_path)
            #shutil.make_archive(file_path, 'zip', file_path)
            zip_buffer = create_zip_in_memory(file_path)
            return FileResponse(zip_buffer, as_attachment=True, filename=os.path.basename(file_path)+".zip")
        else:
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    except FileNotFoundError:
        raise Http404("File not found")
    except PermissionError:
        return HttpResponse("Permission denied", status=403)

#the zip file will be created in memory
#zip文件將在內存中創建
def create_zip_in_memory(directory_path):
    # Create BytesIO object
    in_memory_zip = BytesIO()
    
    # Create ZipFile object
    with ZipFile(in_memory_zip, 'w') as zipf:
        # Walk through directory
        for foldername, subfolders, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname)
    
    # Reset file pointer
    in_memory_zip.seek(0)
    return in_memory_zip    