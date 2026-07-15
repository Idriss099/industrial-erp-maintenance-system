import csv
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from tkinter import messagebox
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from database import execute_query
from utils import CONFIG, resource_path


def show_chart():
    data = execute_query("SELECT name, qty FROM inventory")
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


def draw_company_header(canvas_obj, is_landscape=False):
    width_limit = 750 if is_landscape else 550
    y_top = 780 if not is_landscape else 560
    try:
        logo_img = resource_path("logo.png")
        canvas_obj.drawImage(logo_img, 40, y_top - 60, width=130, height=65, mask='auto')
    except:
        pass

    canvas_obj.setFillColor(colors.blue)
    canvas_obj.setFont("Helvetica-Bold", 14)
    canvas_obj.drawRightString(width_limit, y_top - 10, CONFIG['company_name'])

    canvas_obj.setFillColor(colors.black)
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawRightString(width_limit, y_top - 25, CONFIG['company_subtitle'])
    canvas_obj.drawRightString(width_limit, y_top - 37, CONFIG['company_address'])
    canvas_obj.drawRightString(width_limit, y_top - 49, f"Mob: {CONFIG['company_phone']}")
    canvas_obj.drawRightString(width_limit, y_top - 61, f"Email: {CONFIG['company_email']}")

    canvas_obj.setStrokeColor(colors.blue)
    canvas_obj.setLineWidth(1.5)
    canvas_obj.line(40, y_top - 75, width_limit, y_top - 75)


def create_invoice_pdf(selected_rows):
    """توليد الفاتورة واستقبال مصفوفة البيانات بدلاً من ويدجيت الواجهة مباشرة لضمان الفصل التام."""
    fn = f"Invoice_{datetime.now().strftime('%H%M%S')}.pdf"
    c = canvas.Canvas(fn, pagesize=letter)
    draw_company_header(c)

    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 18);
    c.drawCentredString(300, 680, "SALES INVOICE / FACTURE")
    c.setFillColor(colors.black);
    c.setFont("Helvetica", 10)
    c.drawString(400, 655, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(400, 640, f"No: #INV{datetime.now().strftime('%y%m%d%H')}")
    y = 600
    headers = ["ID", "Designation", "Model/Brand", "Qty", "Price", "Total"]
    x_pts = [50, 110, 240, 370, 430, 500]
    c.setFillColor(colors.lightgrey);
    c.rect(40, y - 5, 520, 20, fill=1, stroke=0)
    c.setFillColor(colors.black);
    c.setFont("Helvetica-Bold", 10)
    for i, h in enumerate(headers): c.drawString(x_pts[i], y, h)

    y -= 25;
    grand_total = 0;
    c.setFont("Helvetica", 9)
    for r in selected_rows:
        total = int(r[4]) * float(r[5]);
        grand_total += total
        c.drawString(50, y, str(r[0]));
        c.drawString(110, y, str(r[1])[:20])
        c.drawString(240, y, f"{r[2]} / {r[3]}");
        c.drawString(370, y, str(r[4]))
        c.drawString(430, y, f"{float(r[5]):,.0f}");
        c.drawString(500, y, f"{total:,.0f}")
        y -= 20

    c.line(40, y, 560, y);
    y -= 30
    c.setFillColor(colors.darkblue);
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(550, y, f"Total Amount: {grand_total:,.2f} {CONFIG['currency']}")

    execute_query("INSERT INTO invoices (client,total,date) VALUES (?,?,?)",
                  ("Default Client", grand_total, datetime.now().strftime("%Y-%m-%d")), is_select=False)
    c.save()
    messagebox.showinfo("Success", f"Invoice saved: {fn}")


def create_stock_report():
    fn = f"Stock_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
    c = canvas.Canvas(fn, pagesize=landscape(letter))
    draw_company_header(c, is_landscape=True)
    c.setFillColor(colors.darkblue);
    c.setFont("Helvetica-Bold", 18);
    c.drawCentredString(400, 440, "FULL INVENTORY REPORT")
    y = 400;
    headers = ["ID", "Name", "Model", "Brand", "Qty", f"Price ({CONFIG['currency']})", "Status"]
    x_pts = [40, 100, 230, 360, 480, 540, 680]
    c.setFillColor(colors.lightgrey);
    c.rect(30, y - 5, 730, 20, fill=1, stroke=0)
    c.setFillColor(colors.black);
    c.setFont("Helvetica-Bold", 10)
    for i, h in enumerate(headers): c.drawString(x_pts[i], y, h)
    y -= 25

    data = execute_query("SELECT id, name, model, brand, qty, price, status FROM inventory")
    if data:
        c.setFont("Helvetica", 9)
        for row in data:
            for i, val in enumerate(row):
                text = f"{float(val):,.0f}" if i == 5 else str(val)
                c.drawString(x_pts[i], y, text)
            y -= 15
            if y < 50: c.showPage(); y = 550
    c.save();
    messagebox.showinfo("Success", f"Report saved: {fn}")


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
    except Exception as e:
        messagebox.showerror("Error", str(e))
