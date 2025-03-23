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
import json
from pathlib import Path

conn = sqlite3.connect(os.path.join(settings.DATABASES_ROOT, 'server_data.db'), check_same_thread=False)


def rename_file_backend(request):
    file_name = request.POST.get('file')
    new_name = request.POST.get('new_name')
    base_name = request.POST.get('base_name')
    ip = get_client_ip(request)
    update_cursor = conn.cursor()
    update_cursor.execute(f"SELECT username FROM accounts where ip_address = '{ip}'")
    for row in update_cursor.fetchall():
        username = row[0]
    server_cursor = conn.cursor()
    server_cursor.execute(f"SELECT server_id, server_name FROM servers where owner = '{username}'")
    for rowrow in server_cursor.fetchall():
        server_id = rowrow[0]
        servername = rowrow[1]
    server_file_path = os.path.join(file_name)
    previous_path = os.path.join(server_file_path.replace("\\"+base_name, ""), new_name)
    print("previous path is : "+previous_path)
    current_path = os.path.join(server_file_path)
    print("current path is : "+current_path)
    os.rename(current_path, previous_path)
    folders, directory_boolean = list_folders(server_file_path, base_name)
    folders2 = [fold.replace(server_file_path+"\\", '') for fold in folders]
    folder_paths = [Path(folder).name for folder in folders] 
    print("the path is" + str(folder_paths))
    folder_names = [folder for folder in folders2]  # Same name for display
    folder_types = ["a" for folder in folders2]  # Type of file
    files = zip(folder_paths, folder_names, folder_paths, folder_types, directory_boolean)
    return render(request, 'file-uploaded.html', {'files': files})
    folders2 = []
    for fold in folders:
        fold = fold.replace(server_file_path+"\\", '')
        folders2.append(fold)
    files = [(folder, folder, 'a') for folder in folders2]
    return render(request, 'file-uploaded.html', {'files': files})

def list_folders(directory, base_name):
    folders = []
    directory_boolean = []
    directory = directory.replace("\\"+base_name, '')
    print(directory)
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        print("item path is : "+item_path)
        if os.path.isdir(item_path):
            folders.append(item_path)
            print("item path is : "+item_path)
            #base_path.append(item_path)
            directory_boolean.append("yes")
        else:    
            folders.append(item_path)
            print("item path is : "+item_path)
            directory_boolean.append("no")
    return folders, directory_boolean, #base_path
    return folders

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip




def rename_file_view(request, file_name):
    ip = get_client_ip(request)
    print(file_name)
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
    file_path = os.path.join(settings.MEDIA_ROOT, server_id , servername)
    rename_file(file_path, file_name)
    return render(request, 'rename_file_view.html', {'file_name': servername})



def rename_file(file_path, new_name):
    if os.path.exists(file_path):
        print(file_path)
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)

def send_rename(request):
    ip = get_client_ip(request)
    new_file_name = request.POST['new_file_name']
    original_file_name = request.POST['original_file_name']
    print(original_file_name + " original")
    print(new_file_name + " new")
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



def file_uploaded_rename(request):
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