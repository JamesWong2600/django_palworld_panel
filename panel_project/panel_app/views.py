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

conn = sqlite3.connect('setting_data.db', check_same_thread=False)

r = redis.Redis(host='localhost', port=6379, db=0)

def change_server_settings(request):
    name = request.POST.get('name')
    value = request.POST.get('value')
    print(name)
    print(value)
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET value = ? WHERE name = ?''', (value, name))
    conn.commit()
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    cursor3 = conn.cursor()
    cursor.execute('SELECT name, value FROM users')
    cursor2.execute('SELECT name FROM users')
    cursor3.execute('SELECT value FROM users')
    all = cursor.fetchall()
    names = cursor2.fetchall()
    values = cursor3.fetchall()
    names_list=[]
    values_list=[]
    for name in names:
        name = str(name).replace("('", "")
        name = name.replace("',)", "")
        names_list.append(name)
    for value in values:
        value = str(value).replace("('", "")
        value = value.replace("',)", "")
        values_list.append(value)
    combined_list = zip(names_list, values_list)
    all = str(all).replace("', '","=")
    all = all.replace("('", "")
    all = all.replace("')", "")
    all = all.replace("[", "OptionSettings=(")
    all = all.replace("]", ")")
    new_file_path = os.path.join(settings.MEDIA_ROOT, 'changed_palworld_setting', 'PalWorldSettings.txt')
    create_new_file(new_file_path, '')
    write_string_to_second_line(os.path.join(settings.MEDIA_ROOT,'changed_palworld_setting', 'PalWorldSettings.txt'), all)
    old_file_path = os.path.join(settings.MEDIA_ROOT, 'changed_palworld_setting', 'PalWorldSettings.txt')
    new_file_name = 'PalWorldSettings.ini'
    rename_file(old_file_path, new_file_name)
    write_string_to_first_line(os.path.join(settings.MEDIA_ROOT,'changed_palworld_setting', 'PalWorldSettings.ini'), '[/Script/Pal.PalGameWorldSettings]')
    print(all)
    return render(request, 'server_setting.html', {'combined_list': combined_list})

def create_new_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)


def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} has been removed.")
    else:
        print(f"File {file_path} does not exist.")        

def write_string_to_first_line(file_path, content):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    lines.insert(0, content + '\n')
    
    with open(file_path, 'w') as file:
        file.writelines(lines)

def write_string_to_second_line(file_path, content):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    lines.insert(1, content + '\n')
    
    with open(file_path, 'w') as file:
        file.writelines(lines)


def write_all_text(file_path, section, value):
    config = ConfigParser()
    config.read(file_path)
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, '', value)
    with open(file_path, 'w') as file:
        config.write(file)


def server_settings(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'PalWorldSettings.ini')
    config_text = read_all_text(file_path)
    config_text = config_text.replace("[/Script/Pal.PalGameWorldSettings]",'')
    config_text = config_text.replace("OptionSettings=(",'')
    config_text = config_text.replace(")",'')
    config_list = [item.strip() for item in config_text.split(',')]
    names = []
    values = []
    combined_list = []
    cursor = conn.cursor()
    cursor.execute('''
    SELECT name FROM sqlite_master WHERE type='table' AND name='users';
    ''')
    table_exists = cursor.fetchone()
    if not table_exists:
        for selection in config_list:
            if '=' in selection:
                name, value = selection.split('=', 1)
                names.append(name.strip())
                values.append(value.strip())
                cursor = conn.cursor()
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value TEXT  NOT NULL
                )
                ''')
                cursor.execute('''
                INSERT INTO users (name, value)
                VALUES (?, ?)
                ''', (name, value))
                conn.commit()
                combined_list = zip(names, values)
    else:
        cursor2 = conn.cursor()
        cursor3 = conn.cursor()
        cursor2.execute('SELECT name FROM users')
        cursor3.execute('SELECT value FROM users')
        names = cursor2.fetchall()
        values = cursor3.fetchall()
        names_list=[]
        values_list=[]
        for name in names:
            name = str(name).replace("('", "")
            name = name.replace("',)", "")
            names_list.append(name)
        for value in values:
            value = str(value).replace("('", "")
            value = value.replace("',)", "")
            values_list.append(value)
        combined_list = zip(names_list, values_list)
    return render(request, 'server_setting.html', {'combined_list': combined_list})


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
    return render(request, 'main.html')

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
    confirm_password = request.POST['confirm_password']
    if password == confirm_password:
        return redirect('main')
    else:
        return render(request, 'register.html')

def upload_file(request):
    file = request.FILES['file']
    filename = None
    subdirectory = generate_random_string()
    server_file_path = os.path.join(settings.MEDIA_ROOT, subdirectory, 'server')
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