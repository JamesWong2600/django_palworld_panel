import os
import sqlite3
from configparser import ConfigParser
from django.conf import settings
from django.shortcuts import render, redirect


conn = sqlite3.connect('setting_data.db', check_same_thread=False)

def edit_file(file_path, new_content=None):
    if new_content is not None:
        with open(file_path, 'w') as file:
            file.write(new_content)
    else:
        with open(file_path, 'r') as file:
            return file.read()

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def download_file(file_path):
    pass

def rename_file(file_path, new_name):
    if os.path.exists(file_path):
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)


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

          
def read_all_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def write_all_text(file_path):
    with open(file_path, 'w') as file:
        return file.write()
