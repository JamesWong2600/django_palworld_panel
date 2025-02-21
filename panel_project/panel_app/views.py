from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.http import HttpResponse
import zipfile
import os
from django.conf import settings
import random
import string
import redis
import shutil
from py_class.file_option import  edit_file, delete_file, rename_file
from py_class.start_or_close_server import execute_exe
from py_class.read_palworld_config.get_config import get_config_data, read_all_text
import ast
import sqlite3
from configparser import ConfigParser
from py_class.servers.check_server import check_server
from py_class.users_information.account import account
from py_class.servers.config_settings.config_settings import *

account()
check_server()

def update_settings(request, file_path, section, value, new_name, content):
    edit_file(file_path, new_content=None)
    delete_file(file_path)
    download_file(file_path)
    rename_file(file_path, new_name)
    change_server_settings(request)
    create_new_file(file_path, content)
    remove_file(file_path)
    write_string_to_first_line(file_path, content)
    write_string_to_second_line(file_path, content)
    write_all_text(file_path, section, value)
    server_settings(request)
    read_all_text(file_path)
    write_all_text(file_path)


conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)






def edit_file_view(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90','server', file_name)
    if request.method == 'POST':
        new_content = request.POST['file_content']
        edit_file(file_path, new_content)
        return redirect('file_uploaded')
    else:
        file_content = edit_file(file_path)
        return render(request, 'edit_file.html', {'file_name': file_name, 'file_content': file_content})
    
def delete_file_view(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90','server',file_name)
    delete_file(file_path)
    return redirect('file_uploaded')

def download_file_view(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90','server', file_name)
    return FileResponse(open(file_path, 'rb'))

def rename_file_view(request, file_name):
    if request.method == 'POST':
        new_name = request.POST['new_name']
        file_path = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90','server', file_name)
        rename_file(file_path, new_name)
        return redirect('file_uploaded')
    return render(request, 'rename_file.html', {'file_name': file_name})    
    
def list_folders(directory):
    folders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) or os.path.isfile(item_path):
            folders.append(item_path)
    return folders


def generate_random_string(length=12):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def main_page(request):
    cursor = server_conn.cursor()
    cursor.execute('SELECT * FROM servers')
    rows = cursor.fetchall()
    print(str(rows))
    if str(rows) == "[]":
        return render(request, 'main.html')
    return HttpResponse('already have a server')

def login_account(request):
    username = request.POST['username']
    password = request.POST['password']
    ip = get_client_ip(request)
    cursor = account_conn.cursor()
    update_cursor = account_conn.cursor()
    cursor.execute('SELECT * FROM accounts where username = ? and password = ?', (username, password))
    update_cursor.execute('''UPDATE accounts SET ip_address = ? WHERE username = ? and password = ?''', (ip, username, password))
    account_conn.commit()
    rows = cursor.fetchall()
    
    if str(rows) == "[]":
        error = 'username or password is incorrect'
        return render(request, 'login.html', {'error': error})
    else:
        return redirect('main')
        
    
def file_uploaded(request):
    server_file_path = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90', 'server')
    print(server_file_path)
    server_file_path_branch = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90', '8Pd0j4fKCO90')
    server_file_path2 = server_file_path.replace(server_file_path_branch, '')
    print(server_file_path2)
    folders = list_folders(server_file_path)
    folders2 = []
    for fold in folders:
        fold = fold.replace(server_file_path+"\\", '')
        folders2.append(fold)
    return render(request, 'file-uploaded.html', {'files': folders2})

def register(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    ip = get_client_ip(request)
    confirm_password = request.POST['confirm_password']
    if password == confirm_password:
        cursor = account_conn.cursor()
        cursor.execute('''
        INSERT INTO accounts (username, email, password, ip_address, login_status)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password, ip, '1'))
        account_conn.commit()
        return redirect('main')
    else:
        return render(request, 'register.html')
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def upload_file(request):
    file = request.FILES['file']
    servername = request.POST['servername']
    filename = None
    subdirectory = generate_random_string()
    print(settings.MEDIA_ROOT)
    print(subdirectory)
    server_file_path = os.path.join(settings.MEDIA_ROOT, subdirectory, servername)
    backup_zip_path = os.path.join(settings.MEDIA_ROOT, subdirectory, 'backup')
    os.makedirs(server_file_path, exist_ok=True)
    os.makedirs(backup_zip_path, exist_ok=True)
    fs = FileSystemStorage(location=backup_zip_path)
    if file:
        filename = file.name
        if filename.__contains__(".zip"):
           fs.save(file.name, file)
           file_path = fs.path(file.name)
           with zipfile.ZipFile(file_path, 'r') as zip_ref:
               cursor = server_conn.cursor()
               cursor.execute('''
                INSERT INTO servers (file_name, server_name, server_id)
                VALUES (?, ?, ?)
            ''', (filename, servername, subdirectory))
               zip_ref.extractall(server_file_path)
               print(filename)
               return redirect('file_uploaded')

          
        else:
          return HttpResponse('please upload a zip file')
    else:
        return HttpResponse('Failed to upload file')
    

def start_or_close_server(request):
    exe_path = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90', 'server', 'PalServer.exe')
    execute_exe(exe_path)
    return HttpResponse('sucessfully started or closed the server')

def server_control(request):
    return render(request, 'start_or_close_server.html')

def execute_exe_view(request, file_name):
    exe_path = os.path.join(settings.MEDIA_ROOT,'8Pd0j4fKCO90', 'server', 'PalServer.exe')
    stdout, stderr = execute_exe(exe_path)
    return render(request, 'execute_exe.html', {'file_name': file_name, 'stdout': stdout, 'stderr': stderr})