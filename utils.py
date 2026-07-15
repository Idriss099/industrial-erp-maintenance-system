import os
import sys
import json
import uuid
import hashlib
import tkinter as tk
from tkinter import messagebox
from PIL import Image

SECRET_SALT = "KADRI_ASCENSEURS_2026_PRO_SECURE_KEY_99"


def load_config():
    config_file = "config.json"
    default_data = {
        "company_name": "SARL KADRI ASCENSEURS",
        "company_subtitle": "Installation, Maintenance et Modernisation d'Ascenseurs",
        "company_address": "309 Rue Freres Zedri, Beni Tamou, Blida",
        "company_phone": "+213 (0) 557 20 79 43 / 0799 06 07 38",
        "company_email": "Kadri.ascenseurs@gmail.com",
        "app_version": "v20.0 PRO",
        "currency": "DA"
    }

    if not os.path.exists(config_file):
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default_data
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return default_data


CONFIG = load_config()


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
    except:
        pass


def check_license():
    device_id = str(uuid.getnode()).upper()
    raw_key = device_id + SECRET_SALT
    expected_key = hashlib.sha256(raw_key.encode()).hexdigest()[:20].upper()
    license_file = "license.dat"

    if os.path.exists(license_file):
        try:
            with open(license_file, "r") as f:
                if f.read().strip() == expected_key:
                    return
        except:
            pass

    show_activation_window(device_id, expected_key, license_file)


def show_activation_window(device_id, expected_key, license_file):
    act_win = tk.Tk()
    act_win.title("تفعيل نظام ERP - SARL KADRI ASCENSEURS")
    act_win.geometry("550x400")
    act_win.configure(bg="#2c3e50")

    tk.Label(act_win, text="🔒 النظام غير مفعل", fg="#e74c3c", bg="#2c3e50", font=("Arial", 20, "bold")).pack(
        pady=(20, 5))
    tk.Label(act_win, text="يرجى إرسال (كود الجهاز) إلى مطور النظام للحصول على مفتاح التفعيل.", fg="#ecf0f1",
             bg="#2c3e50", font=("Arial", 11)).pack(pady=5)

    tk.Label(act_win, text="كود الجهاز (Device ID):", fg="#f1c40f", bg="#2c3e50", font=("Arial", 12, "bold")).pack(
        pady=(15, 0))
    id_entry = tk.Entry(act_win, font=("Arial", 14), justify="center", width=30, bg="#ecf0f1", fg="#2c3e50")
    id_entry.insert(0, device_id)
    id_entry.config(state="readonly")
    id_entry.pack(pady=5)

    tk.Label(act_win, text="أدخل مفتاح التفعيل (Activation Key):", fg="#f1c40f", bg="#2c3e50",
             font=("Arial", 12, "bold")).pack(pady=(20, 0))
    key_entry = tk.Entry(act_win, font=("Arial", 16), justify="center", width=25)
    key_entry.pack(pady=10)

    def attempt_activation():
        entered_key = key_entry.get().strip().upper()
        if entered_key == expected_key:
            with open(license_file, "w") as f:
                f.write(entered_key)
            messagebox.showinfo("نجاح", "✅ تم تفعيل البرنامج بنجاح!", parent=act_win)
            act_win.destroy()
        else:
            messagebox.showerror("خطأ", "❌ مفتاح التفعيل غير صحيح!", parent=act_win)

    tk.Button(act_win, text="تفعيل (ACTIVATE)", command=attempt_activation, bg="#27ae60", fg="white",
              font=("Arial", 14, "bold"), width=20).pack(pady=15)
    act_win.mainloop()

    if os.path.exists(license_file):
        with open(license_file, "r") as f:
            if f.read().strip() == expected_key:
                return
    sys.exit()
