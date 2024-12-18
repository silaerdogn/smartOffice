import RPi.GPIO as GPIO
import time
import threading
from datetime import datetime
import mysql.connector

# GPIO modunu ayarla
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pin tanımlamaları
MQ2_PIN = 27        # Gaz sensörü (PIN 13)
LED_PIN = 23        # Kırmızı LED (PIN 16)
BUZZER_PIN = 17     # Buzzer (PIN 11) - değiştirildi

# Veritabanı bağlantı bilgileri
DB_CONFIG = {
    'host': '....',
    'user': '....',
    'password': '....',
    'database': '....'
}

# Pin ayarları
GPIO.setup(MQ2_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Başlangıçta buzzer'ı kapat
GPIO.output(BUZZER_PIN, GPIO.LOW)

# Global değişkenler
running = True
alarm_active = False
last_alarm_state = False

def connect_database():
    """Veritabanına bağlan"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def log_alarm(status, message):
    """Alarm durumunu veritabanına kaydet"""
    try:
        connection = connect_database()
        if connection:
            cursor = connection.cursor()
            
            # Alarm kaydını ekle
            query = """
                INSERT INTO alarm_logs (timestamp, location, status, message)
                VALUES (%s, %s, %s, %s)
            """
            values = (datetime.now(), 'Mutfak', status, message)
            
            cursor.execute(query, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            print("Alarm kaydı veritabanına eklendi")
            
    except mysql.connector.Error as err:
        print(f"Veritabanı kayıt hatası: {err}")

def normal_led_thread():
    """Normal durumda 5 saniyede bir yanıp sönen LED"""
    while running:
        if not alarm_active:
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(4.5)  # Toplam 5 saniye için
        else:
            time.sleep(0.1)

def cleanup_gpio():
    """GPIO pinlerini temizle"""
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.cleanup()

def main():
    global running, alarm_active, last_alarm_state
    
    try:
        # LED thread'ini başlat
        led_thread = threading.Thread(target=normal_led_thread)
        led_thread.daemon = True
        led_thread.start()
        
        print("\n=== MUTFAK GAZ ALARM SİSTEMİ ===")
        print("Sistem başlatılıyor...")
        print("MQ-2 sensörü ısınıyor, lütfen bekleyin...")
        time.sleep(10)  # Sensörün ısınması için bekleme
        print("Sistem hazır!")
        print("Normal durumda kırmızı LED 5 saniyede bir yanıp sönecek")
        print("Gaz algılandığında alarm çalacak ve kayıt tutulacak")
        
        # Sistem başlangıç kaydı
        log_alarm('info', 'Gaz alarm sistemi başlatıldı')
        
        while True:
            current_state = GPIO.input(MQ2_PIN)
            
            if current_state:  # Gaz tespit edildi
                alarm_active = True
                
                # Eğer yeni bir alarm durumuna geçildiyse kayıt tut
                if not last_alarm_state:
                    print("\n!!! UYARI !!!")
                    print("GAZ TESPİT EDİLDİ!")
                    print("GAZ ALARMI!")
                    log_alarm('danger', 'Yüksek gaz seviyesi tespit edildi!')
                
                # Alarm durumu (hızlı yanıp sönme ve buzzer)
                GPIO.output(LED_PIN, GPIO.HIGH)
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(LED_PIN, GPIO.LOW)
                GPIO.output(BUZZER_PIN, GPIO.LOW)
                time.sleep(0.2)
            
            else:  # Normal durum
                alarm_active = False
                GPIO.output(BUZZER_PIN, GPIO.LOW)
                
                # Eğer alarm durumundan normal duruma geçildiyse
                if last_alarm_state:
                    print("\nSistem normale döndü")
                    print("Gaz seviyesi normal")
                    log_alarm('normal', 'Gaz seviyesi normale döndü')
                
                time.sleep(0.1)
            
            # Alarm durumunu güncelle
            last_alarm_state = current_state
            
            # Debug için sensör değerini göster
            print(f"Sensör değeri: {current_state}", end='\r')
    
    except KeyboardInterrupt:
        print("\nProgram sonlandırılıyor...")
        
    finally:
        running = False
        log_alarm('info', 'Gaz alarm sistemi kapatıldı')
        cleanup_gpio()

if __name__ == "__main__":
    main()
