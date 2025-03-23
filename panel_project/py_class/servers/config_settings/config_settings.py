import os
import sqlite3
from configparser import ConfigParser
from django.conf import settings
from django.shortcuts import render, redirect
import shutil
import json
from django.http import JsonResponse
import time
from django.core.cache import cache
from itertools import islice

conn = sqlite3.connect(os.path.join(settings.DATABASES_ROOT, 'server_data.db'), check_same_thread=False)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def edit_file(file_path, new_content=None):
    if new_content is not None:
        with open(file_path, 'w') as file:
            file.write(new_content)
    else:
        with open(file_path, 'r') as file:
            return file.read()

def delete_file(file_path):
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
           shutil.rmtree(file_path)
        else:   
           os.remove(file_path)
        print(f"File {file_path} has been removed.")
    else:
        print(f"File {file_path} does not exist.")   

def download_file(file_path):
    pass

def rename_file(file_path, new_name):
    if os.path.exists(file_path):
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)

def change_server_settings(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
        update_cursor = conn.cursor()
        update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
        for row in update_cursor.fetchall():
            username = row[0]
        print(username+ " bname")
        server_cursor = conn.cursor()
        server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
        print("tov")   
        for rowrow in server_cursor.fetchall():
            server_id = rowrow[0]
            servername = rowrow[1]  
        names = json.loads(request.POST.get('names', '[]'))
        values = json.loads(request.POST.get('values', '[]'))
        set = zip(names, values)
        print("set is "+str(set))
        #names = []
        #values = []
        settings_parts = []
        cache.set(ip+'_palworld_settings_cahce', set)
        setting_cache = cache.get(ip+'_palworld_settings_cahce')
        for selection in setting_cache:
            selection = str(selection).replace("'", "")
            selection = selection.replace("(", "")
            selection = selection.replace(")", "")
            print("selection now is "+str(selection))
            name, value = str(selection).split(',', 1)
            settings_parts.append(f"{name.strip()}={value.strip()}")
            #names.append(name.strip())
            #values.append(value.strip())
        """combined_list = zip(names, values)
        all = str(combined_list).replace("', '","=")
        print("all is "+str(all))
        all = all.replace("('", "")
        all = all.replace("')", "")
        all = all.replace("[", "OptionSettings=(")
        all = all.replace("]", ")")
        print("all is "+str(all))"""
        settings_string = f"OptionSettings=({','.join(settings_parts)})"
        print(f"Final settings: {settings_string}")
        new_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.txt')
        delete_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.ini')
        delete_file_path2 = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.txt')
        if os.path.exists(delete_file_path):
          os.remove(delete_file_path) 
        if os.path.exists(delete_file_path2):
          os.remove(delete_file_path) 
        create_new_file(new_file_path, '')
        write_string_to_second_line(os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt'), settings_string)
        #write_string_to_second_line(os.path.join(settings.MEDIA_ROOT, server_id, servername, 'DefaultPalWorldSettings.ini'), settings_string)
        old_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt')
        new_file_name = 'PalWorldSettings.ini'
        write_string_to_first_line(os.path.join(settings.MEDIA_ROOT,server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt'), '[/Script/Pal.PalGameWorldSettings]')
        #write_string_to_first_line(os.path.join(settings.MEDIA_ROOT,server_id, servername,'DefaultPalWorldSettings.ini'), '[/Script/Pal.PalGameWorldSettings]')
        rename_file(old_file_path, new_file_name)
        return JsonResponse({'message': 'Settings updated successfully'})#print(all)
        #return render(request, 'server_setting.html', {'combined_list': combined_list})

def change_server_settings_unused(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
        update_cursor = conn.cursor()
        update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
        for row in update_cursor.fetchall():
            username = row[0]
        print(username+ " bname")
        server_cursor = conn.cursor()
        server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
        print("tov")   
        for rowrow in server_cursor.fetchall():
            server_id = rowrow[0]
            servername = rowrow[1]
        print("tov")    
        names = json.loads(request.POST.get('names', '[]'))
        values = json.loads(request.POST.get('values', '[]'))
        set = zip(names, values)
        for name, value in set:    
            print(name+" "+value)
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
            print("new value ="+ value)
        combined_list = zip(names_list, values_list)
        all = str(all).replace("', '","=")
        all = all.replace("('", "")
        all = all.replace("')", "")
        all = all.replace("[", "OptionSettings=(")
        all = all.replace("]", ")")
        new_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.txt')
        delete_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.ini')
        delete_file_path2 = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.txt')
        if os.path.exists(delete_file_path):
           os.remove(delete_file_path) 
        if os.path.exists(delete_file_path2):
           os.remove(delete_file_path) 
        create_new_file(new_file_path, '')
        write_string_to_second_line(os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt'), all)
        old_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt')
        new_file_name = 'PalWorldSettings.ini'
        write_string_to_first_line(os.path.join(settings.MEDIA_ROOT,server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt'), '[/Script/Pal.PalGameWorldSettings]')
        rename_file(old_file_path, new_file_name)
        return JsonResponse({'message': 'Settings updated successfully'})#print(all)
        #return render(request, 'server_setting.html', {'combined_list': combined_list})

def create_new_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)


def remove_file(file_path):
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
           shutil.rmtree(file_path)
        else:   
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
    lines.insert(1, str(content) + '\n')
    
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

def server_settings_notused(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
        update_cursor = conn.cursor()
        update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
        for row in update_cursor.fetchall():
            username = row[0]
        print(username+ " dname")
        time.sleep(1)
        server_cursor = conn.cursor()
        server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
        for rowrow in server_cursor.fetchall():
            server_id = rowrow[0]
            servername = rowrow[1]
        file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, 'DefaultPalWorldSettings.ini')
        #print(file_path)
        config_text = read_all_text(file_path)
        config_text = config_text.replace("""; This configuration file is a sample of the default server settings.
    ; Changes to this file will NOT be reflected on the server.
    ; To change the server settings, modify Pal/Saved/Config/WindowsServer/PalWorldSettings.ini.""",'')
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
                    value TEXT NOT NULL
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
        #print(str(values))
        return render(request, 'server_setting.html', {'combined_list': combined_list})
    
#users can access the server settings page
#用戶可以訪問伺服器設置頁面
def server_settings(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
        update_cursor = conn.cursor()
        update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
        for row in update_cursor.fetchall():
            username = row[0]
        print(username+ " dname")
        time.sleep(1)
        server_cursor = conn.cursor()
        server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
        for rowrow in server_cursor.fetchall():
            server_id = rowrow[0]
            servername = rowrow[1]
        file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, 'DefaultPalWorldSettings.ini')
        #print(file_path)
        original_setting = read_all_text_from_settings(os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.ini'))
        print("original_setting_is:"+str(original_setting))
        if original_setting is None or not str(original_setting).strip():
            config_text = read_all_text(file_path)
            print("original_setting is empty")
            input_text = config_text.replace('[/Script/Pal.PalGameWorldSettings]','')
            print("input_text is "+input_text)
            new_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.txt')
            delete_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.ini')
            delete_file_path2 = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer','PalWorldSettings.txt')
            if os.path.exists(delete_file_path):
              os.remove(delete_file_path) 
            if os.path.exists(delete_file_path2):
              os.remove(delete_file_path) 
            create_new_file(new_file_path, '')
            write_string_to_second_line(os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt'), input_text)
            old_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt')
            new_file_name = 'PalWorldSettings.ini'
            write_string_to_first_line(os.path.join(settings.MEDIA_ROOT,server_id, servername,'Pal','Saved','Config','WindowsServer', 'PalWorldSettings.txt'), '[/Script/Pal.PalGameWorldSettings]')
            rename_file(old_file_path, new_file_name)
        else:
            config_text = original_setting
        config_text = config_text.replace('[/Script/Pal.PalGameWorldSettings]','')
        config_text = config_text.replace("OptionSettings=(",'')
        config_text = config_text.replace(")",'')
        config_list = [item.strip() for item in config_text.split(',')]
        cache.set(ip+'_palworld_settings_cahce', config_list)
        print("configlist is"+str(config_list))
        names = []
        values = []
        combined_list = []
        setting_cache = cache.get(ip+'_palworld_settings_cahce')
        for selection in setting_cache:
            print("selection is aaa"+selection)
            if '=' in selection:
                name, value = selection.split('=', 1)
                names.append(name.strip())
                values.append(value.strip())
        combined_list = zip(names, values)
        return render(request, 'server_setting.html', {'combined_list': combined_list})    

          
def read_all_text(file_path):
    #with open(file_path, 'r', encoding='utf-8') as file:
    # Preserve all formatting including whitespace and newlines
       # content = file.read()
        #return content
    with open(file_path, 'r') as file:
        content_from_fifth = ''.join(islice(file, 4, None))
        print("content_from_fifth is "+content_from_fifth)
        return content_from_fifth
        #return file.read()

def read_all_text_from_settings(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def write_all_text(file_path):
    with open(file_path, 'w') as file:
        return file.write()
