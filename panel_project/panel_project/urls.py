from django.contrib import admin
from django.urls import path
from panel_app.views import upload_file, login_view, register_view, register, main_page, file_uploaded, edit_file_view, delete_file_view, download_file_view, rename_file_view, start_or_close_server, server_control, execute_exe_view

urlpatterns = [
    path('main/', main_page, name='main'),
    path('login/', login_view, name='login'),
    path('', register_view, name='register_view'),
    path('start_or_close_server/', start_or_close_server, name='start_or_close_server'),
    path('register/', register, name='register'),
    path('server_control/', server_control, name='server_control'),
    path('upload/', upload_file, name='upload_file'),
    path('file-uploaded/', file_uploaded, name='file_uploaded'),
    path('edit/<str:file_name>/', edit_file_view, name='edit_file'),
    path('delete/<str:file_name>/', delete_file_view, name='delete_file'),
    path('download/<str:file_name>/', download_file_view, name='download_file'),
    path('rename/<str:file_name>/', rename_file_view, name='rename_file'),
    path('execute/<str:file_name>/', execute_exe_view, name='execute_exe'),
]
