import sqlite3
import os
import shutil
from datetime import datetime
from tkinter import messagebox

DB_NAME = "kadri_final_system.db"


def execute_query(query, params=(), is_select=True, fetchone=False, executemany=False):
    """
    دالة موحدة لتنفيذ الاستعلامات بأمان تام وإغلاق الاتصال تلقائياً لتفادي بقاء قاعدة البيانات معلقة.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=30)
        cursor = conn.cursor()

        if executemany:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)

        if is_select:
            if fetchone:
                return cursor.fetchone()
            return cursor.fetchall()
        else:
            conn.commit()
            return True

    except sqlite3.Error as e:
        messagebox.showerror("خطأ في قاعدة البيانات", f"حدث خطأ أثناء تنفيذ العملية:\n{e}")
        return None
    finally:
        if conn:
            conn.close()


def init_db():
    """تهيئة الجداول الافتراضية وحساب المسؤول الأول لأول مرة."""
    import hashlib
    queries = [
        '''CREATE TABLE IF NOT EXISTS inventory
           (
               id
               TEXT
               PRIMARY
               KEY,
               name
               TEXT,
               model
               TEXT,
               brand
               TEXT,
               qty
               INTEGER,
               price
               REAL,
               destination
               TEXT,
               project
               TEXT,
               function
               TEXT,
               category
               TEXT,
               properties
               TEXT,
               status
               TEXT
           )''',
        '''CREATE TABLE IF NOT EXISTS logs
           (
               user
               TEXT,
               action
               TEXT,
               item_id
               TEXT,
               timestamp
               TEXT
           )''',
        '''CREATE TABLE IF NOT EXISTS users
           (
               username
               TEXT
               PRIMARY
               KEY,
               password
               TEXT,
               role
               TEXT
           )''',
        '''CREATE TABLE IF NOT EXISTS invoices
           (
               id
               INTEGER
               PRIMARY
               KEY
               AUTOINCREMENT,
               client
               TEXT,
               total
               REAL,
               date
               TEXT
           )''',
        '''CREATE TABLE IF NOT EXISTS technicians
           (
               id
               TEXT
               PRIMARY
               KEY,
               name
               TEXT,
               phone
               TEXT,
               specialty
               TEXT,
               status
               TEXT
           )''',
        '''CREATE TABLE IF NOT EXISTS contracts
           (
               id
               TEXT
               PRIMARY
               KEY,
               client
               TEXT,
               address
               TEXT,
               elevator_type
               TEXT,
               start_date
               TEXT,
               end_date
               TEXT,
               status
               TEXT
           )''',
        '''CREATE TABLE IF NOT EXISTS maintenance_tasks
           (
               id
               INTEGER
               PRIMARY
               KEY
               AUTOINCREMENT,
               contract_id
               TEXT,
               tech_id
               TEXT,
               task_date
               TEXT,
               description
               TEXT,
               status
               TEXT,
               notes
               TEXT
           )'''
    ]

    for q in queries:
        execute_query(q, is_select=False)

    admin_exists = execute_query("SELECT COUNT(*) FROM users WHERE role='ADMIN'", fetchone=True)
    if admin_exists and admin_exists[0] == 0:
        default_pw_hashed = hashlib.sha256('admin'.encode()).hexdigest()
        execute_query("INSERT INTO users VALUES ('admin', ?, 'ADMIN')", (default_pw_hashed,), is_select=False)
        print("Database initialized successfully.")


def auto_backup():
    """عمل نسخة احتياطية من قاعدة البيانات تلقائياً عند التشغيل."""
    try:
        if not os.path.exists("backups"):
            os.makedirs("backups")
        if os.path.exists(DB_NAME):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(DB_NAME, f"backups/backup_{timestamp}.db")
    except Exception as e:
        print("Backup failed:", e)
