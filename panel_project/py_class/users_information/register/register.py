from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.http import HttpResponse
from django.conf import settings
import sqlite3
from django.core.cache import cache
import os



conn = sqlite3.connect(os.path.join(settings.DATABASES_ROOT, 'server_data.db'), check_same_thread=False)

# user can send the register request to the server
# 用戶可以發送註冊請求到伺服端
def register(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    ip = get_client_ip(request)
    confirm_password = request.POST['confirm_password']
    if not password == confirm_password:
        return render(request, 'register.html',{'password_not_match': 'the password did not match'})
    elif not len(password) >= 8:
        return render(request, 'register.html',{'password_too_short': 'the password need to be above 8 characters'})
    else:
        cursor = conn.cursor()
        cursor2 = conn.cursor()
        cursor.execute('''
        INSERT INTO accounts (username, email, password, ip_address, login_status)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password, ip, '1'))
        cursor2.execute('''UPDATE accounts SET ip_address = ? WHERE username = ? and password = ?''', (ip, username, password))
        conn.commit()   
        cache.set(ip+'_login_status', "true", timeout=1800)
        return redirect('main')

# get the client ip address
# 獲取用戶端IP地址
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip