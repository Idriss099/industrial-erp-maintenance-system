import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
import shutil
from datetime import datetime
import sys
import os
import ctypes
import csv
import matplotlib.pyplot as plt
import uuid
import json
import hashlib  # <--- إضافة مكتبة التشفير الخاصة بالترخيص وكلمات المرور

# --- 0. نظام الإعدادات الديناميكي (Config System) ---
def load_config():
    config_file = "config.json"
    default_data = {
        "company_name": "SARL KADRI ASCENSEURS",
        "company_subtitle": "Installation, Maintenance et Modernisation d'Ascenseurs",
        "company_address": "*************, Blida",
        "company_phone": "**************",
        "company_email": "**************",
        "app_version": "v20.0 PRO",
        "currency": "DA"
    }
    
    # إذا كان الملف غير موجود، أنشئه بالبيانات الافتراضية
    if not os.path.exists(config_file):
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data
        
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: # إذا كان الملف موجوداً لكنه فارغ
                return default_data
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        # في حال وجود خطأ في بنية الملف، ارجع للبيانات الافتراضية
        return default_data

CONFIG = load_config()

# --- حماية الترخيص (الكود القديم تم تهميشه للحفاظ عليه) ---
# def check_license():
#     device_id = str(uuid.getnode())
#     # قم بوضع Device ID الخاص بك هنا
#     if device_id not in ["PUT_YOUR_DEVICE_ID_HERE", device_id]:
#         messagebox.showerror("License Error", "Unauthorized device")
#         sys.exit()

# --- حماية الترخيص الجديدة (المربوطة بمولد المفاتيح) ---
SECRET_SALT = "KADRI_ASCENSEURS_2026_PRO_SECURE_KEY_99"

def check_license():
    # 1. الحصول على كود الجهاز
    device_id = str(uuid.getnode()).upper()
    
    # 2. توليد المفتاح المتوقع (نفس خوارزمية Key Generator)
    raw_key = device_id + SECRET_SALT
    expected_key = hashlib.sha256(raw_key.encode()).hexdigest()[:20].upper()
    
    license_file = "license.dat"
    
    # 3. التحقق مما إذا كان الترخيص موجوداً وصالحاً
    if os.path.exists(license_file):
        try:
            with open(license_file, "r") as f:
                saved_key = f.read().strip()
            if saved_key == expected_key:
                return  # الترخيص سليم، السماح بمرور البرنامج
        except:
            pass
            
    # 4. إذا لم يكن صالحاً، نظهر نافذة التفعيل
    show_activation_window(device_id, expected_key, license_file)

def show_activation_window(device_id, expected_key, license_file):
    act_win = tk.Tk()
    act_win.title("تفعيل نظام ERP - SARL KADRI ASCENSEURS")
    act_win.geometry("550x400")
    act_win.configure(bg="#2c3e50")
    
    try: act_win.iconbitmap(resource_path("logo.ico"))
    except: pass
    
    tk.Label(act_win, text="🔒 النظام غير مفعل", fg="#e74c3c", bg="#2c3e50", font=("Arial", 20, "bold")).pack(pady=(20, 5))
    tk.Label(act_win, text="يرجى إرسال (كود الجهاز) إلى مطور النظام للحصول على مفتاح التفعيل.", fg="#ecf0f1", bg="#2c3e50", font=("Arial", 11)).pack(pady=5)
    
    # عرض كود الجهاز
    tk.Label(act_win, text="كود الجهاز (Device ID):", fg="#f1c40f", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=(15,0))
    id_entry = tk.Entry(act_win, font=("Arial", 14), justify="center", width=30, bg="#ecf0f1", fg="#2c3e50")
    id_entry.insert(0, device_id)
    id_entry.config(state="readonly") # لمنع التعديل عليه
    id_entry.pack(pady=5)
    
    # إدخال مفتاح التفعيل
    tk.Label(act_win, text="أدخل مفتاح التفعيل (Activation Key):", fg="#f1c40f", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=(20,0))
    key_entry = tk.Entry(act_win, font=("Arial", 16), justify="center", width=25)
    key_entry.pack(pady=10)
    
    def attempt_activation():
        entered_key = key_entry.get().strip().upper()
        if entered_key == expected_key:
            # حفظ المفتاح في ملف
            with open(license_file, "w") as f:
                f.write(entered_key)
            messagebox.showinfo("نجاح", "✅ تم تفعيل البرنامج بنجاح! سيتم تشغيل النظام الآن.", parent=act_win)
            act_win.destroy()
        else:
            messagebox.showerror("خطأ", "❌ مفتاح التفعيل غير صحيح! يرجى التأكد والمحاولة مجدداً.", parent=act_win)
            
    tk.Button(act_win, text="تفعيل (ACTIVATE)", command=attempt_activation, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), width=20).pack(pady=15)
    
    act_win.mainloop()
    
    # التحقق النهائي بعد إغلاق النافذة: إذا لم يتم التفعيل، يتم إغلاق البرنامج بالكامل
    if os.path.exists(license_file):
        with open(license_file, "r") as f:
            if f.read().strip() == expected_key:
                return
    sys.exit() # إنهاء البرنامج إذا تم إغلاق نافذة التفعيل بدون كتابة مفتاح صحيح
