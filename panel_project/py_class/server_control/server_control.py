from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.http import HttpResponse, Http404
import os
from django.conf import settings
import sqlite3
import subprocess
import pygetwindow as gw
import pyautogui
from PIL import Image
import threading
import time
import sys
import select
import pytesseract
from pywinauto import findwindows, Desktop
import uiautomation as auto
import keyboard
import pyperclip
from pywinauto import Application
from pywinauto import *
from PIL import ImageGrab
import pywinauto
from pywinauto.findwindows import find_windows
from queue import Queue, Empty
import psutil
from django.http import JsonResponse
from django.core.cache import cache

conn = sqlite3.connect(os.path.join(settings.DATABASES_ROOT, 'server_data.db'), check_same_thread=False)

# get the client ip address
# 獲取用戶端IP地址
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# get the exe path
# 獲取exe路徑
def get_exe(request):
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
    exe_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, 'PalServer.exe')
    #print("my_path is "+ exe_path)
    return exe_path

# users can access the server control page
# 用戶可以訪問伺服器控制頁面
def server_control(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
        return render(request, 'start_or_close_server.html',{'start_or_close': 'start', 'opened': 'server is closed'})

# get the exe core path
# 獲取exe核心路徑
def get_exe_core(request):
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
    exe_path_core = os.path.join(settings.MEDIA_ROOT, server_id, servername, 'Pal\Binaries\Win64\PalServer-Win64-Shipping-Cmd.exe')
    #print(exe_path_core)
    return exe_path_core

# users can execute the server
# 用戶可以執行伺服器
def execute_exe(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
       windows = gw.getWindowsWithTitle(get_exe_core(request))
       print(windows)
    #windows = find_windows(title_re=".*PalServer.*")
       if not windows:
          cpu_usage = get_process_cpu_usage("PalServer-Win64-Shipping-Cmd.exe")
          if cpu_usage is None:
            cpu_usage = 0
          ram_usage = get_process_ram_usage("PalServer-Win64-Shipping-Cmd.exe")
          if ram_usage is None:
            ram_usage = 0    
          total_ram = get_total_ram_size()
          print("cpu= "+ str(cpu_usage))
          thread = threading.Thread(target=open_server, args=(request,))
          thread.start()
          thread.join()
          return render(request, 'start_or_close_server.html', {'start_or_close': 'close', 'opened': "server is opened", 'cpu_usage': str(cpu_usage), 'ram_usage': str(ram_usage), 'total_ram': str(total_ram)})
       if windows:
          thread = threading.Thread(target=close_server)
          thread.start()
          thread.join()
          return render(request, 'start_or_close_server.html', {'start_or_close': 'start', 'opened': 'server is closed'})
    
# get the server usage
# 獲取伺服器使用率
def get_usage(request):
    cpu_usage = get_process_cpu_usage("PalServer-Win64-Shipping-Cmd.exe")
    if cpu_usage is None:
        cpu_usage = 0
    ram_usage = get_process_ram_usage("PalServer-Win64-Shipping-Cmd.exe")
    if ram_usage is None:
        ram_usage = 0    
    total_ram = get_total_ram_size()
    print(str(ram_usage))
    windows = gw.getWindowsWithTitle(get_exe_core(request))
    if not windows:
        print("server is closed")
        return JsonResponse({'start_or_close': 'start', 'opened': "server is closed"})
    if windows:
        return JsonResponse({'start_or_close': 'close', 'opened': "server is opened", 'cpu_usage': str(cpu_usage), 'ram_usage': str(ram_usage), 'total_ram': str(total_ram)})

#get ram usage
#獲取RAM使用率
def get_process_ram_usage(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process = psutil.Process(proc.info['pid'])
            return round(process.memory_info().rss / (1024 * 1024), 2) 
    return None

#get cpu usage
#獲取CPU使用率
def get_process_cpu_usage(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process = psutil.Process(proc.info['pid'])
            return process.cpu_percent(interval=1)
    return None

# get the total ram size
# 獲取總RAM大小
def get_total_ram_size():
    mem = psutil.virtual_memory()
    return round(mem.total / (1024 * 1024), 2) 

# open the server
# 開啟伺服器
def open_server(request):
    windows = get_exe(request)
    process = subprocess.Popen(
    [rf"{windows}"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    
            
# close the server
# 關閉伺服器
def close_server():
    os.system(r"taskkill /im PalServer-Win64-Shipping-Cmd.exe /f")