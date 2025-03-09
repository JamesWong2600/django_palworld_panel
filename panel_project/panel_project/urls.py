from django.contrib import admin
from django.urls import path, re_path
from panel_app.views import upload_file, login_view, register_view, register, main_page, file_uploaded, edit_file_view
from panel_app.views import delete_file_view, download_file_view, rename_file_view, start_or_close_server, server_control, execute_exe, server_settings
from panel_app.views import change_server_settings, login_view, login_account, logout, file_uploaded_rename, send_rename
from panel_app.views import edit_file_view, save_edit, open_server, close_server, get_usage, backup_page, backup_action, download_backup
from panel_app.views import file_uploaded_with_parameter, open_or_edit_file_view_base, file_uploaded_base
from panel_app.views import file_explorer_view, rename_file_backend
urlpatterns = [
    path('main/', main_page, name='main'),
    path('login/', login_view, name='login'),
    path('', register_view, name='register_view'),
    #path('start_or_close_server/', start_or_close_server, name='start_or_close_server'),
    path('register/', register, name='register'),
    path('server_control/', server_control, name='server_control'),
    path('upload/', upload_file, name='upload_file'),
    #re_path(r'^file_uploaded/(?P<path>.*)$', file_uploaded, name='file_uploaded'),
    path('file_uploaded/', file_uploaded_base, name='file_uploaded_base'),
    #path('file-uploaded/<str:file1>', file_uploaded, name='file_uploaded'),
    #path('file-uploaded/<str:file>/<str:file2>', file_uploaded, name='file_uploaded'),
    #path('file_uploaded_with_parameter/<path:params>/', file_uploaded_with_parameter, name='file_uploaded_with_parameter'),
    path('file_uploaded_with_parameter/', file_uploaded_with_parameter, name='file_uploaded_with_parameter'),
    #path('file_uploaded_with_parameter/<str:arg1>/<str:arg2>/<str:arg3>/', file_uploaded_with_parameter, name='file_uploaded_with_parameter'),
    #path('append-to-url/<path:args>/', append_to_url, name='append_to_url'),
    #path('edit/<str:parameter>/', edit_file_view, name='edit_file'),
    path('edit/<str:file_name>/', edit_file_view, name='edit_file'),
    path('delete_file/', delete_file_view, name='delete_file'),
    path('download/', download_file_view, name='download_file'),
    path('rename_file_view/<str:file_name>', rename_file_view, name='rename_file_view'),
    path('execute_exe/', execute_exe, name='execute_exe'),
    path('admin/', admin.site.urls),
    path('server_settings/', server_settings, name='server_settings'),    
    path('change_server_settings/', change_server_settings, name='change_server_settings'),
    path('login/', login_view, name='login'),
    path('login_account/', login_account, name='login_account'),
    path('logout/', logout, name='logout'),
    path('file_uploaded_rename/', file_uploaded_rename, name='file_uploaded_rename'), #3
    path('send_rename/', send_rename, name='send_rename'),
    path('edit_file_view/', edit_file_view, name='edit_file_view'),
    path('open_file_view/', open_or_edit_file_view_base, name='open_file_view'),#2
    path('save_edit/', save_edit, name='save_edit'),
    path('open_server/', open_server, name='open_server'),
    path('close_server/', close_server, name='close_server'),
    path('get_usage/', get_usage, name='get_usage'),
    path('backup_page/', backup_page, name='backup_page'),
    path('backup_action/', backup_action, name='backup_action'),
    path('download_backup/', download_backup, name='download_backup'),
    path('Content/', edit_file_view, name='edit_file_view_content'),
    path('file_explorer/', file_explorer_view, name='file_explorer'), #1
    path('rename_file_backend/',rename_file_backend, name='rename_file_backend'),#4
]
