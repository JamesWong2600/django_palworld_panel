from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, JsonResponse
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


conn = sqlite3.connect(os.path.join(settings.DATABASES_ROOT, 'server_data.db'), check_same_thread=False)

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
    #current_url = request.build_absolute_uri()

    file_name = request.POST.get('file')
    print("downloaded " +file_name)
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
    ip = get_client_ip(request)
    update_cursor = conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    print(username+ " name")
    server_cursor = conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    for rowrow in server_cursor.fetchall():
        server_id = rowrow[0]
        servername = rowrow[1]
    file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, file_name)
    '''if os.path.isdir(file_path):
        server_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, substring, file_name)
        print(server_file_path)
        folders = list_folders(server_file_path)
        folders2 = []
        for fold in folders:
          fold = fold.replace(server_file_path+"\\", '')
          folders2.append(fold)
          files = [(folder, folder, "a") for folder in folders2]   
        return render(request, 'file-uploaded.html', {'files': files})
    else:'''
    content = read_all_text(file_path)
    return render(request, 'edit_file_view.html', {'file_name': file_name, 'content': content})
    
def list_folders(directory):
    folders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) or os.path.isfile(item_path):
            folders.append(item_path)
    return folders

def save_edit_notused(request):
    file_name = request.POST['file_name']
    content = request.POST['content']
    base_name = request.POST['base_name']
    ip = get_client_ip(request)
    update_cursor = conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    print(username+ " name")
    server_cursor = conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    print("james_test")
    for rowrow in server_cursor.fetchall():
        server_id = rowrow[0]
        servername = rowrow[1]
    if not file_name.endswith('.txt'):
        new_file_name = file_name + '.txt'
        old_file_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, file_name)
        print("old file path is "+old_file_path)
        new_file_name = os.path.join(settings.MEDIA_ROOT, server_id, servername, new_file_name)
        os.rename(old_file_path, new_file_name)
        with open(new_file_name, 'w') as file:
            file.write(content) 
            print("weittedddddddddddddddddddddddddddddd")
        with open(new_file_name, 'r') as file:
            print(file.read())
        os.rename(new_file_name, old_file_path)    
    else:
        with open(new_file_name, 'w') as file:
            file.write(content)
        with open(new_file_name, 'r') as file:
            print(file.read())
    previous_url = request.META.get('HTTP_REFERER', '')         
    #return redirect('file_explorer')
    return JsonResponse({'status': 'success', 'message': 'File saved successfully'})