import RPi.GPIO as GPIO
import time
import mysql.connector
from datetime import datetime, timedelta
from iot_integration import setup_aws_iot, publish_entry
import logging
import json

# Tüm logging mesajlarını kapat
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('AWSIoTPythonSDK').setLevel(logging.CRITICAL)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pin tanımlamaları
BUZZER_PIN = 12
SERVO_PIN = 18  # Servo motor için GPIO18 kullanıyoruz

# Buzzer setup
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

# Servo motor setup
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz frekans
servo.start(0)

# Keypad satır ve sütun pinleri
ROW_PINS = [5, 6, 13, 19]  # Satırlar
COL_PINS = [26, 20, 21, 16]  # Sütunlar

# Keypad matrisi
MATRIX = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# GPIO pinlerini ayarla
for pin in ROW_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

for pin in COL_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Servo motor fonksiyonları
def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)

def unlock_door():
    print("Kapı açılıyor...")
    set_servo_angle(90)  # Kapıyı aç
    time.sleep(3)  # 3 saniye bekle
    print("Kapı kapanıyor...")
    set_servo_angle(0)  # Kapıyı kapat

# Buzzer fonksiyonları
def success_beep():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def error_beep():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def key_beep():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.05)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

# Keypad okuma fonksiyonu
def read_keypad():
    pressed_key = None

    for row_num, row_pin in enumerate(ROW_PINS):
        GPIO.output(row_pin, GPIO.LOW)

        for col_num, col_pin in enumerate(COL_PINS):
            if GPIO.input(col_pin) == GPIO.LOW:
                pressed_key = MATRIX[row_num][col_num]
                time.sleep(0.2)  # Tuş sıçramasını önle

        GPIO.output(row_pin, GPIO.HIGH)
    return pressed_key

# Veritabanı bağlantısı
def connect_db():
    return mysql.connector.connect(
     
    'host': '....',
    'user': '....',
    'password': '....',
    'database': '....'

    )

def verify_password(password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name, department FROM employees WHERE password = %s", (password,))
    result = cursor.fetchone()

    conn.close()
    return (result[0], result[1]) if result else (None, None)

def log_entry(person_name, entry_time):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Türkiye saati için 3 saat ekle
    entry_time = entry_time + timedelta(hours=3)

    # Mesai saati kontrolü (9:00)
    target_time = entry_time.replace(hour=9, minute=0, second=0, microsecond=0)
    status = "GEÇ GİRİŞ" if entry_time > target_time else "NORMAL GİRİŞ"

    sql = """
    INSERT INTO employee_entries
    (employee_name, entry_time, status)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (person_name, entry_time, status))
    conn.commit()
    conn.close()

    return status, entry_time

def main():
    print("\n=== OFİS GİRİŞ SİSTEMİ ===")

    try:
        aws_iot_client = setup_aws_iot()
        print("AWS IoT bağlantısı hazır\n")
    except Exception as e:
        print(f"AWS IoT bağlantı hatası: {e}")
        aws_iot_client = None

    print("Şifrenizi girin:")
    current_code = ""

    try:
        while True:
            key = read_keypad()

            if key is not None:
                key_beep()

                if key == '#':
                    person_info = verify_password(current_code)
                    if person_info[0]:  # person_info[0] is name, person_info[1] is department
                        success_beep()
                        entry_time = datetime.now()
                        status, adjusted_time = log_entry(person_info[0], entry_time)

                        # Kapıyı aç
                        unlock_door()

                        # AWS IoT'ye giriş bilgisini gönder
                        if aws_iot_client:
                            message = {
                                "device_id": "RaspberryPi_OfficeSystem",
                                "timestamp": adjusted_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "person_name": person_info[0],
                                "department": person_info[1],
                                "status": status,
                                "office_location": "Ana Ofis"
                            }
                            try:
                                aws_iot_client.publish("office/entries", json.dumps(message), 1)
                                print(f"\nGiriş kaydedildi: {person_info[0]}")
                            except Exception as e:
                                print(f"\nAWS IoT gönderim hatası: {e}")

                        print(f"\nHoş geldiniz {person_info[0]}")
                        print(f"Departman: {person_info[1]}")
                        print(f"Giriş durumu: {status}")
                        print(f"Giriş saati: {adjusted_time.strftime('%H:%M:%S')}")
                    else:
                        error_beep()
                        print("\nHatalı şifre!")
                    current_code = ""
                    print("\nYeni giriş için hazır...")

                elif key == '*':
                    current_code = ""
                    print("\nŞifre sıfırlandı")

                else:
                    current_code += key
                    print("*", end="", flush=True)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram sonlandırılıyor...")
        if aws_iot_client:
            aws_iot_client.disconnect()
    finally:
        print("\nSistem kapatılıyor...")
        servo.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
