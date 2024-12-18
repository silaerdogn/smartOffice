import cv2
import numpy as np
import os
import pickle
from db_operations import DatabaseManager

def train_model():
    print("\n=== OFİS YÖNETİM SİSTEMİ - MODEL EĞİTİMİ ===")
    print("Model eğitimi başlıyor...")

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    faces = []
    labels = []
    label_dict = {}
    current_label = 0

    print("Dataset klasörü taranıyor...")
    
    db = DatabaseManager()
    
    # Veritabanından yetkili kullanıcıları al
    db.cursor.execute("SELECT name, face_data FROM authorized_users WHERE is_manager = TRUE")
    authorized_users = db.cursor.fetchall()

    for name, face_data in authorized_users:
        print(f"İşleniyor: {name}")
        label_dict[current_label] = name
        
        # Binary verileri numpy dizisine çevir
        face_images = pickle.loads(face_data)
        
        for face_img in face_images:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            faces.append(cv2.resize(gray, (100, 100)))
            labels.append(current_label)
        
        current_label += 1

    print(f"Toplam {len(faces)} yüz tespit edildi.")

    if len(faces) == 0:
        print("Hiç yüz tespit edilemedi! Eğitim yapılamıyor.")
        return

    print("Model eğitiliyor...")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))

    recognizer.save('trainer.yml')
    print("Model trainer.yml olarak kaydedildi.")

    with open('labels.pkl', 'wb') as f:
        pickle.dump(label_dict, f)
    print("Etiketler labels.pkl olarak kaydedildi.")

    print("\nModel eğitimi tamamlandı!")
    print(f"Tanınan kişiler: {list(label_dict.values())}")

if __name__ == "__main__":
    try:
        train_model()
    except Exception as e:
        print(f"Bir hata oluştu: {str(e)}")
