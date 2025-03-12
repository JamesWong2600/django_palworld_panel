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
from pathlib import Path
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
from django_redis import get_redis_connection
from django.core.cache import cache


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

class DjangoCache:
    def set_value(self, key: str, value: any, timeout=None):
        return cache.set(key, value, timeout)
        
    def get_value(self, key: str, default=None):
        return cache.get(key, default)
        
    def delete_value(self, key: str):
        return cache.delete(key)
    def set_list(self, key: str, value: any, timeout=None):
        if isinstance(value, list):
            value = json.dumps(value)  # Convert list to JSON string
        return cache.set(key, value, timeout)
        
    def get_list(self, key: str, default=None):
        value = cache.get(key, default)
        if isinstance(value, str):
            try:
                return json.loads(value)  # Convert JSON string back to list
            except json.JSONDecodeError:
                return value
        return value
    def delete_list(self, key: str) -> bool:
        return cache.delete(key)

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
    server_directory_path = os.path.join(settings.MEDIA_ROOT, server_id,  server_name)
    output_zip_path = os.path.join(settings.MEDIA_ROOT, server_id, "backup", f"{servername}_{str(formatted_time)}")
    #print(os.path.join(settings.MEDIA_ROOT, server_id, servername,f"{servername}_{formatted_time}"))
    #f"{servername}_{formatted_time}"
    threading.Thread(target=make_zip_of_directory, args=(server_directory_path, output_zip_path)).start()
    return render(request, 'backup_page.html', {'combined_list': combined_list})


def make_zip_of_directory(directory_path, output_zip_path):
    shutil.make_archive(output_zip_path, 'zip', directory_path)


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
    server_id_list = []
    server_name_list = []
    time_created_list = []
    for rowss in backup_cursorr.fetchall():
        server_id = rowss[0]
        server_name = rowss[1]
        time_created = rowss[2]
        if server_id and server_name and time_created:    
            server_id_list.append(server_id)
            server_name_list.append(server_name)
            time_created_list.append(time_created)
    combined_list = zip(server_id_list, server_name_list, time_created_list)        
    return render(request, 'backup_page.html', {'combined_list': combined_list})
    

    






    