# ----------------------------------------------------------------------


try:
    from PIL import Image, ImageTk
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except ImportError:
    print("برجاء تثبيت المكتبات: pip install pillow reportlab")

# --- 1. إعدادات النظام وقاعدة البيانات ---

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def prepare_icon():
    try:
        logo_p = resource_path("logo.png")
        if os.path.exists(logo_p) and not os.path.exists("logo.ico"):
            img = Image.open(logo_p)
            img.save("logo.ico", format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    except: pass

def init_db():
    conn = sqlite3.connect("kadri_final_system.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory
                      (id TEXT PRIMARY KEY, name TEXT, model TEXT, brand TEXT,
                       qty INTEGER, price REAL, destination TEXT, project TEXT,
                       function TEXT, category TEXT, properties TEXT, status TEXT)''')
                       
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                      (user TEXT, action TEXT, item_id TEXT, timestamp TEXT)''')
                      
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
                  
    # تشفير كلمة المرور الافتراضية 'admin' عند إنشاء قاعدة البيانات لأول مرة
    default_pw_hashed = hashlib.sha256('admin'.encode()).hexdigest()
    # التحقق من وجود أي حساب مسؤول (ADMIN) قبل الإضافة
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='ADMIN'")
    admin_exists = cursor.fetchone()[0]

    if admin_exists == 0:
        # إذا لم يوجد أي أدمن نهائياً، ننشئ الحساب الافتراضي لأول مرة فقط
        default_pw_hashed = hashlib.sha256('admin'.encode()).hexdigest()
        cursor.execute("INSERT INTO users VALUES ('admin', ?, 'ADMIN')", (default_pw_hashed,))
        print("تم إنشاء حساب المسؤول الافتراضي.")
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS invoices
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, client TEXT, total REAL, date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS technicians
                  (id TEXT PRIMARY KEY, name TEXT, phone TEXT, specialty TEXT, status TEXT)''')
                  
    cursor.execute('''CREATE TABLE IF NOT EXISTS contracts
                  (id TEXT PRIMARY KEY, client TEXT, address TEXT, elevator_type TEXT, 
                   start_date TEXT, end_date TEXT, status TEXT)''')
                   
    cursor.execute('''CREATE TABLE IF NOT EXISTS maintenance_tasks
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, contract_id TEXT, tech_id TEXT, 
                   task_date TEXT, description TEXT, status TEXT, notes TEXT)''')
                   
    conn.commit()
    conn.close()

def auto_backup():
    try:
        if not os.path.exists("backups"): os.makedirs("backups")
        db_file = "kadri_final_system.db"
        if os.path.exists(db_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(db_file, f"backups/backup_{timestamp}.db")
    except: pass

# --- دوال المخططات والذكاء الاصطناعي ---
def show_chart():
    conn = sqlite3.connect("kadri_final_system.db")
    data = conn.execute("SELECT name, qty FROM inventory").fetchall()
    conn.close()
    if not data:
        messagebox.showinfo("Info", "No data to display")
        return
    names = [d[0] for d in data]
    qtys = [d[1] for d in data]
    plt.bar(names, qtys)
    plt.xticks(rotation=45)
    plt.title("Stock Levels")
    plt.tight_layout()
    plt.show()    
    
def smart_restock():
    conn = sqlite3.connect("kadri_final_system.db")
    data = conn.execute("SELECT name, qty FROM inventory").fetchall()
    conn.close()
    low = [d[0] for d in data if d[1] < 5]
    if low:
        messagebox.showinfo("Smart System", "Restock needed:\n" + "\n".join(low))
    else:
        messagebox.showinfo("Smart System", "Stock is OK")  

# --- 1.5. نافذة إعدادات النظام ---
def open_settings_window(parent):
    set_win = tk.Toplevel(parent)
    set_win.title("⚙️ إعدادات النظام (System Settings)")
    # تم زيادة ارتفاع النافذة لتتسع لإعدادات المستخدم وكلمة المرور
    set_win.geometry("550x700")
    set_win.configure(bg="#f4f7f6")
    
    try: set_win.iconbitmap(resource_path("logo.ico"))
    except: pass

    tk.Label(set_win, text="تعديل بيانات الشركة والنظام", font=("Arial", 16, "bold"), bg="#f4f7f6", fg="#2c3e50").pack(pady=10)

    form_frame = tk.Frame(set_win, bg="#f4f7f6")
    form_frame.pack(pady=5)

    fields_info = [
        ("company_name", "اسم الشركة:"),
        ("company_subtitle", "النشاط / الوصف:"),
        ("company_address", "العنوان:"),
        ("company_phone", "أرقام الهاتف:"),
        ("company_email", "البريد الإلكتروني:"),
        ("app_version", "إصدار البرنامج:"),
        ("currency", "العملة المستخدمة:")
    ]

    entries = {}
    
    for i, (key, label_text) in enumerate(fields_info):
        tk.Label(form_frame, text=label_text, font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=i, column=1, sticky="e", padx=10, pady=5)
        ent = tk.Entry(form_frame, width=35, font=("Arial", 11))
        ent.insert(0, CONFIG.get(key, ""))
        ent.grid(row=i, column=0, padx=10, pady=5)
        entries[key] = ent

    def save_new_settings():
        global CONFIG
        new_data = {key: ent.get().strip() for key, ent in entries.items()}
        
        # حفظ في الملف
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
            
        # تحديث المتغير العالمي
        CONFIG.update(new_data)
        
        messagebox.showinfo("تم الحفظ", "✅ تم حفظ الإعدادات بنجاح.\nالرجاء إعادة تشغيل البرنامج لتطبيق جميع التغييرات (مثل عنوان النافذة).", parent=set_win)
        # أزلت إغلاق النافذة التلقائي هنا للسماح للمستخدم بتغيير الباسوورد إن أراد

    tk.Button(set_win, text="💾 حفظ إعدادات الشركة", command=save_new_settings, bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=20).pack(pady=10)

    # --------- قسم تعديل بيانات الدخول (جديد) ---------
    # --------- قسم تعديل بيانات الدخول (نسخة محسنة وآمنة) ---------
    ttk.Separator(set_win, orient='horizontal').pack(fill='x', pady=10, padx=20)
    
    tk.Label(set_win, text="تغيير بيانات تسجيل الدخول", font=("Arial", 14, "bold"), bg="#f4f7f6", fg="#c0392b").pack(pady=5)
    
    cred_frame = tk.Frame(set_win, bg="#f4f7f6")
    cred_frame.pack(pady=5)
    
    # إضافة حقل كلمة المرور القديمة للأمان
    tk.Label(cred_frame, text="كلمة المرور الحالية:", font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=0, column=1, sticky="e", padx=10, pady=5)
    old_pass_ent = tk.Entry(cred_frame, width=25, font=("Arial", 11), show="*")
    old_pass_ent.grid(row=0, column=0, padx=10, pady=5)

    tk.Label(cred_frame, text="اسم المستخدم الجديد:", font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=1, column=1, sticky="e", padx=10, pady=5)
    new_user_ent = tk.Entry(cred_frame, width=25, font=("Arial", 11))
    new_user_ent.grid(row=1, column=0, padx=10, pady=5)
    
    tk.Label(cred_frame, text="كلمة المرور الجديدة:", font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=2, column=1, sticky="e", padx=10, pady=5)
    new_pass_ent = tk.Entry(cred_frame, width=25, font=("Arial", 11), show="*")
    new_pass_ent.grid(row=2, column=0, padx=10, pady=5)
    
    tk.Label(cred_frame, text="تأكيد كلمة المرور:", font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=3, column=1, sticky="e", padx=10, pady=5)
    conf_pass_ent = tk.Entry(cred_frame, width=25, font=("Arial", 11), show="*")
    conf_pass_ent.grid(row=3, column=0, padx=10, pady=5)
    
    def save_credentials():
        op = old_pass_ent.get().strip()
        nu = new_user_ent.get().strip()
        np = new_pass_ent.get().strip()
        cp = conf_pass_ent.get().strip()
        
        if not op or not nu or not np:
            messagebox.showwarning("تحذير", "يرجى ملء جميع الحقول!", parent=set_win)
            return
        
        if np != cp:
            messagebox.showerror("خطأ", "كلمات المرور الجديدة غير متطابقة!", parent=set_win)
            return

        try:
            conn = sqlite3.connect("kadri_final_system.db")
            cursor = conn.cursor()
            
            # 1. التحقق من صحة كلمة المرور القديمة أولاً
            hashed_op = hashlib.sha256(op.encode()).hexdigest()
            cursor.execute("SELECT password FROM users WHERE role='ADMIN'")
            result = cursor.fetchone()
            
            if result and result[0] == hashed_op:
                # 2. إذا كانت صحيحة، نقوم بالتحديث
                hashed_np = hashlib.sha256(np.encode()).hexdigest()
                cursor.execute("UPDATE users SET username=?, password=? WHERE role='ADMIN'", (nu, hashed_np))
                conn.commit()
                messagebox.showinfo("نجاح", "✅ تم تحديث بيانات الدخول بنجاح!", parent=set_win)
                
                # تنظيف الحقول
                for entry in [old_pass_ent, new_user_ent, new_pass_ent, conf_pass_ent]:
                    entry.delete(0, tk.END)
            else:
                messagebox.showerror("خطأ", "❌ كلمة المرور الحالية غير صحيحة!", parent=set_win)
                
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("خطأ في قاعدة البيانات", f"فشل التحديث: {e}", parent=set_win)
        except Exception as e:
            messagebox.showerror("خطأ غير متوقع", f"حدث خطأ: {e}", parent=set_win)

    tk.Button(set_win, text="🔐 تحديث بيانات الدخول", command=save_credentials, bg="#c0392b", fg="white", font=("Arial", 11, "bold"), width=20).pack(pady=10)
    # --------------------------------------------------


# --- 2. التطبيق الرئيسي ---

def open_main_app():
    root = tk.Tk()
    try:
        myappid = 'kadri.ascenseurs.erp.v20'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        root.iconbitmap(resource_path("logo.ico"))
    except: pass
    
    root.title(f"{CONFIG['company_name']} - Enterprise ERP {CONFIG['app_version']}")
    root.geometry("1550x900")
    root.configure(bg="#f4f7f6")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_inventory = tk.Frame(notebook, bg="#f4f7f6")
    tab_maintenance = tk.Frame(notebook, bg="#f4f7f6")

    notebook.add(tab_inventory, text="📦 إدارة المخزون والمبيعات (Inventory & Sales)")
    notebook.add(tab_maintenance, text="🛠️ إدارة الصيانة والعقود (Maintenance & Contracts)")

    # =========================================================
    # التبويب الأول: المخزون والمبيعات
    # =========================================================
    
    def log_action(action, item_id):
        conn = sqlite3.connect("kadri_final_system.db")
        conn.execute("INSERT INTO logs VALUES (?,?,?,?)",
                     ("Admin", action, item_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()

    def update_stats():
        conn = sqlite3.connect("kadri_final_system.db")
        res = conn.execute("SELECT SUM(qty), SUM(qty * price), COUNT(*) FROM inventory").fetchone()
        conn.close()
        q, v, c = (res[0] or 0), (res[1] or 0), (res[2] or 0)
        lbl_stats.config(text=f"📊 Items: {c} | Units: {int(q)} | Inventory Value: {float(v):,.2f} {CONFIG['currency']}")
        if q > 0:
            conn = sqlite3.connect("kadri_final_system.db")
            low_items = conn.execute("SELECT name FROM inventory WHERE qty < 3").fetchall()
            conn.close()
            if low_items:
                lbl_alert.config(text=f"⚠️ Low Stock: {len(low_items)} items need ordering!", fg="red")
            else:
                lbl_alert.config(text="✅ Stock levels normal", fg="#27ae60")

    def refresh_table(query="SELECT * FROM inventory"):
        # مسح الجدول
        for item in tree.get_children(): 
            tree.delete(item)
            
        conn = None
        try:
            conn = sqlite3.connect("kadri_final_system.db", timeout=30)
            cursor = conn.cursor()
            cursor.execute(query)
            
            rows = cursor.fetchall() # جلب البيانات دفعة واحدة
            
            for row in rows:
                try:
                    qty = int(row[4]) if row[4] else 0
                    tag = "low" if qty < 3 else "normal"
                except:
                    tag = "normal"
                tree.insert('', 'end', values=row, tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحديث الجدول:\n{e}")
            
        finally:
            # إغلاق قاعدة البيانات إجبارياً بعد جلب البيانات
            if conn:
                conn.close()
                
        # تحديث الإحصائيات (تُستدعى بعد إغلاق الاتصال لكي لا تتداخل)
        update_stats()

    def quick_search(event=None):
        val = search_var.get()
        refresh_table(f"SELECT * FROM inventory WHERE name LIKE '%{val}%' OR id LIKE '%{val}%' OR project LIKE '%{val}%'")

    def barcode_handler(event=None):
        code = barcode_var.get().strip()
        if code:
            refresh_table(f"SELECT * FROM inventory WHERE id = '{code}'")
            root.after(1000, lambda: barcode_var.set(""))

    def save_data():
        try:
            d = {k: v.get().strip() for k, v in entries.items()}
            if not d['ID'] or not d['Name']: raise ValueError("ID and Name are required")
            conn = sqlite3.connect("kadri_final_system.db")
            conn.execute("INSERT OR REPLACE INTO inventory VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         (d['ID'], d['Name'], d['Model'], d['Brand'], int(d['Qty']), float(d['Price']),
                          d['Dest'], d['Proj'], d['Func'], d['Cat'], d['Prop'], d['Stat']))
            conn.commit(); conn.close()
            log_action("Saved/Updated Item", d['ID'])
            refresh_table()
            messagebox.showinfo("Success", "System Updated Successfully!")
        except Exception as e: messagebox.showerror("Error", f"Input Error: {e}")

    def edit_item_fill():
        selected = tree.selection()
        if not selected: return messagebox.showwarning("Warning", "Select item to edit")
        item_data = tree.item(selected[0], 'values')
        field_keys = ["ID", "Name", "Model", "Brand", "Qty", "Price", "Dest", "Proj", "Func", "Cat", "Prop", "Stat"]
        for i, key in enumerate(field_keys):
            if isinstance(entries[key], ttk.Combobox): entries[key].set(item_data[i])
            else:
                entries[key].delete(0, tk.END)
                entries[key].insert(0, item_data[i])

    def delete_item():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("تنبيه", "الرجاء تحديد عنصر واحد أو أكثر من الجدول لحذفه.")
            return

        confirm = messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف {len(selected_items)} عنصر؟")
        
        if confirm:
            conn = None  # تهيئة المتغير
            try:
                # فتح الاتصال
                conn = sqlite3.connect("kadri_final_system.db", timeout=30)
                cursor = conn.cursor()
                
                for item in selected_items:
                    item_id = tree.item(item, 'values')[0]
                    # تنفيذ الحذف
                    cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
                    
                conn.commit() # تأكيد الحذف
                messagebox.showinfo("نجاح", "تم حذف العناصر المحددة بنجاح.")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء الحذف:\n{e}")
                
            finally:
                # هذه هي الكلمة السحرية التي تحل المشكلة: الإغلاق الإجباري
                if conn:
                    conn.close()
            
            # يتم استدعاء التحديث بعد إغلاق قاعدة البيانات تماماً
            refresh_table()

    def export_excel():
        try:
            fn = f"Export_{datetime.now().strftime('%Y%m%d')}.csv"
            conn = sqlite3.connect("kadri_final_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory")
            rows = cursor.fetchall()
            with open(fn, "w", newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([d[0] for d in cursor.description])
                writer.writerows(rows)
            conn.close()
            messagebox.showinfo("Export", f"Data exported to {fn}")
        except Exception as e: messagebox.showerror("Error", str(e))

    def show_dashboard():
        dash = tk.Toplevel(root)
        dash.title("Inventory Dashboard")
        dash.geometry("600x400")
        dash.configure(bg="white")
        tk.Label(dash, text="Inventory Analytics", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        conn = sqlite3.connect("kadri_final_system.db")
        data = conn.execute("SELECT status, COUNT(*) FROM inventory GROUP BY status").fetchall()
        conn.close()
        for stat, count in data:
            frame = tk.Frame(dash, bg="#f8f9fa", pady=5)
            frame.pack(fill="x", padx=50, pady=2)
            tk.Label(frame, text=f"{stat}:", font=("Arial", 12), bg="#f8f9fa").pack(side="left")
            tk.Label(frame, text=f"{count} items", font=("Arial", 12, "bold"), bg="#f8f9fa", fg="#2980b9").pack(side="right")

    def draw_company_header(canvas_obj, is_landscape=False):
        width_limit = 750 if is_landscape else 550
        y_top = 780 if not is_landscape else 560
        try:
            logo_img = resource_path("logo.png")
            canvas_obj.drawImage(logo_img, 40, y_top-60, width=130, height=65, mask='auto')
        except: pass
        
        canvas_obj.setFillColor(colors.blue)
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawRightString(width_limit, y_top-10, CONFIG['company_name'])
        
        canvas_obj.setFillColor(colors.black)
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawRightString(width_limit, y_top-25, CONFIG['company_subtitle'])
        canvas_obj.drawRightString(width_limit, y_top-37, CONFIG['company_address'])
        canvas_obj.drawRightString(width_limit, y_top-49, f"Mob: {CONFIG['company_phone']}")
        canvas_obj.drawRightString(width_limit, y_top-61, f"Email: {CONFIG['company_email']}")
        
        canvas_obj.setStrokeColor(colors.blue)
        canvas_obj.setLineWidth(1.5)
        canvas_obj.line(40, y_top-75, width_limit, y_top-75)

    def create_invoice_pdf():
        selected = tree.selection()
        if not selected: return messagebox.showwarning("Warning", "Select items")
        fn = f"Invoice_{datetime.now().strftime('%H%M%S')}.pdf"
        c = canvas.Canvas(fn, pagesize=letter)
        draw_company_header(c)
        
        c.setFillColor(colors.darkblue)
        c.setFont("Helvetica-Bold", 18); c.drawCentredString(300, 680, "SALES INVOICE / FACTURE")
        c.setFillColor(colors.black); c.setFont("Helvetica", 10)
        c.drawString(400, 655, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
        c.drawString(400, 640, f"No: #INV{datetime.now().strftime('%y%m%d%H')}")
        y = 600
        headers = ["ID", "Designation", "Model/Brand", "Qty", "Price", "Total"]
        x_pts = [50, 110, 240, 370, 430, 500]
        c.setFillColor(colors.lightgrey); c.rect(40, y-5, 520, 20, fill=1, stroke=0)
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 10)
        for i, h in enumerate(headers): c.drawString(x_pts[i], y, h)
        y -= 25; grand_total = 0; c.setFont("Helvetica", 9)
        for s in selected:
            r = tree.item(s, 'values')
            total = int(r[4]) * float(r[5]); grand_total += total
            c.drawString(50, y, str(r[0])); c.drawString(110, y, str(r[1])[:20])
            c.drawString(240, y, f"{r[2]} / {r[3]}"); c.drawString(370, y, str(r[4]))
            c.drawString(430, y, f"{float(r[5]):,.0f}"); c.drawString(500, y, f"{total:,.0f}")
            y -= 20
        c.line(40, y, 560, y); y -= 30
        c.setFillColor(colors.darkblue); c.setFont("Helvetica-Bold", 12)
        c.drawRightString(550, y, f"Total Amount: {grand_total:,.2f} {CONFIG['currency']}")
        
        conn = sqlite3.connect("kadri_final_system.db")
        conn.execute("INSERT INTO invoices (client,total,date) VALUES (?,?,?)",
                     ("Default Client", grand_total, datetime.now().strftime("%Y-%m-%d")))
        conn.commit(); conn.close()
        c.save(); messagebox.showinfo("Success", f"Invoice saved: {fn}")

    def create_stock_report():
        fn = f"Stock_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        c = canvas.Canvas(fn, pagesize=landscape(letter))
        draw_company_header(c, is_landscape=True)
        c.setFillColor(colors.darkblue); c.setFont("Helvetica-Bold", 18); c.drawCentredString(400, 440, "FULL INVENTORY REPORT")
        y = 400; headers = ["ID", "Name", "Model", "Brand", "Qty", f"Price ({CONFIG['currency']})", "Status"]
        x_pts = [40, 100, 230, 360, 480, 540, 680]
        c.setFillColor(colors.lightgrey); c.rect(30, y-5, 730, 20, fill=1, stroke=0)
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 10)
        for i, h in enumerate(headers): c.drawString(x_pts[i], y, h)
        y -= 25; conn = sqlite3.connect("kadri_final_system.db")
        data = conn.execute("SELECT id, name, model, brand, qty, price, status FROM inventory").fetchall()
        conn.close(); c.setFont("Helvetica", 9)
        for row in data:
            for i, val in enumerate(row):
                text = f"{float(val):,.0f}" if i == 5 else str(val)
                c.drawString(x_pts[i], y, text)
            y -= 15
            if y < 50: c.showPage(); y = 550
        c.save(); messagebox.showinfo("Success", f"Report saved: {fn}")

    # واجهة المخزون
    header = tk.Frame(tab_inventory, bg="#2c3e50", height=120); header.pack(fill="x")
    tk.Label(header, text=CONFIG['company_name'], fg="#f1c40f", bg="#2c3e50", font=("Arial", 28, "bold")).pack(pady=(15,0))
    lbl_stats = tk.Label(header, text="", fg="#ecf0f1", bg="#2c3e50", font=("Arial", 11)); lbl_stats.pack()
    lbl_alert = tk.Label(header, text="", bg="#2c3e50", font=("Arial", 10, "bold")); lbl_alert.pack(pady=5)

    tool_bar = tk.Frame(tab_inventory, bg="#ecf0f1", pady=10); tool_bar.pack(fill="x", padx=20)
    tk.Label(tool_bar, text="🔍 Search:", bg="#ecf0f1", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    search_var = tk.StringVar(); search_ent = tk.Entry(tool_bar, textvariable=search_var, width=35, font=("Arial", 11))
    search_ent.pack(side="left", padx=5); search_ent.bind("<KeyRelease>", quick_search)
    tk.Label(tool_bar, text="   ⚡ BARCODE:", fg="#e74c3c", bg="#ecf0f1", font=("Arial", 10, "bold")).pack(side="left", padx=10)
    barcode_var = tk.StringVar(); barcode_ent = tk.Entry(tool_bar, textvariable=barcode_var, width=20, bg="#fff9c4", font=("Arial", 12, "bold"))
    barcode_ent.pack(side="left"); barcode_ent.bind("<Return>", barcode_handler)

    # إضافة زر الإعدادات الجديد هنا
    tk.Button(tool_bar, text="⚙️ Settings", command=lambda: open_settings_window(root), bg="#34495e", fg="white", font=("Arial", 9, "bold")).pack(side="right", padx=5)
    tk.Button(tool_bar, text="📊 Dashboard", command=show_dashboard, bg="#16a085", fg="white", font=("Arial", 9, "bold")).pack(side="right", padx=5)
    tk.Button(tool_bar, text="📥 Export CSV", command=export_excel, bg="#27ae60", fg="white", font=("Arial", 9, "bold")).pack(side="right", padx=5)
    tk.Button(tool_bar, text="📈 Charts", command=show_chart, bg="#8e44ad", fg="white", font=("Arial", 9, "bold")).pack(side="right", padx=5)
    tk.Button(tool_bar, text="🤖 Smart", command=smart_restock, bg="#e67e22", fg="white", font=("Arial", 9, "bold")).pack(side="right", padx=5)

    input_frame = tk.LabelFrame(tab_inventory, text=" 📝 Inventory Management Entry ", bg="white", font=("Arial", 10, "bold"), padx=15, pady=10); input_frame.pack(fill="x", padx=20, pady=5)
    fields = [("ID", 0, 0), ("Name", 0, 2), ("Model", 0, 4), ("Brand", 0, 6),
              ("Qty", 1, 0), ("Price", 1, 2), ("Dest", 1, 4), ("Proj", 1, 6),
              ("Func", 2, 0), ("Cat", 2, 2), ("Prop", 2, 4), ("Stat", 2, 6)]
    entries = {}
    for k, r, c in fields:
        tk.Label(input_frame, text=k+":", bg="white", font=("Arial", 9, "bold")).grid(row=r, column=c, padx=5, pady=5, sticky="w")
        if k=="Stat":
            ent = ttk.Combobox(input_frame, values=["In Stock", "Out", "Installed", "Repair", "Pending"], width=18)
            ent.set("In Stock")
        else:
            ent = tk.Entry(input_frame, width=22, font=("Arial", 10))
        ent.grid(row=r, column=c+1, padx=5); entries[k] = ent

    tree_frame = tk.Frame(tab_inventory); tree_frame.pack(fill="both", expand=True, padx=20)
    cols = ("id", "name", "model", "brand", "qty", "price", "dest", "proj", "func", "cat", "prop", "stat")
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
    style = ttk.Style(); style.configure("Treeview.Heading", font=("Arial", 10, "bold")); style.configure("Treeview", rowheight=28)
    for col in cols:
        tree.heading(col, text=col.upper())
        tree.column(col, width=110, anchor="center")
    tree.tag_configure("low", background="#ffcccc")
    tree.pack(side="left", fill="both", expand=True)
    sc = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); sc.pack(side="right", fill="y"); tree.config(yscrollcommand=sc.set)

    btn_frame = tk.Frame(tab_inventory, bg="#f4f7f6", pady=20); btn_frame.pack()
    st = {"font": ("Arial", 10, "bold"), "fg": "white", "width": 16, "pady": 10, "bd": 0}
    tk.Button(btn_frame, text="✚ SAVE ITEM", command=save_data, bg="#27ae60", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✏️ EDIT ITEM", command=edit_item_fill, bg="#f39c12", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="📊 STOCK REPORT", command=create_stock_report, bg="#8e44ad", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="📄 PRINT INVOICE", command=create_invoice_pdf, bg="#2980b9", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="🗑 DELETE ITEM", command=delete_item, bg="#c0392b", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="🔄 REFRESH", command=refresh_table, bg="#34495e", **st).pack(side="left", padx=5)


    # =========================================================
    # التبويب الثاني: إدارة الصيانة والعقود
    # =========================================================
    
    maint_header = tk.Frame(tab_maintenance, bg="#34495e", height=80); maint_header.pack(fill="x")
    tk.Label(maint_header, text="نظام إدارة عقود الصيانة والمهندسين", fg="white", bg="#34495e", font=("Arial", 20, "bold")).pack(pady=20)

    def refresh_contracts():
        for i in tree_contracts.get_children(): tree_contracts.delete(i)
        conn = sqlite3.connect("kadri_final_system.db")
        for row in conn.execute("SELECT * FROM contracts").fetchall():
            tree_contracts.insert('', 'end', values=row)
        conn.close()

    def save_contract():
        try:
            conn = sqlite3.connect("kadri_final_system.db")
            conn.execute("INSERT OR REPLACE INTO contracts VALUES (?,?,?,?,?,?,?)",
                         (c_id.get(), c_client.get(), c_addr.get(), c_type.get(), c_start.get(), c_end.get(), c_stat.get()))
            conn.commit(); conn.close()
            refresh_contracts()
            messagebox.showinfo("Success", "Contract Saved!")
        except Exception as e: messagebox.showerror("Error", str(e))

    contract_frame = tk.LabelFrame(tab_maintenance, text=" 📝 Contract Entry ", bg="white", font=("Arial", 10, "bold"), padx=15, pady=10)
    contract_frame.pack(fill="x", padx=20, pady=10)

    tk.Label(contract_frame, text="Contract ID:", bg="white").grid(row=0, column=0, padx=5, pady=5)
    c_id = tk.Entry(contract_frame); c_id.grid(row=0, column=1)
    
    tk.Label(contract_frame, text="Client Name:", bg="white").grid(row=0, column=2, padx=5, pady=5)
    c_client = tk.Entry(contract_frame); c_client.grid(row=0, column=3)
    
    tk.Label(contract_frame, text="Elevator Brand/Type:", bg="white").grid(row=0, column=4, padx=5, pady=5)
    c_type = ttk.Combobox(contract_frame, values=["Montanari", "Fermator", "Orona", "Sodimas", "Other"])
    c_type.grid(row=0, column=5)

    tk.Label(contract_frame, text="Address:", bg="white").grid(row=1, column=0, padx=5, pady=5)
    c_addr = tk.Entry(contract_frame); c_addr.grid(row=1, column=1)

    tk.Label(contract_frame, text="Start Date:", bg="white").grid(row=1, column=2, padx=5, pady=5)
    c_start = tk.Entry(contract_frame); c_start.grid(row=1, column=3)
    c_start.insert(0, datetime.now().strftime("%Y-%m-%d"))

    tk.Label(contract_frame, text="End Date:", bg="white").grid(row=1, column=4, padx=5, pady=5)
    c_end = tk.Entry(contract_frame); c_end.grid(row=1, column=5)

    tk.Label(contract_frame, text="Status:", bg="white").grid(row=0, column=6, padx=5, pady=5)
    c_stat = ttk.Combobox(contract_frame, values=["Active", "Expired", "Suspended"])
    c_stat.set("Active"); c_stat.grid(row=0, column=7)

    tk.Button(contract_frame, text="Save Contract", bg="#2980b9", fg="white", command=save_contract).grid(row=1, column=7, pady=5)

    tree_c_frame = tk.Frame(tab_maintenance)
    tree_c_frame.pack(fill="both", expand=True, padx=20, pady=5)
    
    cols_c = ("ID", "Client", "Address", "Elevator Type", "Start Date", "End Date", "Status")
    tree_contracts = ttk.Treeview(tree_c_frame, columns=cols_c, show='headings')
    for col in cols_c:
        tree_contracts.heading(col, text=col)
        tree_contracts.column(col, anchor="center")
    tree_contracts.pack(side="left", fill="both", expand=True)

    refresh_table()
    refresh_contracts()
    root.mainloop()

# --- 3. Login Window ---

def login(event=None):
    username = user_ent.get()
    password = l_ent.get()
    
    # تشفير كلمة المرور المُدخلة للمقارنة
    hashed_input_pw = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect("kadri_final_system.db")
    # التعديل هنا: نقارن بكلمة المرور المشفرة (hashed_input_pw) 
    # وأيضاً بالكلمة العادية (password) في حال كانت قاعدة البيانات قديمة ولم تتحدث بعد
    res = conn.execute("SELECT role FROM users WHERE username=? AND (password=? OR password=?)", 
                       (username, hashed_input_pw, password)).fetchone()
    conn.close()
    
    if res:
        l_win.destroy()
        open_main_app()
    else:
        messagebox.showerror("Access Denied", "Incorrect credentials")

if __name__ == "__main__":
    # --- تشغيل دالة التحقق من الترخيص أولاً ---
    check_license()
    # ----------------------------------------
    
    auto_backup()
    prepare_icon()
    init_db()

    l_win = tk.Tk()
    l_win.title(f"{CONFIG['company_name']} SECURITY")
    l_win.geometry("450x650")
    l_win.configure(bg="#2c3e50")

    try: l_win.iconbitmap(resource_path("logo.ico"))
    except: pass

    try:
        img_login = Image.open(resource_path("elevator.png")).resize((320, 260), Image.Resampling.LANCZOS)
        photo_login = ImageTk.PhotoImage(img_login)
        tk.Label(l_win, image=photo_login, bg="#2c3e50").pack(pady=30)
    except: pass

    tk.Label(l_win, text="USERNAME", fg="#bdc3c7", bg="#2c3e50", font=("Arial", 10, "bold")).pack()
    user_ent = tk.Entry(l_win, justify="center", font=("Arial", 18))
    user_ent.pack(pady=5, ipady=5)
    user_ent.insert(0, "admin")

    tk.Label(l_win, text="ENTER SYSTEM PASSWORD", fg="#f1c40f", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=(15,0))
    l_ent = tk.Entry(l_win, show="*", justify="center", font=("Arial", 22), bg="#ecf0f1", bd=0)
    l_ent.pack(pady=10, ipady=5)
    l_ent.focus()
    l_ent.bind("<Return>", login)

    tk.Button(l_win, text="UNLOCK SYSTEM", command=login, bg="#f1c40f", fg="#2c3e50", width=25, height=2, font=("Arial", 11, "bold"), bd=0).pack(pady=25)
    
    tk.Label(l_win, text=f"{CONFIG['company_name']} - Official ERP {CONFIG['app_version']}", fg="#bdc3c7", bg="#2c3e50", font=("Arial", 8)).pack(side="bottom", pady=10)

    l_win.mainloop()
