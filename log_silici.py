import mysql.connector
from datetime import datetime

# Veritabanı bağlantı bilgileri
DB_CONFIG = {
    'host': 'database-1.cb8k2y8iy0eb.eu-central-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'raspberrypi',
    'database': 'office_management'
}

def connect_database():
    try:
        print("Veritabanına bağlanılıyor...")
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def cleanup_logs():
    try:
        connection = connect_database()
        if not connection:
            return
        
        cursor = connection.cursor()
        
        # Toplantı odası logları
        print("\nToplantı odası logları temizleniyor...")
        cursor.execute("""
            DELETE FROM meeting_room_logs 
            WHERE id NOT IN (
                SELECT id FROM (
                    SELECT id FROM meeting_room_logs 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                ) AS last_five
            )
        """)
        deleted_meeting = cursor.rowcount
        print(f"Toplantı odası: {deleted_meeting} log silindi")
        
        # Lavabo durumu logları
        print("\nLavabo durumu logları temizleniyor...")
        cursor.execute("""
            DELETE FROM bathroom_status 
            WHERE id NOT IN (
                SELECT id FROM (
                    SELECT id FROM bathroom_status 
                    ORDER BY last_check_time DESC 
                    LIMIT 5
                ) AS last_five
            )
        """)
        deleted_bathroom = cursor.rowcount
        print(f"Lavabo durumu: {deleted_bathroom} log silindi")
        
        # Müdür odası giriş logları
        print("\nMüdür odası giriş logları temizleniyor...")
        cursor.execute("""
            DELETE FROM access_logs 
            WHERE id NOT IN (
                SELECT id FROM (
                    SELECT id FROM access_logs 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                ) AS last_five
            )
        """)
        deleted_access = cursor.rowcount
        print(f"Müdür odası: {deleted_access} log silindi")
        
        # Gaz alarm logları
        print("\nGaz alarm logları temizleniyor...")
        cursor.execute("""
            DELETE FROM alarm_logs 
            WHERE id NOT IN (
                SELECT id FROM (
                    SELECT id FROM alarm_logs 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                ) AS last_five
            )
        """)
        deleted_alarms = cursor.rowcount
        print(f"Gaz alarmları: {deleted_alarms} log silindi")
        
        connection.commit()
        
        # Kalan logları göster
        print("\nKalan son loglar:")
        
        print("\nToplantı Odası Son 5 Log:")
        cursor.execute("SELECT timestamp, status, message FROM meeting_room_logs ORDER BY timestamp DESC LIMIT 5")
        for log in cursor.fetchall():
            print(f"Zaman: {log[0]}, Durum: {log[1]}, Mesaj: {log[2]}")
            
        print("\nLavabo Durumu Son 5 Log:")
        cursor.execute("SELECT last_check_time, status FROM bathroom_status ORDER BY last_check_time DESC LIMIT 5")
        for log in cursor.fetchall():
            print(f"Zaman: {log[0]}, Durum: {log[1]}")
            
        print("\nMüdür Odası Son 5 Giriş:")
        cursor.execute("SELECT timestamp, person_name, action FROM access_logs ORDER BY timestamp DESC LIMIT 5")
        for log in cursor.fetchall():
            print(f"Zaman: {log[0]}, Kişi: {log[1]}, İşlem: {log[2]}")
            
        print("\nSon 5 Gaz Alarmı:")
        cursor.execute("SELECT timestamp, status, message FROM alarm_logs ORDER BY timestamp DESC LIMIT 5")
        for log in cursor.fetchall():
            print(f"Zaman: {log[0]}, Durum: {log[1]}, Mesaj: {log[2]}")
        
        cursor.close()
        connection.close()
        print("\nVeritabanı bağlantısı kapatıldı!")
        
        total_deleted = deleted_meeting + deleted_bathroom + deleted_access + deleted_alarms
        print(f"\nToplam {total_deleted} log temizlendi!")
        
    except mysql.connector.Error as err:
        print(f"Hata: {err}")

if __name__ == "__main__":
    print("=== VERİTABANI LOG TEMİZLEME PROGRAMI ===\n")
    cleanup_logs()
    print("\nİşlem tamamlandı!")