def list_folders(directory, file):
    folders_path = []
    directory_boolean = []
    #print("directory is "+directory)
    #print("file is "+str(file))
    if file == None:
        directory = str(directory).replace("\\"+str(file), '')
        print("directory is "+directory)
    if os.path.isdir(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                if file == None:
                    folders_path.append(item_path)
                    #print("item path is : "+item_path)
                    #base_path.append(item_path)
                else:
                    folders_path.append(str(file)+"\\"+item_path)
                    print("item path is : "+item_path)
                    #base_path.append(item_path)
                directory_boolean.append("yes")
            else:    
                if file == None:
                    folders_path.append(item_path)
                    print("item path is : "+item_path)
                else:
                    folders_path.append(str(file)+"\\"+item_path)
                directory_boolean.append("no")
        return folders_path, directory_boolean, #base_path
    else:
        return directory, "no"


def generate_random_string(length=12):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def login_view(request):
    cache.set('key', 'value112233')
    print(cache.get('key'))
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def main_page(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    if not login_status == "true":
        return redirect('login')
    else:
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

"{% url 'file_uploaded_with_parameter' parameter=file %}"
"{% url 'file_uploaded_with_parameter' parameter=file %}"
"{% url 'upload_file'  %}"
def file_uploaded_with_parameter(request):
    #print("the args is "+args)
    current_url = request.build_absolute_uri()
    current_url = current_url.split('http://127.0.0.1:8000/',1)[1]
    url_path_items = current_url.split('/')
    print("Current URL is:", current_url)
    print("URL Path Items are:", url_path_items)
    #print("param is "+params)
    #args = params.split('/')
    slash_count = current_url.count('/')
    #print("arg is " +str(args))
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
    directory = None    
    if slash_count == 2:   
        directory = os.path.join(settings.MEDIA_ROOT,server_id, servername, url_path_items[1])
    if slash_count == 3:   
        directory = os.path.join(settings.MEDIA_ROOT,server_id, servername, url_path_items[1], url_path_items[2])
    if not os.path.exists(directory):
        return HttpResponse("Directory does not exist")
    if os.path.isdir(directory):
        print(directory)
        folders = list_folders(directory)
        folders2 = []
        for fold in folders:
            fold = fold.replace(directory+"\\", '')
            folders2.append(fold)
            files = [(folder, folder, "a") for folder in folders2]   
            return render(request, 'file-uploaded.html', {'files': files})
    else:
        file_name = request.POST['file']
       # print("downloaded " +file_name)
        content = read_all_text(directory)
        return render(request, 'edit_file_view.html', {'file_name': file_name, 'content': content})
    
    #revious_url = request.META.get('HTTP_REFERER', '/')
    #print(previous_url)
    #substring =''
    #if '/file_uploaded/' in previous_url:
    #    substring = str(previous_url).split('/file_uploaded/')[1]
    #elif '/edit_file_view/' in previous_url:
    #    substring = str(previous_url).split('/edit_file_view/')[1]
    #elif 'edit_file_view/' in previous_url:
    #    substring = f"engine\\{file_name}"
    #print(substring)    



def append_to_url(request, *args):
    new_segment = request.GET.get('new_segment')
    if new_segment:
        new_url = "/file-uploaded/" + "/".join(args) + f"/{new_segment}/"
        return redirect(new_url)
    else:
        return HttpResponse("New segment not provided")
    
def file_explorer_view(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    if not login_status == "true":
        return redirect('login')
    else:
        file = request.POST.get('file')
        #action = request.POST.get('action')
        print("file are "+str(file))
        cache_service = DjangoCache()
        #if not file == None:
            #cache_service.set_value(ip, file)   
        #print("Cached value is:", cached_value)
        update_cursor = account_conn.cursor()
        update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
        username = update_cursor.fetchone()[0]
        server_cursor = server_conn.cursor()
        server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
        server_id, servername = server_cursor.fetchone()
        directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, str(file))
        print("Directory:", directory)
        folders, directory_boolean = list_folders(directory, file)
        folders2 = [fold.replace(directory+"\\", '') for fold in folders]
        folder_paths = [folder for folder in folders2]  # Original path
        folder_names = [Path(folder).name for folder in folders2]  # Same name for display
        folder_types = ["a" for folder in folders2]  # Type of file
        #print("folder_types is:", folder_types)
        if file == None:
            cache_service.set_list(ip, folder_paths)

        elif not file == None:
            folder_paths = cache_service.get_list(ip)
            cache_service.delete_list(ip)
            print("cache_paths is:", folder_paths)
        files = zip(folder_paths , folder_names, folder_paths, folder_types, directory_boolean)
        return render(request, 'file-uploaded.html', {'files': files})  
    

    


def open_or_edit_file_view_base(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
        action = 0
        file = request.POST.get('file')
        base_file = request.POST.get('base_name')
        print("file yiis "+str(base_file))
        #action = request.POST.get('action')
        print("file arrres "+str(file))
        if file == None or base_file == None:
            file = cache.get(ip+'edit_file')
            base_file = cache.get(ip+'edit_base')
            action = 1
        else:
            cache.set(ip+'edit_file', file)
            cache.set(ip+'edit_base', base_file)
        print("basefile is "+str(base_file))
        #action = request.POST.get('action')
        print("file ares "+str(file))
        update_cursor = account_conn.cursor()
        update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
        username = update_cursor.fetchone()[0]
        server_cursor = server_conn.cursor()
        server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
        server_id, servername = server_cursor.fetchone()
        directory = os.path.join(file)
        if action == 0:
                if os.path.isdir(directory):
                    folders, directory_boolean = open_or_edit_file_view_list_folders(file, base_file)
                    folders2 = [fold.replace(directory+"\\", '') for fold in folders]
                    print("folders is:", folders)
                    #folder_paths = [Path(folder).name for folder in folders] 
                    folder_paths = [folder for folder in folders]  # Original path
                    folder_names = [Path(folder).name for folder in folders2]  # Same name for display
                    folder_types = ["a" for folder in folders2]  # Type of file
                    print("folder_types ifff:", folder_types)
                    cache_service = DjangoCache()
                    print("folder_paths is:", folder_paths)
                    cache_service.set_list(ip, folder_paths)
                    folder_paths = cache_service.get_list(ip)
                    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa"+str(folder_paths))
                    files = zip(folder_paths, folder_names, folder_paths, folder_types, directory_boolean)
                    if os.path.isdir(directory):
                        return render(request, 'file-uploaded.html', {'files': files})  
                    """ return render(request, 'file-uploaded.html', {
                        'files': files,
                        'redirect_url': 'file_explorer'
                    }) """

                else:
                    content = read_all_text(directory)
                    return render(request, 'edit_file_view.html', {'file_name': file, 'content': content, 'base_name': base_file})
        else:
            content = rf"{request.POST.get('content')}"
            print("content is "+str(content))
            processed_content = remove_empty_lines(content)
            if not file.endswith('.txt'):
                new_file_name = file + '.txt'
                old_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, file)
                print("old file path is "+old_file_path)
                new_file_name = os.path.join(settings.MEDIA_ROOT, server_id, servername, new_file_name)
                os.rename(old_file_path, new_file_name)
                with open(new_file_name, 'w') as filess:
                    filess.write(processed_content) 
                    print("weittedddddddddddddddddddddddddddddd")
                with open(new_file_name, 'r') as filess:
                    print(filess.read())
                os.rename(new_file_name, old_file_path)    
            else:
                with open(new_file_name, 'w') as filess:
                    filess.write(processed_content)
                with open(new_file_name, 'r') as filess:
                    print(filess.read())  
            gfolders, gdirectory_boolean = edit_return_list_folders(file, base_file)
            gfolders2 = [fold.replace(directory+"\\", '') for fold in gfolders]
            print("folders is:", gfolders)
            #folder_paths = [Path(folder).name for folder in folders] 
            gfolder_paths = [gfolder for gfolder in gfolders]  # Original path
            gfolder_names = [Path(gfolder).name for gfolder in gfolders2]  # Same name for display
            gfolder_types = ["a" for folder in gfolders2]  # Type of file
            # print("folder_types ifff:", folder_types)
            #cache_service = DjangoCache()
            #print("folder_paths is:", folder_paths)
            #cache_service.set_list(ip, folder_paths)
            #folder_paths = cache_service.get_list(ip)
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa"+str(gfolder_paths))
            gfiles = zip(gfolder_paths, gfolder_names, gfolder_paths, gfolder_types, gdirectory_boolean)
            return render(request, 'file-uploaded.html', {'files': gfiles})  
        
def remove_empty_lines(text):
    # Split text into lines and filter out empty lines while preserving indentation
    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    # Rejoin lines with newline character
    return '\n'.join(non_empty_lines)       
   

def edit_return_list_folders(directory, file):
    folders_path = []
    directory_boolean = []
    directory = directory.replace("\\"+file, '')
    print("directory is "+directory)
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        print("item path is a: "+item_path)
        if os.path.isdir(item_path):
            folders_path.append(item_path)
            print("item path is b: "+item_path)
            #base_path.append(item_path)
            directory_boolean.append("yes")
        else:    
            folders_path.append(item_path)
            print("item path is c: "+item_path)
            #folders_path.append(str(file)+"\\"+item_path)
            directory_boolean.append("no")
    return folders_path, directory_boolean


def open_or_edit_file_view_list_folders(directory, file):
    folders_path = []
    directory_boolean = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        print("item path is b : "+item_path)
        if os.path.isdir(item_path):
            folders_path.append(item_path)
            print("item path is : "+item_path)
            #base_path.append(item_path)
            directory_boolean.append("yes")
        else:    
            folders_path.append(item_path)
            print("item path is : "+item_path)
            folders_path.append(str(file)+"\\"+item_path)
            directory_boolean.append("no")
    return folders_path, directory_boolean, #base_path
"""def open_or_edit_file_view_base(request):
    file = request.POST.get('file')
    #action = request.POST.get('action')
    print("file is "+str(file))
    ip = get_client_ip(request)
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    username = update_cursor.fetchone()[0]
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    server_id, servername = server_cursor.fetchone()
    directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, str(file))
    if file == "Engine":
       directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, str(file))
    elif file == "Binaries":
       directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, "Engine", "Binaries") 
    elif file == "Content":
       directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, "Engine", "Content") 
    elif file == "Programs":
       directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, "Engine", "Programs")  
    elif file == "Saved":
       directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, "Engine", "Saved")
    elif file == "ThirdParty":
       directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, "Engine", "Binaries", "ThirdParty")  
    elif file == "ThirdParty":
       directory = os.path.join(settings.MEDIA_ROOT, server_id, servername, "Engine", "Binaries", "ThirdParty")        
    #for root, dirs, _ in os.walk(os.path.join(settings.MEDIA_ROOT, server_id, servername)):
    #  if file in dirs:
    #     directory = os.path.join(root, file)        
    #print("Directory:", directory)
    folders, directory_boolean = list_folders(directory, file)
    folders2 = [fold.replace(directory+"\\", '') for fold in folders]
#folder_paths = [Path(folder).name for folder in folders] 
    folder_paths = [folder for folder in folders2]  # Original path
    folder_names = [Path(folder).name for folder in folders2]  # Same name for display
    folder_types = ["a" for folder in folders2]  # Type of file
    print("folder_types is:", folder_types)
    files = zip(folder_paths, folder_names, folder_paths, folder_types, directory_boolean)
    if os.path.isdir(directory):
        return render(request, 'file-uploaded.html', {'files': files})
    else:
        content = read_all_text(folders)
        return render(request, 'edit_file_view.html', {'file_name': file, 'content': content})"""



def file_uploaded_base(request):
    ip = get_client_ip(request)
    file = request.POST.get('file')
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    username = update_cursor.fetchone()[0]
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    server_id, servername = server_cursor.fetchone()
    directory = os.path.join(settings.MEDIA_ROOT, server_id, servername)
    #print("Directory:", directory)
    directory = os.path.join(directory)
    folders, directory_boolean = list_folders(directory, file)
    #print("base_path is:", base_path)
    folders2 = [fold.replace(directory+"\\", '') for fold in folders]
    folder_paths = [Path(folder).name for folder in folders] 
    print("the path is" + str(folder_paths))
    folder_names = [folder for folder in folders2]  # Same name for display
    folder_types = ["a" for folder in folders2]  # Type of file
    files = zip(folder_paths, folder_names, folder_paths, folder_types, directory_boolean)
    return render(request, 'file-uploaded.html', {'files': files})


def file_uploaded(request, file1):
    ip = get_client_ip(request)
    #path = request.GET.get('path')
    print("Path is:", file1)
    # Get username
    update_cursor = account_conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    username = update_cursor.fetchone()[0]
    
    # Get server info
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    server_id, servername = server_cursor.fetchone()
    
    # Build directory path
    directory = os.path.join(settings.MEDIA_ROOT, server_id, servername)
    print("Directory:", directory)
    if file1:
        directory = os.path.join(directory, file1)
        
    # List folders and files
    folders = list_folders(directory)
    folders2 = [fold.replace(directory+"\\", '') for fold in folders]
    files = [(folder, folder, "a") for folder in folders2]
    
    return render(request, 'file-uploaded.html', {'files': files})    
'''def file_uploaded(request, *args):
    file = request.GET.get('file')
    print("Arguments:", args)
    print("file is "+str(file))
    current_url = request.build_absolute_uri()
    current_url = current_url.split('http://127.0.0.1:8000/',1)[1]
    url_path_items = current_url.split('/')
    print("Current URL is:", current_url)
    print("URL Path Items are:", url_path_items)
    #print("param is "+params)
    #args = params.split('/')
    slash_count = current_url.count('/')
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
    directory = None 
    if slash_count == 1:    
        directory = os.path.join(settings.MEDIA_ROOT, server_id, servername)  
    if slash_count == 2:   
        directory = os.path.join(settings.MEDIA_ROOT,server_id, servername, url_path_items[1])
    if slash_count == 3:   
        directory = os.path.join(settings.MEDIA_ROOT,server_id, servername, url_path_items[1], url_path_items[2])
    #server_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername)
    print(directory)
    #server_file_path_branch = os.path.join(settings.MEDIA_ROOT, '8Pd0j4fKCO90', '8Pd0j4fKCO90')
    #server_file_path2 = server_file_path.replace(server_file_path_branch, '')
    print(directory)
    folders = list_folders(directory)
    folders2 = []
    for fold in folders:
        fold = fold.replace(directory+"\\", '')
        folders2.append(fold)
    files = [(folder, folder, "a") for folder in folders2]   
    return render(request, 'file-uploaded.html', {'files': files})'''







    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def upload_file(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
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
                   return redirect('file_explorer')

          
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

def server_monitor(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
        return render(request, 'server_monitor.html')