import sqlite3



"""def account():
    user_account_conn = sqlite3.connect('account.db', check_same_thread=False)
    cursor = user_account_conn.cursor()
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS accounts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    login_status TEXT NOT NULL             
    )
    ''')"""