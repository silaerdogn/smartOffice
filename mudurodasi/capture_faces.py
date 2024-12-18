import cv2
import os
import time
import sys
import pickle
from db_operations import DatabaseManager

# X11 için gerekli çevre değişkenleri
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["DISPLAY"] = ":0"

# Veritabanı bağlantısı
db = DatabaseManager()

# Kamera başlatma
print("\nKamera başlatılıyor...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Kamera açılamadı!")
    sys.exit(1)

# Çözünürlük ayarla
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Yüz tespiti için cascade sınıflandırıcı
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Ana klasör kontrolü
if not os.path.exists('dataset'):
    os.makedirs('dataset')

print("\n=== OFİS YÖNETİM SİSTEMİ - YÜZ KAYIT ===")

# Pencereyi oluştur ve boyutunu ayarla
window_name = 'Ofis Yönetim Sistemi - Yüz Kayıt'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 640, 480)

# Müdür kontrolü
while True:
    name = input("\nLütfen personel adını ve soyadını girin: ")
    if name.strip():
        if db.verify_manager(name):
            break
        else:
            print("Bu isimde yetkili bir müdür bulunamadı!")
            print("Lütfen veritabanındaki ismi aynen giriniz.")
    else:
        print("Geçerli bir isim giriniz!")

# Kullanıcı klasörü oluştur
user_path = os.path.join('dataset', name)
if not os.path.exists(user_path):
    os.makedirs(user_path)

count = 0
total_images = 30
last_capture_time = time.time()
face_images = []

print("\nYüz kayıt işlemi başlıyor...")
print(f"Lütfen kameraya bakın ve yüzünüzü yavaşça farklı açılara çevirin.")
print(f"Toplam {total_images} fotoğraf çekilecek.")
print("İşlemi iptal etmek için 'q' tuşuna basın.")

# Kamera önizlemesini başlat
cv2.startWindowThread()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Görüntü alınamıyor!")
        break

    # Görüntüyü ayna gibi çevir
    frame = cv2.flip(frame, 1)

    # Yüz tespiti
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    current_time = time.time()

    for (x, y, w, h) in faces:
        # Yüz çerçevesi çiz
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Her 0.5 saniyede bir fotoğraf çek
        if current_time - last_capture_time >= 0.5 and count < total_images:
            face_img = frame[y:y+h, x:x+w]

            if face_img.size > 0:
                img_path = os.path.join(user_path, f'{name}_{count}.jpg')
                try:
                    cv2.imwrite(img_path, face_img)
                    face_images.append(face_img)
                    print(f"Fotoğraf {count+1}/{total_images} kaydedildi!")
                    count += 1
                    last_capture_time = current_time
                except Exception as e:
                    print(f"Fotoğraf kaydetme hatası: {str(e)}")

    # Kalan fotoğraf sayısını göster
    cv2.putText(frame, f"Kalan: {total_images-count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Görüntüyü göster
    try:
        cv2.imshow(window_name, frame)
    except Exception as e:
        print(f"Görüntü gösterme hatası: {str(e)}")
        continue

    # Tüm fotoğraflar çekildiyse veya q tuşuna basıldıysa çık
    if count >= total_images:
        print("\nTüm fotoğraflar başarıyla kaydedildi!")
        # Yüz verilerini veritabanına kaydet
        face_data = pickle.dumps(face_images)
        db.save_face_data(name, "manager", face_data)
        print("Yüz verileri veritabanına kaydedildi.")
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\nİşlem kullanıcı tarafından iptal edildi.")
        break

# Temizlik
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)  # Pencereyi düzgün kapatmak için ek bekleme

print(f"\nİşlem tamamlandı!")
print(f"Toplam {count} fotoğraf {user_path} klasörüne kaydedildi.")
if count < total_images:
    print(f"Not: Hedeflenen {total_images} fotoğraftan {count} tanesi çekilebildi.")

# Veritabanı bağlantısını kapat
db.close()
