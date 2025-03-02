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
import subprocess
import pygetwindow as gw
import pyautogui
from PIL import Image
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

conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)








    






    
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



def capture_cmd_window(window_name):
    # Get the window by its title
    window = gw.getWindowsWithTitle(window_name)
    if not window:
        print(f"No window found with the title: {window_name}")
        return None

    window = window[0]

    print(f"Window found: {window}")
    # Activate the window
    window.activate()

    # Get the window's bounding box
    left, top, right, bottom = window.left, window.top, window.right, window.bottom

    # Capture the screen area of the window
    screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

    # Save the screenshot
    screenshot.save('cmd_window_capture.png')
    print("Screenshot saved as cmd_window_capture.png")

    return screenshot



    
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

def server_control(request):
    return render(request, 'start_or_close_server.html',{'start_or_close': 'start', 'opened': 'server is closed'})

def execute_exe(request):
    windows = gw.getWindowsWithTitle(window_title)
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
       thread = threading.Thread(target=open_server)
       thread.start()
       thread.join()
       window_text = get_window_text()
       if window_text:
           print(f"Window text: {window_text}")
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
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print("server is closed")
        return JsonResponse({'start_or_close': 'start', 'opened': "server is closed"})
    if windows:
        return JsonResponse({'start_or_close': 'close', 'opened': "server is opened", 'cpu_usage': str(cpu_usage), 'ram_usage': str(ram_usage), 'total_ram': str(total_ram)})
    


def get_window_text():
    try:
        windows = find_windows(title_re=".*PalServer.*")
        if windows:
            app = Application(backend="win32").connect(handle=windows[0])
            window = app.window(handle=windows[0])
            return window.window_text()
    except Exception as e:
        print(f"Error: {e}")
    return None

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


def open_server():
    process = subprocess.Popen(
    [r"C:\\project\\django_palworld_panel\\panel_project\\uploads\\yOCn2OfYILkQ\\kfc\\PalServer.exe"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    q_stdout = Queue()
    q_stderr = Queue()
    threading.Thread(target=enqueue_output, args=(process.stdout, q_stdout)).start()
    threading.Thread(target=enqueue_output, args=(process.stderr, q_stderr)).start()
    while True:
        try:
            line = q_stdout.get_nowait()
        except Empty:
            break
        else:
            print(line.strip())

        try:
            line = q_stderr.get_nowait()
        except Empty:
            break
        else:
            print(line.strip())


def enqueue_output(pipe, queue):
    for line in iter(pipe.readline, ''):
        queue.put(line)
    pipe.close()


def read_output(pipe):
    for line in iter(pipe.readline, ''):
        print(line.strip())
    pipe.close()
    #Application(backend="win32").start(r"C:\\project\\django_palworld_panel\\panel_project\\uploads\\yOCn2OfYILkQ\\kfc\\PalServer.exe")
    #return render(request, 'start_or_close_server.html', {'open': "server is opened"})

def close_server():
    os.system(r"taskkill /im PalServer-Win64-Shipping-Cmd.exe /f")
    #return render(request, 'start_or_close_server.html')
    #os.system(r"taskkill /im C:\project\django_palworld_panel\panel_project\uploads\yOCn2OfYILkQ\kfc\Pal\Binaries\Win64\PalServer-Win64-Shipping-Cmd.exe")  
    #app = Application().connect(window_title=r"C:\\project\\django_palworld_panel\\panel_project\\uploads\\yOCn2OfYILkQ\\kfc\\PalServer.exe")
    #app.kill()    


def read_output(pipe):
    for line in iter(pipe.readline, b''):
        print(line.decode().strip())
    pipe.close()

window_title = r"C:\project\django_palworld_panel\panel_project\uploads\yOCn2OfYILkQ\kfc\Pal\Binaries\Win64\PalServer-Win64-Shipping-Cmd.exe"


def subprocess_run(request):
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
       Application(backend="win32").start(r"C:\\project\\django_palworld_panel\\panel_project\\uploads\\yOCn2OfYILkQ\\kfc\\PalServer.exe")
    if windows:
       app = Application().connect(r"C:\\project\\django_palworld_panel\\panel_project\\uploads\\yOCn2OfYILkQ\\kfc\\PalServer.exe")
       os.system(rf"taskkill /f /im C:\\project\\django_palworld_panel\\panel_project\\uploads\\yOCn2OfYILkQ\\kfc\\PalServer.exe")  


    #exe_path = get_exe(request)
    #exe_path = rf"{exe_path.replace("\\","\\")}"
    #exe_path = get_exe(request).replace("\\","/")
    #print(exe_path)
    #exe_name = os.path.basename(exe_path)
    #process = subpr*-ocess.Popen(exe_path , stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)

    # 等待應用程式啟動

    '''windows = [w.window_text() for w in Desktop(backend="uia").windows() if w.window_text()]
    print("目前開啟的視窗標題：")
    for title in windows:
        print(title)'''
    '''title=r"C:/project/django_palworld_panel/panel_project/uploads/yOCn2OfYILkQ/kfc/Pal/Binaries/Win64/PalServer-Win64-Shipping-Cmd.exe"'''
    #window = app.window(title=r"C:/project/django_palworld_panel/panel_project/uploads/yOCn2OfYILkQ/kfc/Pal/Binaries/Win64/PalServer-Win64-Shipping-Cmd.exe")  

    #try:
        #window = gw.getWindowsWithTitle(r"C:\project\django_palworld_panel\panel_project\uploads\yOCn2OfYILkQ\kfc\Pal\Binaries\Win64\PalServer-Win64-Shipping-Cmd.exe")[0]
        #time.sleep(1)
        #left, top, width, height = window.left, window.top, window.width, window.height
        #left, top, right, bottom = window.rectangle()
        
        #screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        #screenshot = pyautogui.screenshot(region=(left, top, width, height))
        #screenshot.save("windows.png")
        ## print(f"Captured image from 'windows.png' and saved as 'windows.png'")
    #except IndexError:
      #  print(f"No window found with title: {window_title}")
    '''time.sleep(2)
    windows = gw.getWindowsWithTitle(exe_name)
    window = windows[0]
    window.activate()
    print("MYTEXT")
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    import pyperclip
    text = pyperclip.paste()
    print("MYTEXT"+text)
    #print(exe_name)
    #subprocess.run([exe_path], shell=True, check=False, capture_output=False, text=False)
    time.sleep(1.5)
    #windows = gw.getWindowsWithTitle(exe_name)
    windows = gw.getWindowsWithTitle(exe_name)[0]
    windows.activate()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    import pyperclip
    text = pyperclip.paste()
    print(text)
    print(str(windows) + "windows")
    if not windows:
        print(f"No window found with the title: {exe_path}")
        return None
    window = windows[0]
    print(str(window))
    left, top, right, bottom = window.left, window.top, window.right, window.bottom
    width = right - left
    height = bottom - top
    capture_width = int(width * 0.95)  # Capture 80% of the width
    capture_height = int(height * 0.8)  # Capture 80% of the height
    capture_left = left + int(width * 0.02)  # Start 10% from the left
    capture_top = top + int(height * 0.1) 
    screenshot = pyautogui.screenshot(region=(capture_left, capture_top, capture_width, capture_height))
    screenshot.save(os.path.join(settings.MEDIA_ROOT,'cmd_window_capture.png'))
    print("Screenshot saved as cmd_window_capture.png")'''



'''def get_windows(request):  
    exe_path_core = get_exe(request)  
    print(exe_path_core+" hp")
    windows = gw.getWindowsWithTitle(exe_path_core)
    print(windows)
    if not windows:
        print(f"No window found with the title: {exe_path_core}")
        return None
    window = windows[0]
    print(str(window))
    left, top, right, bottom = window.left, window.top, window.right, window.bottom
    screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
    screenshot.save('cmd_window_capture.png')
    print("Screenshot saved as cmd_window_capture.png")'''


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
    print("my_path is "+ exe_path)
    return exe_path

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
    print(exe_path_core)
    return exe_path_core