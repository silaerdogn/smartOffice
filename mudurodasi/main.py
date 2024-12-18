import cv2
import pickle
import time
import sys
import os
import json
from datetime import datetime
from gpiozero import Servo, LED
from db_operations import DatabaseManager
from iot_integration import setup_aws_iot

# X11 için gerekli çevre değişkenleri
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["DISPLAY"] = ":0"

# AWS IoT bağlantısı
try:
    aws_iot_client = setup_aws_iot()
    print("AWS IoT baglantisi hazir")
except Exception as e:
    print(f"AWS IoT baglanti hatasi: {e}")
    aws_iot_client = None

# Servo motor ve LED ayarları
servo = Servo(22, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
green_led = LED(27)  # Yeşil LED için GPIO27 (Pin 13)
print("Servo motor ve LED basariyla baslatildi!")

# Başlangıçta LED'i söndür
green_led.off()

def unlock_door(name, confidence, action):
    try:
        print("\n=== YETKİLİ GİRİŞİ ONAYLANDI ===")
        print("Kapı açılıyor...")
        
        # Yeşil LED'i yak
        green_led.on()
        
        # Giriş/çıkış durumunu kaydet
        entry_status = db.log_access(name, confidence, action)
        
        # Servo kontrolü
        servo.max()
        time.sleep(3)
        
        print("Kapı kapanıyor...")
        servo.min()
        time.sleep(1)
        
        # LED'i söndür
        green_led.off()
        
        return entry_status
        
    except Exception as e:
        print(f"Kilit mekanizması hatası: {str(e)}")
        green_led.off()  # Hata durumunda LED'i söndür
        return None

def publish_to_iot(name, action, location="Mudur Odasi"):
    if aws_iot_client:
        message = {
            "device_id": "RaspberryPi_ManagerOffice",
            "timestamp": datetime.now().isoformat(),
            "person_name": name,
            "action": action,
            "location": location
        }
        try:
            aws_iot_client.publish("office/manager_access", json.dumps(message), 1)
            print(f"IoT mesaji gonderildi: {action}")
        except Exception as e:
            print(f"IoT yayin hatasi: {str(e)}")

# Veritabanı bağlantısı
db = DatabaseManager()

# Yüz tanıma modelini yükle
recognizer = cv2.face.LBPHFaceRecognizer_create()
try:
    recognizer.read('trainer.yml')
except:
    print("trainer.yml dosyasi bulunamadi! Once modeli egittiginizden emin olun.")
    sys.exit(1)

# Cascade sınıflandırıcı
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Etiketleri yükle
try:
    with open('labels.pkl', 'rb') as f:
        label_dict = pickle.load(f)
except:
    print("labels.pkl dosyasi bulunamadi! Once modeli egittiginizden emin olun.")
    sys.exit(1)

# Kamera başlat
print("\n=== OFIS YONETIM SISTEMI - MUDUR ODASI ===")
print("Kamera baslatiliyor...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Kamera acilamadi!")
    sys.exit(1)

# Kamera ayarları
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Pencereyi oluştur
window_name = 'Ofis Yonetim Sistemi - Mudur Odasi'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 640, 480)

print("Sistem hazir! Cikmak icin 'q' tusuna basin.")

last_unlock_time = 0
recognition_counter = 0
RECOGNITION_THRESHOLD = 3

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Goruntu alinamiyor!")
            break
            
        frame = cv2.flip(frame, 1)
        
        # Bilgi paneli
        info_panel = frame.copy()
        cv2.rectangle(info_panel, (0, 0), (frame.shape[1], 40), (0, 0, 0), -1)
        cv2.putText(info_panel, "Ofis Yonetim Sistemi - Mudur Odasi", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        frame = info_panel
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))
        
        current_time = time.time()
        face_recognized = False
        
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (100, 100))
            
            try:
                label, confidence = recognizer.predict(roi_gray)
                
                if confidence < 85:
                    name = label_dict[label]
                    if db.verify_manager(name):
                        match_text = f"Eslesme: {100-confidence:.1f}%"
                        color = (0, 255, 0)
                        face_recognized = True
                        
                        if recognition_counter >= RECOGNITION_THRESHOLD and current_time - last_unlock_time > 5:
                            print(f"\nHoş geldiniz Sayın {name}")
                            entry_status = unlock_door(name, 100-confidence, "YETKILI GIRIS")
                            if entry_status:
                                publish_to_iot(name, f"YETKILI {entry_status}")
                            last_unlock_time = current_time
                            recognition_counter = 0
                        else:
                            recognition_counter += 1
                    else:
                        name = "Yetkisiz Giris"
                        match_text = f"Eslesme: {100-confidence:.1f}%"
                        color = (0, 0, 255)
                        recognition_counter = 0
                        db.log_access(name, 100-confidence, "YETKISIZ GIRIS DENEMESI")
                        publish_to_iot(name, "YETKISIZ GIRIS DENEMESI")
                else:
                    name = "Taninmayan Kisi"
                    match_text = f"Eslesme: {100-confidence:.1f}%"
                    color = (0, 0, 255)
                    recognition_counter = 0
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.rectangle(frame, (x, y-60), (x+w, y), color, -1)
                cv2.putText(frame, name, (x+5, y-35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, match_text, (x+5, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
            except Exception as e:
                print(f"Tanima hatasi: {str(e)}")
                recognition_counter = 0
        
        if not face_recognized:
            recognition_counter = 0
        
        cv2.imshow(window_name, frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nProgram kullanici tarafindan sonlandirildi.")
except Exception as e:
    print(f"Beklenmeyen hata: {str(e)}")
finally:
    print("\nSistem kapatiliyor...")
    green_led.off()  # LED'i söndür
    servo.detach()
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    db.close()
    if aws_iot_client:
        aws_iot_client.disconnect()
