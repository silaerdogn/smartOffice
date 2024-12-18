import RPi.GPIO as GPIO
import time
import mysql.connector
from datetime import datetime

# GPIO modunu ayarla
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pin tanımlamaları
PIR_PIN = 17        # PIR Hareket Sensörü (PIN 11)
LED_PIN = 18        # Yeşil LED (PIN 12)

# Veritabanı bağlantı bilgileri
DB_CONFIG = {
    'host': 'database-1.cb8k2y8iy0eb.eu-central-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'raspberrypi',
    'database': 'office_management'
}

# Pin ayarları
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

# Başlangıçta LED'i söndür
GPIO.output(LED_PIN, GPIO.LOW)

# Hareket algılama parametreleri
MOTION_THRESHOLD = 5     # Kaç kez hareket algılanırsa gerçek hareket sayılacak
MAX_MOTION_COUNT = 10    # Maksimum hareket sayacı değeri
MOTION_TIMEOUT = 10      # Hareket olmadığında ne kadar süre sonra boş sayılacak (saniye)
DEBOUNCE_TIME = 0.5     # Ardışık okumaların arasındaki minimum süre (saniye)
MOTION_RESET_TIME = 2   # Hareket sayacının sıfırlanması için gereken süre (saniye)

def connect_database():
    """Veritabanına bağlan"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def log_room_status(status, message):
    """Oda durumunu veritabanına kaydet"""
    try:
        connection = connect_database()
        if connection:
            cursor = connection.cursor()
            
            query = """
                INSERT INTO meeting_room_logs 
                (timestamp, status, message, motion_detected)
                VALUES (%s, %s, %s, %s)
            """
            values = (
                datetime.now(),
                status,
                message,
                status == 'DOLU'
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            print("Oda durumu veritabanına kaydedildi")
            
    except mysql.connector.Error as err:
        print(f"Veritabanı kayıt hatası: {err}")

def main():
    print("\n=== TOPLANTI ODASI TAKİP SİSTEMİ ===")
    print("Sistem başlatılıyor...")
    print("PIR sensörü ısınıyor, lütfen bekleyin...")
    time.sleep(5)  # Sensörün ısınması için bekleme süresini düşürdük
    
    print("Sistem hazır!")
    print("Hareket algılandığında yeşil LED yanacak")
    print("ve oda durumu kaydedilecek")
    
    # Sistem başlangıç kaydı
    log_room_status('BOS', 'Toplantı odası takip sistemi başlatıldı')
    
    last_motion_time = 0
    last_status_change = 0
    room_occupied = False
    motion_count = 0
    last_read_time = 0
    last_reset_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # Belirli aralıklarla hareket sayacını sıfırla
            if current_time - last_reset_time > MOTION_RESET_TIME:
                motion_count = max(0, motion_count - 2)  # Her reset periyodunda 2 azalt
                last_reset_time = current_time
            
            # Debounce kontrolü
            if current_time - last_read_time >= DEBOUNCE_TIME:
                motion_detected = GPIO.input(PIR_PIN)
                last_read_time = current_time
                
                if motion_detected:
                    # Hareket sayacını sınırla
                    motion_count = min(motion_count + 1, MAX_MOTION_COUNT)
                    last_motion_time = current_time
                    
                    # Yeterli hareket algılandı mı?
                    if motion_count >= MOTION_THRESHOLD and not room_occupied:
                        print("\n! HAREKETLİLİK ALGILANDI !")
                        print("Toplantı odası: DOLU")
                        GPIO.output(LED_PIN, GPIO.HIGH)  # LED'i yak
                        log_room_status('DOLU', 'Odada hareket algılandı')
                        room_occupied = True
                        last_status_change = current_time
                
                # Hareket yoksa veya çok düşükse
                if not motion_detected or motion_count < MOTION_THRESHOLD:
                    # Timeout kontrolü
                    if room_occupied and (current_time - last_motion_time) > MOTION_TIMEOUT:
                        print("\nToplantı odası: BOŞ")
                        print(f"{MOTION_TIMEOUT} saniyedir hareket algılanmadı")
                        GPIO.output(LED_PIN, GPIO.LOW)  # LED'i söndür
                        log_room_status('BOS', 'Odada hareket algılanmıyor')
                        room_occupied = False
                        motion_count = 0
                        last_status_change = current_time
            
            # Mevcut durumu göster
            status = "DOLU" if room_occupied else "BOŞ"
            print(f"\rOda Durumu: {status} (Hareket Sayacı: {motion_count})", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nProgram sonlandırılıyor...")
        log_room_status('BOS', 'Toplantı odası takip sistemi kapatıldı')
        GPIO.output(LED_PIN, GPIO.LOW)  # LED'i söndür
        GPIO.cleanup()

if __name__ == "__main__":
    main()
