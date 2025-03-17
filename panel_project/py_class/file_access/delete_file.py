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
from pathlib import Path
import re

conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)





# users can delete the files
# 用戶可以刪除文件
def delete_file_view(request):
    file_name = request.POST.get('file')
    base_name = request.POST.get('base_name')
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
    file_path = os.path.join(file_name)
    #current_dir = file_path.replace(Path(file_path).name,'')
    #print("current_dir is:", current_dir)
    os.chmod(file_path, stat.S_IWRITE)
    delete_file(file_path)
    folders, directory_boolean = delete_list_folders(file_path, base_name)
    folders2 = [fold.replace(file_path+"\\", '') for fold in folders]
#folder_paths = [Path(folder).name for folder in folders] 
    folder_paths = [folder for folder in folders2]  # Original path
    folder_names = [Path(folder).name for folder in folders2]  # Same name for display
    folder_types = ["a" for folder in folders2]  # Type of file
    files = zip(folder_paths, folder_names, folder_paths, folder_types, directory_boolean)
    return render(request, 'file-uploaded.html', {'files': files}) 

# to list the folders after the delete action
# 在刪除操作之後列出文件夾
def delete_list_folders(file_name, base_name):
    folders_path = []
    directory_boolean = []
    print("base_name is:", base_name)
    file_name = file_name.replace("\\"+base_name, "")
    print("file_name is:", file_name)
    #base_path = []
    if os.path.isdir(file_name):
        for item in os.listdir(file_name):
            item_path = os.path.join(file_name, item)
            if os.path.isdir(item_path):
                folders_path.append(item_path)
                directory_boolean.append("yes")
            else:    
                folders_path.append(item_path)
                directory_boolean.append("no")
        if folders_path == []:
            file_name = file_name.split('\\')
            file_name = file_name[:-1]
            file_name = '\\'.join(file_name)
            print("folders_path is:", str(file_name))
            for item in os.listdir(file_name):
                item_path = os.path.join(file_name, item)
                if os.path.isdir(item_path):
                    folders_path.append(item_path)
                    directory_boolean.append("yes")
                else:    
                    folders_path.append(item_path)
                    directory_boolean.append("no")
        return folders_path, directory_boolean, #base_path

# get the client ip address
# 獲取用戶端IP地址
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#delete file function
#刪除文件功能
def delete_file(file_path):
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
           shutil.rmtree(file_path)
        else:   
           os.remove(file_path)
        print(f"File {file_path} has been removed.")
    else:
        print(f"File {file_path} does not exist.")   
