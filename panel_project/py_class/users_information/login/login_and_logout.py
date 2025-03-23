from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.http import HttpResponse
from django.conf import settings
import sqlite3
from django.core.cache import cache
import os

conn = sqlite3.connect(os.path.join(settings.DATABASES_ROOT, 'server_data.db'), check_same_thread=False)




def logout(request):
    update_cursor = conn.cursor()
    ip = get_client_ip(request)
    update_cursor.execute('''UPDATE accounts SET login_status = ? WHERE ip_address = ?''', ('0', ip))
    conn.commit()
    cache.delete(ip+'_login_status')
    print(cache.get(ip+'_login_status'))
    return redirect('login')
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_account(request):
    username = request.POST['username']
    password = request.POST['password']
    ip = get_client_ip(request)
    cursor = conn.cursor()
    update_cursor = conn.cursor()
    update_cursor2 = conn.cursor()
    cursor.execute('SELECT * FROM accounts where username = ? and password = ?', (username, password))
    update_cursor.execute('''UPDATE accounts SET login_status = ? WHERE username = ? and password = ?''', ('1', username, password))
    update_cursor2.execute('''UPDATE accounts SET ip_address = ? WHERE username = ? and password = ?''', (ip, username, password))
    conn.commit()
    rows = cursor.fetchall()
    if str(rows) == "[]":
        error = 'username or password is incorrect'
        return render(request, 'login.html', {'error': error})
    else:
        cache.set(ip+'_login_status', "true",timeout=1800)
        print(cache.get(ip+'_login_status'))
        return redirect('main')