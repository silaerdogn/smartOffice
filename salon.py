import RPi.GPIO as GPIO
import time
import threading
from datetime import datetime
import adafruit_dht
import board
import json
from iot_integration import setup_aws_iot
import os

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pin tanımlamaları
MQ135_PIN = 5    # GPIO5 (Pin 29) - MQ135 Dijital çıkış (D0)
DHT_PIN = 4      # GPIO4 (Pin 7)  - DHT11
LDR_PIN = 27     # GPIO27 (Pin 13) - LDR
STATUS_LED_PIN = 22  # GPIO22 (Pin 15) - 5sn yanıp sönen yeşil led
WARNING_LED_PIN = 23 # GPIO23 (Pin 16) - Karanlıkta yanıp sönen kırmızı led
LAMP_LED_PIN = 24    # GPIO24 (Pin 18) - Manuel kontrol edilen yeşil led

# DHT11 setup
dht = adafruit_dht.DHT11(board.D4)

# Pin ayarları
GPIO.setup(MQ135_PIN, GPIO.IN)
GPIO.setup(LDR_PIN, GPIO.IN)
GPIO.setup(STATUS_LED_PIN, GPIO.OUT)
GPIO.setup(WARNING_LED_PIN, GPIO.OUT)
GPIO.setup(LAMP_LED_PIN, GPIO.OUT)

# Global değişkenler
lamp_status = False
running = True

# AWS IoT client
try:
    aws_iot_client = setup_aws_iot()
    print("AWS IoT bağlantısı hazır")
except Exception as e:
    print(f"AWS IoT bağlantı hatası: {e}")
    aws_iot_client = None

def read_dht11():
    """DHT11'den sıcaklık ve nem oku"""
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        return humidity, temperature
    except RuntimeError as error:
        print(f"DHT11 okuma hatası: {error.args[0]}")
        return None, None
    except Exception as error:
        dht.exit()
        raise error

def read_air_quality():
    """MQ135'ten hava kalitesi durumunu oku"""
    return "İyi" if GPIO.input(MQ135_PIN) else "Kötü"

def status_led_thread():
    """5 saniyede bir yanıp sönen yeşil led için thread"""
    while running:
        GPIO.output(STATUS_LED_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(STATUS_LED_PIN, GPIO.LOW)
        time.sleep(4.5)

def warning_led_thread():
    """Karanlıkta yanıp sönen kırmızı led için thread"""
    while running:
        if GPIO.input(LDR_PIN) == GPIO.HIGH and not lamp_status:  # Karanlık ve lamba kapalı
            GPIO.output(WARNING_LED_PIN, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(WARNING_LED_PIN, GPIO.LOW)
            time.sleep(0.5)
        else:
            GPIO.output(WARNING_LED_PIN, GPIO.LOW)
            time.sleep(0.1)

def clear_screen():
    """Ekranı temizle"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_status(temperature, humidity, air_quality, light_level):
    """Güncel durumu ekrana yazdır"""
    clear_screen()
    print("\n=== SALON KONTROL SİSTEMİ ===")
    print("1: Lambayı aç")
    print("2: Lambayı kapa")
    print("3: Çıkış")
    print("\nGüncel Durum:")
    print(f"Sıcaklık: {temperature}°C")
    print(f"Nem: {humidity}%")
    print(f"Hava Kalitesi: {air_quality}")
    print(f"Işık Durumu: {light_level}")
    print(f"Lamba Durumu: {'Açık' if lamp_status else 'Kapalı'}")
    
    if light_level == "Karanlık" and not lamp_status:
        print("\nUYARI: Ortam karanlık, lamba açılmalı!")
    
    print("\nSeçiminiz (1-3): ", end='', flush=True)

def publish_sensor_data(temperature, humidity, air_quality, light_level):
    """Sensör verilerini AWS IoT'ye gönder"""
    if aws_iot_client:
        message = {
            "device_id": "RaspberryPi_SalonSystem",
            "timestamp": datetime.now().isoformat(),
            "temperature": temperature,
            "humidity": humidity,
            "air_quality": air_quality,
            "light_level": light_level,
            "lamp_status": "Açık" if lamp_status else "Kapalı"
        }
        try:
            aws_iot_client.publish("salon/sensors", json.dumps(message), 1)
        except Exception as e:
            print(f"AWS IoT gönderim hatası: {e}")

def main():
    global running, lamp_status
    
    # Thread'leri başlat
    status_thread = threading.Thread(target=status_led_thread)
    warning_thread = threading.Thread(target=warning_led_thread)
    
    status_thread.daemon = True
    warning_thread.daemon = True
    
    status_thread.start()
    warning_thread.start()
    
    try:
        while True:
            # Sensör verilerini oku
            humidity, temperature = read_dht11()
            
            if humidity is not None and temperature is not None:
                air_quality = read_air_quality()
                light_level = "Karanlık" if GPIO.input(LDR_PIN) == GPIO.HIGH else "Normal"
                
                # Güncel durumu göster
                print_status(temperature, humidity, air_quality, light_level)
                
                # Sensör verilerini AWS'ye gönder
                publish_sensor_data(temperature, humidity, air_quality, light_level)
            
            # Kullanıcı girişini kontrol et
            if input_available():
                choice = input()
                
                if choice == '1':
                    lamp_status = True
                    GPIO.output(LAMP_LED_PIN, GPIO.HIGH)
                    print("\nLamba açıldı")
                    time.sleep(1)
                
                elif choice == '2':
                    lamp_status = False
                    GPIO.output(LAMP_LED_PIN, GPIO.LOW)
                    print("\nLamba kapatıldı")
                    time.sleep(1)
                
                elif choice == '3':
                    print("\nProgram sonlandırılıyor...")
                    running = False
                    break
                
                else:
                    print("\nGeçersiz seçim!")
                    time.sleep(1)
            
            time.sleep(0.5)  # Yarım saniyede bir güncelle
    
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından sonlandırıldı.")
    
    finally:
        running = False
        dht.exit()
        GPIO.cleanup()
        if aws_iot_client:
            aws_iot_client.disconnect()

def input_available():
    """Kullanıcı girişi var mı kontrol et"""
    import sys, select
    return select.select([sys.stdin], [], [], 0)[0] != []

if __name__ == "__main__":
    main()
