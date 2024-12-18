import mysql.connector
from datetime import datetime, timedelta
from prettytable import PrettyTable
import os

# Veritabanı bağlantı bilgileri
DB_CONFIG = {
    'host': 'database-1.cb8k2y8iy0eb.eu-central-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'raspberrypi',
    'database': 'office_management'
}

class OfficeManager:
    def __init__(self):
        self.db = self.connect_database()
        
    def connect_database(self):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error as err:
            print(f"Veritabanı bağlantı hatası: {err}")
            return None

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def show_current_status(self):
        """Ofisin anlık durumunu göster"""
        cursor = self.db.cursor()
        
        # İçerideki personel sayısı
        cursor.execute("""
            SELECT COUNT(*) FROM employee_entries 
            WHERE status = 'GIRIS' AND DATE(entry_time) = CURDATE()
            AND NOT EXISTS (
                SELECT 1 FROM employee_entries e2 
                WHERE e2.employee_name = employee_entries.employee_name 
                AND e2.status = 'CIKIS' 
                AND e2.entry_time > employee_entries.entry_time
            )
        """)
        current_count = cursor.fetchone()[0]
        
        print("\n=== OFİS ANLIK DURUM ===")
        print(f"İçerideki Personel Sayısı: {current_count}")
        
        # Müdürlerin durumu
        cursor.execute("""
            SELECT e.name, 
                   CASE WHEN EXISTS (
                       SELECT 1 FROM employee_entries ee 
                       WHERE ee.employee_name = e.name 
                       AND ee.status = 'GIRIS' 
                       AND DATE(ee.entry_time) = CURDATE()
                       AND NOT EXISTS (
                           SELECT 1 FROM employee_entries ee2 
                           WHERE ee2.employee_name = e.name 
                           AND ee2.status = 'CIKIS' 
                           AND ee2.entry_time > ee.entry_time
                       )
                   ) THEN 'İçeride' ELSE 'Dışarıda' END as status
            FROM employees e 
            WHERE e.is_manager = TRUE
        """)
        managers = cursor.fetchall()
        
        print("\nMüdürlerin Durumu:")
        for manager in managers:
            print(f"{manager[0]}: {manager[1]}")

    def show_meeting_room_status(self):
        """Toplantı odası durumunu göster"""
        cursor = self.db.cursor()
        
        # Son durum
        cursor.execute("""
            SELECT status, timestamp, message 
            FROM meeting_room_logs 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        current_status = cursor.fetchone()
        
        print("\n=== TOPLANTI ODASI DURUMU ===")
        if current_status:
            print(f"Mevcut Durum: {current_status[0]}")
            print(f"Son Güncelleme: {current_status[1].strftime('%H:%M:%S')}")
            print(f"Durum Bilgisi: {current_status[2]}")
        else:
            print("Durum bilgisi bulunamadı")
        
        # Son 5 hareket kaydı
        cursor.execute("""
            SELECT timestamp, status, message 
            FROM meeting_room_logs 
            WHERE timestamp >= NOW() - INTERVAL 1 HOUR
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        movements = cursor.fetchall()
        
        if movements:
            print("\nSon Hareketler:")
            table = PrettyTable()
            table.field_names = ["Zaman", "Durum", "Açıklama"]
            for movement in movements:
                table.add_row([
                    movement[0].strftime('%H:%M:%S'),
                    movement[1],
                    movement[2]
                ])
            print(table)

    def show_today_entries(self):
        """Günlük giriş çıkışları göster"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT employee_name, entry_time, status 
            FROM employee_entries 
            WHERE DATE(entry_time) = CURDATE()
            ORDER BY entry_time DESC
        """)
        entries = cursor.fetchall()
        
        table = PrettyTable()
        table.field_names = ["Personel", "Zaman", "Durum"]
        for entry in entries:
            table.add_row([entry[0], entry[1].strftime('%H:%M:%S'), entry[2]])
        
        print("\n=== GÜNLÜK GİRİŞ ÇIKIŞLAR ===")
        print(table)

    def show_gas_alarms(self):
        """Son gaz alarmlarını göster"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT timestamp, status, message 
            FROM alarm_logs 
            WHERE timestamp >= NOW() - INTERVAL 24 HOUR
            ORDER BY timestamp DESC
        """)
        alarms = cursor.fetchall()
        
        table = PrettyTable()
        table.field_names = ["Zaman", "Durum", "Mesaj"]
        for alarm in alarms:
            table.add_row([alarm[0].strftime('%H:%M:%S'), alarm[1], alarm[2]])
        
        print("\n=== SON 24 SAAT GAZ ALARMLARI ===")
        print(table)

    def show_late_arrivals(self):
        """Geç gelenleri göster"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT employee_name, entry_time 
            FROM employee_entries 
            WHERE DATE(entry_time) = CURDATE()
            AND TIME(entry_time) > '09:00:00'
            AND status = 'GIRIS'
            ORDER BY entry_time
        """)
        late_arrivals = cursor.fetchall()
        
        table = PrettyTable()
        table.field_names = ["Personel", "Giriş Saati"]
        for entry in late_arrivals:
            table.add_row([entry[0], entry[1].strftime('%H:%M:%S')])
        
        print("\n=== BUGÜN GEÇ GELENLER ===")
        print(table)

    def show_bathroom_status(self):
        """Lavabo durumunu göster"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT status, last_check_time 
            FROM bathroom_status 
            ORDER BY last_check_time DESC 
            LIMIT 1
        """)
        status = cursor.fetchone()
        
        print("\n=== LAVABO DURUMU ===")
        if status:
            print(f"Durum: {status[0]}")
            print(f"Son Kontrol: {status[1].strftime('%H:%M:%S')}")
        else:
            print("Durum bilgisi bulunamadı")

    def update_bathroom_status(self):
        """Lavabo durumunu güncelle"""
        cursor = self.db.cursor()
        
        print("\n=== LAVABO DURUMU GÜNCELLE ===")
        print("1. Temiz")
        print("2. Kirli")
        print("3. Bakımda")
        
        choice = input("\nSeçiminiz (1-3): ")
        status_map = {'1': 'TEMIZ', '2': 'KIRLI', '3': 'BAKIMDA'}
        
        if choice in status_map:
            cursor.execute("""
                INSERT INTO bathroom_status (status, last_check_time)
                VALUES (%s, NOW())
            """, (status_map[choice],))
            self.db.commit()
            print("\nLavabo durumu güncellendi!")
        else:
            print("\nGeçersiz seçim!")

    def show_menu(self):
        while True:
            self.clear_screen()
            print("\n=== GELİŞMİŞ OFİS YÖNETİM SİSTEMİ ===")
            print("1. Ofisin Anlık Durumu")
            print("2. Toplantı Odası Durumu")
            print("3. Günlük Giriş Çıkışlar")
            print("4. Gaz Alarmları")
            print("5. Geç Gelenler")
            print("6. Lavabo Durumu")
            print("7. Lavabo Durumu Güncelle")
            print("8. Tüm Raporları Göster")
            print("9. Çıkış")
            
            choice = input("\nSeçiminiz (1-9): ")
            
            if choice == '1':
                self.show_current_status()
            elif choice == '2':
                self.show_meeting_room_status()
            elif choice == '3':
                self.show_today_entries()
            elif choice == '4':
                self.show_gas_alarms()
            elif choice == '5':
                self.show_late_arrivals()
            elif choice == '6':
                self.show_bathroom_status()
            elif choice == '7':
                self.update_bathroom_status()
            elif choice == '8':
                self.show_current_status()
                self.show_meeting_room_status()
                self.show_today_entries()
                self.show_gas_alarms()
                self.show_late_arrivals()
                self.show_bathroom_status()
            elif choice == '9':
                print("\nProgram kapatılıyor...")
                break
            else:
                print("\nGeçersiz seçim!")
            
            input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    manager = OfficeManager()
    manager.show_menu()
