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
#import stat
#import subprocess
#import pyautogui
#from PIL import Image
import threading
from py_class.file_option import  edit_file, delete_file, rename_file
from py_class.start_or_close_server import execute_exe
from py_class.read_palworld_config.get_config import get_config_data, read_all_text
from configparser import ConfigParser
from py_class.servers.check_server import check_server
from py_class.users_information.account import account
from py_class.servers.config_settings.config_settings import *
from py_class.users_information.register.register import register
from py_class.users_information.login.login_and_logout import login_account, logout
from py_class.file_access.edit_file import *
from py_class.file_access.delete_file import *
from py_class.file_access.download_file import *
from py_class.file_access.rename_file import *
from py_class.server_control.server_control import *
import time
import sys
import select
#import pytesseract
#from pywinauto import findwindows, Desktop
#import uiautomation as auto
import keyboard
import pyperclip
#from pywinauto import Application
#from pywinauto import *
from PIL import ImageGrab
#import pywinauto
#from pywinauto.findwindows import find_windows
#from queue import Queue, Empty
import psutil
from django.http import JsonResponse
from py_class.backup.backup_sql_initial import *
from datetime import datetime

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

def file_acesss(request, file_name):
    edit_file_view(request)
    save_edit(request)
    delete_file_view(request)
    download_file_view(request)
    rename_file_view(request, file_name)
    send_rename(request)
    file_uploaded_rename(request)

def server_controller(request, process_name):
    get_client_ip(request)
    get_exe(request)
    server_control(request)
    execute_exe(request)
    get_usage(request)
    get_process_ram_usage(process_name)
    get_process_cpu_usage(process_name)
    get_total_ram_size()
    open_server()
    close_server()
    get_exe_core(request)
      
servers_backup_create_table()


conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)
servers_backup = sqlite3.connect('servers_backup.db', check_same_thread=False)


def download_backup(request):
    ip = get_client_ip(request)
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    print(username+ " name")
    #server_cursor = server_conn.cursor()
    #server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    #for rowrow in server_cursor.fetchall():
    #    server_id = rowrow[0]
    #    servername = rowrow[1]
    backup_cursorr = servers_backup.cursor()  
    backup_cursorr.execute(f"SELECT server_id, server_name, time_created FROM servers_backup where username = '{username}'")
    server_id_list = []
    server_name_list = []
    time_created_list = []
    for rowss in backup_cursorr.fetchall():
      server_id = rowss[0]
      server_name = rowss[1]
      time_created = rowss[2]
      server_id_list.append(server_id)
      server_name_list.append(server_name)
      time_created_list.append(time_created)
      if server_id:
         print(server_id)
         print(server_name)
         print(time_created)
    combined_list = zip(server_id_list, server_name_list, time_created_list)
    post_server_name = request.POST.get('server_name')
    post_server_id = request.POST.get('server_id')
    post_time_created = request.POST.get('time_created')
    file_name = f"{post_server_name}_{post_time_created}.zip"
    print("my file name is "+file_name)
    print("my server id is "+str(post_server_id))
    file_path = os.path.join(settings.MEDIA_ROOT, str(post_server_id), 'backup', file_name)
    print("yes nice")
    if os.path.exists(file_path):
        print("yes nice")
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    






def backup_action(request):
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
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y_%m_%d__%H_%M_%S")
    backup_cursorr = servers_backup.cursor()  
    backup_cursorr.execute('''INSERT INTO servers_backup (username, server_id, server_name, time_created) VALUES (?, ?, ?, ?)''', (username, server_id, servername, formatted_time))
    servers_backup.commit()
    backup_cursorr = servers_backup.cursor()  
    backup_cursorr.execute(f"SELECT server_id, server_name, time_created FROM servers_backup where username = '{username}'")
    server_id_list = []
    server_name_list = []
    time_created_list = []
    for rowss in backup_cursorr.fetchall():
      server_id = rowss[0]
      server_name = rowss[1]
      time_created = rowss[2]
      server_id_list.append(server_id)
      server_name_list.append(server_name)
      time_created_list.append(time_created)
      if server_id:
         print(server_id)
         print(server_name)
         print(time_created)
    combined_list = zip(server_id_list, server_name_list, time_created_list)
    print(os.path.join(settings.MEDIA_ROOT, server_id, 'backup'))
    print(os.path.join(settings.MEDIA_ROOT, server_id, server_name))
    #print(os.path.join(settings.MEDIA_ROOT, server_id, servername,f"{servername}_{formatted_time}"))
    #f"{servername}_{formatted_time}"
    shutil.make_archive(os.path.join(settings.MEDIA_ROOT, server_id, "backup", f"{servername}_{str(formatted_time)}"), "zip",
                         os.path.join(settings.MEDIA_ROOT, server_id,  server_name))
    return render(request, 'backup_page.html', {'combined_list': combined_list})



def backup_page(request):
    ip = get_client_ip(request)
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    print(username+ " name")
    #server_cursor = server_conn.cursor()
    #server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    #for rowrow in server_cursor.fetchall():
        #server_id = rowrow[0]
        #servername = rowrow[1]
    backup_cursorr = servers_backup.cursor()
    backup_cursorr.execute(f"SELECT server_id, server_name, time_created FROM servers_backup where username = '{username}'")
    for rowss in backup_cursorr.fetchall():
        server_id = rowss[0]
        server_name = rowss[1]
        time_created = rowss[2]
        if server_id:    
            print(server_id)
            print(server_name)
            print(time_created)
    return render(request, 'backup_page.html')
    

    






    
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
    server_cursor = server_conn.cursor()
    user_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in user_cursor.fetchall():
        username = row[0]
    server_cursor.execute(f"SELECT * FROM servers where owner = '{username}'")
    server = "[]"
    for rows in server_cursor.fetchall():
        server = rows[0]
    if server == "[]":
        return render(request, 'main.html',{'username': username})
    else:
        return render(request, 'main.html',{'server': server, 'username': username})


        
    
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



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

