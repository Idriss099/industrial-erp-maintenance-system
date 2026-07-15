import tkinter as tk
from tkinter import messagebox, ttk
import ctypes
import hashlib
import json
from datetime import datetime
from PIL import Image, ImageTk

from database import execute_query
from utils import CONFIG, resource_path
from reports import show_chart, create_invoice_pdf, create_stock_report, export_excel


def open_settings_window(parent):
    set_win = tk.Toplevel(parent)
    set_win.title("⚙️ إعدادات النظام (System Settings)")
    set_win.geometry("550x700")
    set_win.configure(bg="#f4f7f6")

    tk.Label(set_win, text="تعديل بيانات الشركة والنظام", font=("Arial", 16, "bold"), bg="#f4f7f6", fg="#2c3e50").pack(
        pady=10)

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
        tk.Label(form_frame, text=label_text, font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=i, column=1,
                                                                                             sticky="e", padx=10,
                                                                                             pady=5)
        ent = tk.Entry(form_frame, width=35, font=("Arial", 11))
        ent.insert(0, CONFIG.get(key, ""))
        ent.grid(row=i, column=0, padx=10, pady=5)
        entries[key] = ent

    def save_new_settings():
        global CONFIG
        new_data = {key: ent.get().strip() for key, ent in entries.items()}
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        CONFIG.update(new_data)
        messagebox.showinfo("تم الحفظ", "✅ تم حفظ الإعدادات بنجاح.", parent=set_win)

    tk.Button(set_win, text="💾 حفظ إعدادات الشركة", command=save_new_settings, bg="#27ae60", fg="white",
              font=("Arial", 11, "bold"), width=20).pack(pady=10)

    ttk.Separator(set_win, orient='horizontal').pack(fill='x', pady=10, padx=20)
    tk.Label(set_win, text="تغيير بيانات تسجيل الدخول", font=("Arial", 14, "bold"), bg="#f4f7f6", fg="#c0392b").pack(
        pady=5)

    cred_frame = tk.Frame(set_win, bg="#f4f7f6")
    cred_frame.pack(pady=5)

    tk.Label(cred_frame, text="كلمة المرور الحالية:", font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=0, column=1,
                                                                                                     sticky="e",
                                                                                                     padx=10, pady=5)
    old_pass_ent = tk.Entry(cred_frame, width=25, font=("Arial", 11), show="*")
    old_pass_ent.grid(row=0, column=0, padx=10, pady=5)

    tk.Label(cred_frame, text="اسم المستخدم الجديد:", font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=1, column=1,
                                                                                                     sticky="e",
                                                                                                     padx=10, pady=5)
    new_user_ent = tk.Entry(cred_frame, width=25, font=("Arial", 11))
    new_user_ent.grid(row=1, column=0, padx=10, pady=5)

    tk.Label(cred_frame, text="كلمة المرور الجديدة:", font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=2, column=1,
                                                                                                     sticky="e",
                                                                                                     padx=10, pady=5)
    new_pass_ent = tk.Entry(cred_frame, width=25, font=("Arial", 11), show="*")
    new_pass_ent.grid(row=2, column=0, padx=10, pady=5)

    tk.Label(cred_frame, text="تأكيد كلمة المرور:", font=("Arial", 11, "bold"), bg="#f4f7f6").grid(row=3, column=1,
                                                                                                   sticky="e", padx=10,
                                                                                                   pady=5)
    conf_pass_ent = tk.Entry(cred_frame, width=25, font=("Arial", 11), show="*")
    conf_pass_ent.grid(row=3, column=0, padx=10, pady=5)

    def save_credentials():
        op = old_pass_ent.get().strip()
        nu = new_user_ent.get().strip()
        np = new_pass_ent.get().strip()
        cp = conf_pass_ent.get().strip()

        if not op or not nu or not np: return messagebox.showwarning("تحذير", "يرجى ملء جميع الحقول!", parent=set_win)
        if np != cp: return messagebox.showerror("خطأ", "كلمات المرور غير متطابقة!", parent=set_win)

        hashed_op = hashlib.sha256(op.encode()).hexdigest()
        result = execute_query("SELECT password FROM users WHERE role='ADMIN'", fetchone=True)

        if result and result[0] == hashed_op:
            hashed_np = hashlib.sha256(np.encode()).hexdigest()
            execute_query("UPDATE users SET username=?, password=? WHERE role='ADMIN'", (nu, hashed_np),
                          is_select=False)
            messagebox.showinfo("نجاح", "✅ تم تحديث بيانات الدخول بنجاح!", parent=set_win)
            for entry in [old_pass_ent, new_user_ent, new_pass_ent, conf_pass_ent]: entry.delete(0, tk.END)
        else:
            messagebox.showerror("خطأ", "❌ كلمة المرور الحالية غير صحيحة!", parent=set_win)

    tk.Button(set_win, text="🔐 تحديث بيانات الدخول", command=save_credentials, bg="#c0392b", fg="white",
              font=("Arial", 11, "bold"), width=20).pack(pady=10)


def open_main_app():
    root = tk.Tk()
    try:
        myappid = 'kadri.ascenseurs.erp.v20'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    root.title(f"{CONFIG['company_name']} - Enterprise ERP {CONFIG['app_version']}")
    root.geometry("1550x900")
    root.configure(bg="#f4f7f6")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_inventory = tk.Frame(notebook, bg="#f4f7f6")
    tab_maintenance = tk.Frame(notebook, bg="#f4f7f6")

    notebook.add(tab_inventory, text="📦 إدارة المخزون والمبيعات (Inventory & Sales)")
    notebook.add(tab_maintenance, text="🛠️ إدارة الصيانة والعقود (Maintenance & Contracts)")

    def log_action(action, item_id):
        execute_query("INSERT INTO logs VALUES (?,?,?,?)",
                      ("Admin", action, item_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                      is_select=False)

    def update_stats():
        res = execute_query("SELECT SUM(qty), SUM(qty * price), COUNT(*) FROM inventory", fetchone=True)
        if res:
            q, v, c = (res[0] or 0), (res[1] or 0), (res[2] or 0)
            lbl_stats.config(
                text=f"📊 Items: {c} | Units: {int(q)} | Inventory Value: {float(v):,.2f} {CONFIG['currency']}")

            if q > 0:
                low_items = execute_query("SELECT name FROM inventory WHERE qty < 3")
                if low_items:
                    lbl_alert.config(text=f"⚠️ Low Stock: {len(low_items)} items need ordering!", fg="red")
                else:
                    lbl_alert.config(text="✅ Stock levels normal", fg="#27ae60")

    def refresh_table(query="SELECT * FROM inventory", params=()):
        for item in tree.get_children():
            tree.delete(item)

        rows = execute_query(query, params)
        if rows:
            for row in rows:
                try:
                    qty = int(row[4]) if row[4] else 0
                    tag = "low" if qty < 3 else "normal"
                except:
                    tag = "normal"
                tree.insert('', 'end', values=row, tags=(tag,))
        update_stats()

    def quick_search(event=None):
        val = search_var.get()
        query = "SELECT * FROM inventory WHERE name LIKE ? OR id LIKE ? OR project LIKE ?"
        params = (f"%{val}%", f"%{val}%", f"%{val}%")
        refresh_table(query, params)

    def barcode_handler(event=None):
        code = barcode_var.get().strip()
        if code:
            refresh_table("SELECT * FROM inventory WHERE id = ?", (code,))
            root.after(1000, lambda: barcode_var.set(""))

    def save_data():
        try:
            d = {k: v.get().strip() for k, v in entries.items()}
            if not d['ID'] or not d['Name']: raise ValueError("ID and Name are required")

            query = "INSERT OR REPLACE INTO inventory VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
            params = (d['ID'], d['Name'], d['Model'], d['Brand'], int(d['Qty']), float(d['Price']),
                      d['Dest'], d['Proj'], d['Func'], d['Cat'], d['Prop'], d['Stat'])

            execute_query(query, params, is_select=False)
            log_action("Saved/Updated Item", d['ID'])
            refresh_table()
            messagebox.showinfo("Success", "System Updated Successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Input Error: {e}")

    def edit_item_fill():
        selected = tree.selection()
        if not selected: return messagebox.showwarning("Warning", "Select item to edit")
        item_data = tree.item(selected[0], 'values')
        field_keys = ["ID", "Name", "Model", "Brand", "Qty", "Price", "Dest", "Proj", "Func", "Cat", "Prop", "Stat"]
        for i, key in enumerate(field_keys):
            if isinstance(entries[key], ttk.Combobox):
                entries[key].set(item_data[i])
            else:
                entries[key].delete(0, tk.END)
                entries[key].insert(0, item_data[i])

    def delete_item():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("تنبيه", "الرجاء تحديد عنصر واحد أو أكثر لحذفه.")
            return

        confirm = messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف {len(selected_items)} عنصر؟")
        if confirm:
            ids_to_delete = [(tree.item(item, 'values')[0],) for item in selected_items]
            execute_query("DELETE FROM inventory WHERE id=?", ids_to_delete, is_select=False, executemany=True)
            refresh_table()

    def trigger_invoice():
        selected = tree.selection()
        if not selected:
            return messagebox.showwarning("Warning", "Select items first")
        # استخلاص مصفوفة القيم وتمريرها للدالة المفصولة لكي لا نمرر عناصر الواجهة مباشرة
        selected_rows = [tree.item(s, 'values') for s in selected]
        create_invoice_pdf(selected_rows)

    def smart_restock():
        data = execute_query("SELECT name, qty FROM inventory")
        if data:
            low = [d[0] for d in data if d[1] < 5]
            if low:
                messagebox.showinfo("Smart System", "Restock needed:\n" + "\n".join(low))
            else:
                messagebox.showinfo("Smart System", "Stock is OK")

    # واجهة المخزون
    header = tk.Frame(tab_inventory, bg="#2c3e50", height=120);
    header.pack(fill="x")
    tk.Label(header, text=CONFIG['company_name'], fg="#f1c40f", bg="#2c3e50", font=("Arial", 28, "bold")).pack(
        pady=(15, 0))
    lbl_stats = tk.Label(header, text="", fg="#ecf0f1", bg="#2c3e50", font=("Arial", 11));
    lbl_stats.pack()
    lbl_alert = tk.Label(header, text="", bg="#2c3e50", font=("Arial", 10, "bold"));
    lbl_alert.pack(pady=5)

    tool_bar = tk.Frame(tab_inventory, bg="#ecf0f1", pady=10);
    tool_bar.pack(fill="x", padx=20)
    tk.Label(tool_bar, text="🔍 Search:", bg="#ecf0f1", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    search_var = tk.StringVar();
    search_ent = tk.Entry(tool_bar, textvariable=search_var, width=35, font=("Arial", 11))
    search_ent.pack(side="left", padx=5);
    search_ent.bind("<KeyRelease>", quick_search)
    tk.Label(tool_bar, text="   ⚡ BARCODE:", fg="#e74c3c", bg="#ecf0f1", font=("Arial", 10, "bold")).pack(side="left",
                                                                                                          padx=10)
    barcode_var = tk.StringVar();
    barcode_ent = tk.Entry(tool_bar, textvariable=barcode_var, width=20, bg="#fff9c4", font=("Arial", 12, "bold"))
    barcode_ent.pack(side="left");
    barcode_ent.bind("<Return>", barcode_handler)

    tk.Button(tool_bar, text="⚙️ Settings", command=lambda: open_settings_window(root), bg="#34495e", fg="white",
              font=("Arial", 9, "bold")).pack(side="right", padx=5)
    tk.Button(tool_bar, text="📊 Dashboard",
              command=lambda: messagebox.showinfo("Dashboard", "Dynamic Analytics Ready!"), bg="#16a085", fg="white",
              font=("Arial", 9, "bold")).pack(side="right", padx=5)
    tk.Button(tool_bar, text="📥 Export CSV", command=export_excel, bg="#27ae60", fg="white",
              font=("Arial", 9, "bold")).pack(side="right", padx=5)
    tk.Button(tool_bar, text="📈 Charts", command=show_chart, bg="#8e44ad", fg="white", font=("Arial", 9, "bold")).pack(
        side="right", padx=5)
    tk.Button(tool_bar, text="🤖 Smart", command=smart_restock, bg="#e67e22", fg="white",
              font=("Arial", 9, "bold")).pack(side="right", padx=5)

    input_frame = tk.LabelFrame(tab_inventory, text=" 📝 Inventory Management Entry ", bg="white",
                                font=("Arial", 10, "bold"), padx=15, pady=10);
    input_frame.pack(fill="x", padx=20, pady=5)
    fields = [("ID", 0, 0), ("Name", 0, 2), ("Model", 0, 4), ("Brand", 0, 6),
              ("Qty", 1, 0), ("Price", 1, 2), ("Dest", 1, 4), ("Proj", 1, 6),
              ("Func", 2, 0), ("Cat", 2, 2), ("Prop", 2, 4), ("Stat", 2, 6)]
    entries = {}
    for k, r, c in fields:
        tk.Label(input_frame, text=k + ":", bg="white", font=("Arial", 9, "bold")).grid(row=r, column=c, padx=5, pady=5,
                                                                                        sticky="w")
        if k == "Stat":
            ent = ttk.Combobox(input_frame, values=["In Stock", "Out", "Installed", "Repair", "Pending"], width=18)
            ent.set("In Stock")
        else:
            ent = tk.Entry(input_frame, width=22, font=("Arial", 10))
        ent.grid(row=r, column=c + 1, padx=5);
        entries[k] = ent

    tree_frame = tk.Frame(tab_inventory);
    tree_frame.pack(fill="both", expand=True, padx=20)
    cols = ("id", "name", "model", "brand", "qty", "price", "dest", "proj", "func", "cat", "prop", "stat")
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
    style = ttk.Style();
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"));
    style.configure("Treeview", rowheight=28)
    for col in cols:
        tree.heading(col, text=col.upper())
        tree.column(col, width=110, anchor="center")
    tree.tag_configure("low", background="#ffcccc")
    tree.pack(side="left", fill="both", expand=True)
    sc = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview);
    sc.pack(side="right", fill="y");
    tree.config(yscrollcommand=sc.set)

    btn_frame = tk.Frame(tab_inventory, bg="#f4f7f6", pady=20);
    btn_frame.pack()
    st = {"font": ("Arial", 10, "bold"), "fg": "white", "width": 16, "pady": 10, "bd": 0}
    tk.Button(btn_frame, text="✚ SAVE ITEM", command=save_data, bg="#27ae60", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✏️ EDIT ITEM", command=edit_item_fill, bg="#f39c12", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="📊 STOCK REPORT", command=create_stock_report, bg="#8e44ad", **st).pack(side="left",
                                                                                                      padx=5)
    tk.Button(btn_frame, text="📄 PRINT INVOICE", command=trigger_invoice, bg="#2980b9", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="🗑 DELETE ITEM", command=delete_item, bg="#c0392b", **st).pack(side="left", padx=5)
    tk.Button(btn_frame, text="🔄 REFRESH", command=refresh_table, bg="#34495e", **st).pack(side="left", padx=5)

    # التبويب الثاني
    maint_header = tk.Frame(tab_maintenance, bg="#34495e", height=80);
    maint_header.pack(fill="x")
    tk.Label(maint_header, text="نظام إدارة عقود الصيانة والمهندسين", fg="white", bg="#34495e",
             font=("Arial", 20, "bold")).pack(pady=20)

    def refresh_contracts():
        for i in tree_contracts.get_children(): tree_contracts.delete(i)
        rows = execute_query("SELECT * FROM contracts")
        if rows:
            for row in rows:
                tree_contracts.insert('', 'end', values=row)

    def save_contract():
        try:
            query = "INSERT OR REPLACE INTO contracts VALUES (?,?,?,?,?,?,?)"
            params = (c_id.get(), c_client.get(), c_addr.get(), c_type.get(), c_start.get(), c_end.get(), c_stat.get())
            execute_query(query, params, is_select=False)
            refresh_contracts()
            messagebox.showinfo("Success", "Contract Saved!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    contract_frame = tk.LabelFrame(tab_maintenance, text=" 📝 Contract Entry ", bg="white", font=("Arial", 10, "bold"),
                                   padx=15, pady=10)
    contract_frame.pack(fill="x", padx=20, pady=10)

    tk.Label(contract_frame, text="Contract ID:", bg="white").grid(row=0, column=0, padx=5, pady=5)
    c_id = tk.Entry(contract_frame);
    c_id.grid(row=0, column=1)

    tk.Label(contract_frame, text="Client Name:", bg="white").grid(row=0, column=2, padx=5, pady=5)
    c_client = tk.Entry(contract_frame);
    c_client.grid(row=0, column=3)

    tk.Label(contract_frame, text="Elevator Brand/Type:", bg="white").grid(row=0, column=4, padx=5, pady=5)
    c_type = ttk.Combobox(contract_frame, values=["Montanari", "Fermator", "Orona", "Sodimas", "Other"])
    c_type.grid(row=0, column=5)

    tk.Label(contract_frame, text="Address:", bg="white").grid(row=1, column=0, padx=5, pady=5)
    c_addr = tk.Entry(contract_frame);
    c_addr.grid(row=1, column=1)

    tk.Label(contract_frame, text="Start Date:", bg="white").grid(row=1, column=2, padx=5, pady=5)
    c_start = tk.Entry(contract_frame);
    c_start.grid(row=1, column=3)
    c_start.insert(0, datetime.now().strftime("%Y-%m-%d"))

    tk.Label(contract_frame, text="End Date:", bg="white").grid(row=1, column=4, padx=5, pady=5)
    c_end = tk.Entry(contract_frame);
    c_end.grid(row=1, column=5)

    tk.Label(contract_frame, text="Status:", bg="white").grid(row=0, column=6, padx=5, pady=5)
    c_stat = ttk.Combobox(contract_frame, values=["Active", "Expired", "Suspended"])
    c_stat.set("Active");
    c_stat.grid(row=0, column=7)

    tk.Button(contract_frame, text="Save Contract", bg="#2980b9", fg="white", command=save_contract).grid(row=1,
                                                                                                          column=7,
                                                                                                          pady=5)

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


def show_login_window():
    global l_win, user_ent, l_ent
    l_win = tk.Tk()
    l_win.title(f"{CONFIG['company_name']} SECURITY")
    l_win.geometry("450x650")
    l_win.configure(bg="#2c3e50")

    try:
        l_win.iconbitmap(resource_path("logo.ico"))
    except:
        pass

    try:
        # منع مشكلة الـ Garbage Collection للصور في Tkinter عن طريق حفظ مرجع محلي
        img_login = Image.open(resource_path("elevator.png")).resize((320, 260), Image.Resampling.LANCZOS)
        photo_login = ImageTk.PhotoImage(img_login)
        lbl_img = tk.Label(l_win, image=photo_login, bg="#2c3e50")
        lbl_img.image = photo_login
        lbl_img.pack(pady=30)
    except Exception as e:
        print("Login image load skipped:", e)

    tk.Label(l_win, text="USERNAME", fg="#bdc3c7", bg="#2c3e50", font=("Arial", 10, "bold")).pack()
    user_ent = tk.Entry(l_win, justify="center", font=("Arial", 18))
    user_ent.pack(pady=5, ipady=5)
    user_ent.insert(0, "admin")

    tk.Label(l_win, text="ENTER SYSTEM PASSWORD", fg="#f1c40f", bg="#2c3e50", font=("Arial", 12, "bold")).pack(
        pady=(15, 0))
    l_ent = tk.Entry(l_win, show="*", justify="center", font=("Arial", 22), bg="#ecf0f1", bd=0)
    l_ent.pack(pady=10, ipady=5)
    l_ent.focus()

    def trigger_login(event=None):
        username = user_ent.get()
        password = l_ent.get()
        hashed_input_pw = hashlib.sha256(password.encode()).hexdigest()

        query = "SELECT role FROM users WHERE username=? AND (password=? OR password=?)"
        res = execute_query(query, (username, hashed_input_pw, password), fetchone=True)

        if res:
            l_win.destroy()
            open_main_app()
        else:
            messagebox.showerror("Access Denied", "Incorrect credentials")

    l_ent.bind("<Return>", trigger_login)

    tk.Button(l_win, text="UNLOCK SYSTEM", command=trigger_login, bg="#f1c40f", fg="#2c3e50", width=25, height=2,
              font=("Arial", 11, "bold"), bd=0).pack(pady=25)
    tk.Label(l_win, text=f"{CONFIG['company_name']} - Official ERP {CONFIG['app_version']}", fg="#bdc3c7", bg="#2c3e50",
             font=("Arial", 8)).pack(side="bottom", pady=10)

    l_win.mainloop()
