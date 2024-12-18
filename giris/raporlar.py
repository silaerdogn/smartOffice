import mysql.connector
from datetime import datetime, timedelta
from tabulate import tabulate

def connect_db():
    return mysql.connector.connect(
   
    'host': '....',
    'user': '....',
    'password': '....',
    'database': '....'

    )

def daily_report(date=None):
    if date is None:
        date = datetime.now().date()
    
    conn = connect_db()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        employee_name,
        DATE_FORMAT(MIN(entry_time), '%H:%i:%s') as ilk_giris,
        status,
        COUNT(*) as giris_sayisi
    FROM employee_entries
    WHERE DATE(entry_time) = '{}'
    GROUP BY employee_name, status
    ORDER BY employee_name, ilk_giris
    """.format(date)
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print(f"\n{date} tarihinde hiç giriş kaydı bulunmamaktadır.")
        return
    
    headers = ["Çalışan", "İlk Giriş", "Durum", "Giriş Sayısı"]
    print(f"\n=== GÜNLÜK RAPOR: {date} ===")
    print(tabulate(results, headers=headers, tablefmt="grid"))
    
    conn.close()

def weekly_report():
    conn = connect_db()
    cursor = conn.cursor()
    
    one_week_ago = datetime.now() - timedelta(days=7)
    
    query = """
    SELECT 
        DATE(entry_time) as tarih,
        employee_name,
        COUNT(*) as toplam_giris,
        SUM(CASE WHEN status = 'GEÇ GİRİŞ' THEN 1 ELSE 0 END) as gec_giris,
        MIN(DATE_FORMAT(entry_time, '%H:%i:%s')) as ilk_giris
    FROM employee_entries
    WHERE entry_time >= '{}'
    GROUP BY DATE(entry_time), employee_name
    ORDER BY tarih DESC, employee_name
    """.format(one_week_ago.strftime('%Y-%m-%d'))
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("\nSon bir haftada hiç giriş kaydı bulunmamaktadır.")
        return
    
    headers = ["Tarih", "Çalışan", "Toplam Giriş", "Geç Giriş", "İlk Giriş"]
    print("\n=== HAFTALIK RAPOR ===")
    print(tabulate(results, headers=headers, tablefmt="grid"))
    
    conn.close()

def late_entry_stats():
    conn = connect_db()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        employee_name,
        COUNT(*) as toplam_giris,
        SUM(CASE WHEN status = 'GEÇ GİRİŞ' THEN 1 ELSE 0 END) as gec_giris,
        ROUND(SUM(CASE WHEN status = 'GEÇ GİRİŞ' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as gec_yuzde,
        MIN(DATE_FORMAT(entry_time, '%H:%i:%s')) as en_erken,
        MAX(DATE_FORMAT(entry_time, '%H:%i:%s')) as en_gec
    FROM employee_entries
    GROUP BY employee_name
    ORDER BY gec_yuzde DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("\nHiç giriş kaydı bulunmamaktadır.")
        return
    
    headers = ["Çalışan", "Toplam Giriş", "Geç Giriş", "Geç Giriş %", "En Erken", "En Geç"]
    print("\n=== GEÇ GİRİŞ İSTATİSTİKLERİ ===")
    print(tabulate(results, headers=headers, tablefmt="grid"))
    
    conn.close()

def specific_date_report():
    while True:
        date_str = input("\nTarih girin (GG-AA-YYYY) veya 'iptal' yazın: ")
        if date_str.lower() == 'iptal':
            return
        
        try:
            date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()
            daily_report(date_obj)
            break
        except ValueError:
            print("Hatalı tarih formatı! Örnek: 14-12-2024")

def main_menu():
    while True:
        print("\n=== RAPORLAMA SİSTEMİ ===")
        print("1. Bugünün Raporu")
        print("2. Belirli Bir Günün Raporu")
        print("3. Haftalık Rapor")
        print("4. Geç Giriş İstatistikleri")
        print("5. Çıkış")
        
        choice = input("\nSeçiminiz (1-5): ")
        
        if choice == "1":
            daily_report()
        elif choice == "2":
            specific_date_report()
        elif choice == "3":
            weekly_report()
        elif choice == "4":
            late_entry_stats()
        elif choice == "5":
            print("\nProgram sonlandırılıyor...")
            break
        else:
            print("\nGeçersiz seçim!")
        
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main_menu()
