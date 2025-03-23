import sqlite3


"""def check_server():
    user_account_conn = sqlite3.connect('servers.db', check_same_thread=False)
    cursor = user_account_conn.cursor()
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS servers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id TEXT NOT NULL UNIQUE,
    server_name TEXT NOT NULL,    
    file_name TEXT NOT NULL,           
    owner TEXT              
    )
    ''')"""