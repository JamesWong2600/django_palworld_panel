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

conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_exe(request):
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
    exe_path = os.path.join(settings.MEDIA_ROOT, server_id, servername, 'PalServer.exe')
    #print("my_path is "+ exe_path)
    return exe_path

def server_control(request):
    ip = get_client_ip(request)
    login_status = cache.get(ip+'_login_status')
    print("login status is "+str(login_status))
    if not login_status == "true":
        return redirect('login')
    else:
        return render(request, 'start_or_close_server.html',{'start_or_close': 'start', 'opened': 'server is closed'})

def get_exe_core(request):
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
    exe_path_core = os.path.join(settings.MEDIA_ROOT, server_id, servername, 'Pal\Binaries\Win64\PalServer-Win64-Shipping-Cmd.exe')
    #print(exe_path_core)
    return exe_path_core


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
    #thread = threading.Thread(subprocess_run(request))
    #=thread2 = threading.Thread(get_windows(request))
    #thread.start()
    #thread2.start()
    #image_path = os.path.join('C:\web-project\django_palworld_panel\panel_project', 'cmd_window_capture.png')
    #thread.join()
    #print(str(image_path))
    #return render(request, 'start_or_close_server.html', {'open': "server is opened"})
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
    
def get_process_ram_usage(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process = psutil.Process(proc.info['pid'])
            return round(process.memory_info().rss / (1024 * 1024), 2) 
    return None


def get_process_cpu_usage(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process = psutil.Process(proc.info['pid'])
            return process.cpu_percent(interval=1)
    return None


def get_total_ram_size():
    mem = psutil.virtual_memory()
    return round(mem.total / (1024 * 1024), 2) 

def open_server(request):
    windows = get_exe(request)
    process = subprocess.Popen(
    [rf"{windows}"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    
            
def close_server():
    os.system(r"taskkill /im PalServer-Win64-Shipping-Cmd.exe /f")
    #return render(request, 'start_or_close_server.html')
    #os.system(r"taskkill /im C:\project\django_palworld_panel\panel_project\uploads\yOCn2OfYILkQ\kfc\Pal\Binaries\Win64\PalServer-Win64-Shipping-Cmd.exe")  
    #app = Application().connect(window_title=r"C:\\project\\django_palworld_panel\\panel_project\\uploads\\yOCn2OfYILkQ\\kfc\\PalServer.exe")
    #app.kill()    