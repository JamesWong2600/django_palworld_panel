from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.http import HttpResponse
from django.conf import settings
import sqlite3





conn = sqlite3.connect('setting_data.db', check_same_thread=False)
server_conn = sqlite3.connect('servers.db', check_same_thread=False)
account_conn = sqlite3.connect('account.db', check_same_thread=False)


def register(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    ip = get_client_ip(request)
    confirm_password = request.POST['confirm_password']
    if password == confirm_password:
        cursor = account_conn.cursor()
        cursor2 = account_conn.cursor()
        cursor.execute('''
        INSERT INTO accounts (username, email, password, ip_address, login_status)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password, ip, '1'))
        cursor2.execute('''UPDATE accounts SET ip_address = ? WHERE username = ? and password = ?''', (ip, username, password))
        account_conn.commit()
        return redirect('main')
    else:
        return render(request, 'register.html')
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip