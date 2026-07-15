import sys
from utils import check_license, prepare_icon
from database import init_db, auto_backup
from gui import show_login_window


def main():
    # 1. فحص الترخيص أولاً
    check_license()

    # 2. أخذ نسخة احتياطية من قاعدة البيانات
    auto_backup()

    # 3. تجهيز أيقونة البرنامج
    prepare_icon()

    # 4. تهيئة قاعدة البيانات والجداول
    init_db()

    # 5. تشغيل واجهة تسجيل الدخول
    show_login_window()


if __name__ == "__main__":
    main()
