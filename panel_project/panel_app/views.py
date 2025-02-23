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
from py_class.file_option import  edit_file, delete_file, rename_file
from py_class.start_or_close_server import execute_exe
from py_class.read_palworld_config.get_config import get_config_data, read_all_text
import ast
import sqlite3
from configparser import ConfigParser
from py_class.servers.check_server import check_server
from py_class.users_information.account import account
from py_class.servers.config_settings.config_settings import *
from py_class.users_information.register.register import register
from py_class.users_information.login.login_and_logout import login_account, logout
import stat
import shutil


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

def authentication(request):
    register(request)
    logout(request)
    login_account(request)

conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)






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

    
def delete_file_view(request):
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
    os.chmod(file_path, stat.S_IWRITE)
    delete_file(file_path)
    return redirect('file_uploaded')

def download_file_view(request, file_name):
    file_name = request.GET['file']
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


def rename_file_view(request, file_name):
    ip = get_client_ip(request)
    print(file_name)
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
    file_path = os.path.join(settings.MEDIA_ROOT, server_id , servername)
    rename_file(file_path, file_name)
    return render(request, 'rename_file_view.html', {'file_name': servername})



def rename_file(file_path, new_name):
    if os.path.exists(file_path):
        print(file_path)
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)
    
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
    ip = get_client_ip(request)
    user_cursor = account_conn.cursor()
    print(ip)
    cursor = server_conn.cursor()
    user_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    rows = cursor.fetchall()
    for row in user_cursor.fetchall():
        username = row[0]
    cursor.execute(f"SELECT * FROM servers where owner = '{username}'")
    print(username)
    if str(rows) == "[]":
        return render(request, 'main.html',{'username': username})
    else:
        return HttpResponse('already have a server')


        
    
def file_uploaded(request):
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
    print(server_id)
    print(servername)
    server_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername)
    print(server_file_path)
    #server_file_path_branch = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90', '8Pd0j4fKCO90')
    #server_file_path2 = server_file_path.replace(server_file_path_branch, '')
    print(server_file_path)
    folders = list_folders(server_file_path)
    folders2 = []
    for fold in folders:
        fold = fold.replace(server_file_path+"\\", '')
        folders2.append(fold)
    files = [(folder, folder, "a") for folder in folders2]   
    return render(request, 'file-uploaded.html', {'files': files})


def file_uploaded_rename(request):
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
    print(server_id)
    print(servername)
    server_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername)
    print(server_file_path)
    #server_file_path_branch = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90', '8Pd0j4fKCO90')
    #server_file_path2 = server_file_path.replace(server_file_path_branch, '')
    print(server_file_path)
    folders = list_folders(server_file_path)
    folders2 = []
    for fold in folders:
        fold = fold.replace(server_file_path+"\\", '')
        folders2.append(fold)
    files = [(folder, folder, "b") for folder in folders2]
    return render(request, 'file-uploaded.html', {'files': files})

def send_rename(request):
    ip = get_client_ip(request)
    new_file_name = request.POST['new_file_name']
    original_file_name = request.POST['original_file_name']
    print(original_file_name + " original")
    print(new_file_name + " new")
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
    server_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername)
    os.rename(os.path.join(server_file_path, original_file_name), os.path.join(server_file_path, new_file_name))
    print(server_id)
    print(servername)
    print(server_file_path)
    #server_file_path_branch = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90', '8Pd0j4fKCO90')
    #server_file_path2 = server_file_path.replace(server_file_path_branch, '')
    print(server_file_path)
    folders = list_folders(server_file_path)
    folders2 = []
    for fold in folders:
        fold = fold.replace(server_file_path+"\\", '')
        folders2.append(fold)
    files = [(folder, folder, 'a') for folder in folders2]
    return render(request, 'file-uploaded.html', {'files': files})

    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def upload_file(request):
    ip = get_client_ip(request)
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    print(username)
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
                INSERT INTO servers (file_name, server_name, server_id, owner)
                VALUES (?, ?, ?, ?)
            ''', (filename, servername, subdirectory, username))
               server_conn.commit()
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