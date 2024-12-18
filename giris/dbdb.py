import mysql.connector

# Veritabanı bağlantı bilgileri
DB_CONFIG = {
    'host': '....',
    'user': '....',
    'password': '....',
    'database': '....'
}


def update_database():
    try:
        print("Veritabanına bağlanılıyor...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("\nTablolar güncelleniyor...")
        
        # employee_entries tablosuna yeni sütunlar ekle
        try:
            cursor.execute("""
                ALTER TABLE employee_entries 
                ADD COLUMN confidence FLOAT,
                ADD COLUMN action VARCHAR(50)
            """)
            print("employee_entries tablosuna yeni sütunlar eklendi!")
        except mysql.connector.Error as err:
            if err.errno == 1060:  # Duplicate column error
                print("Sütunlar zaten mevcut!")
            else:
                print(f"Hata: {err}")
        
        # Tabloyu kontrol et
        cursor.execute("DESCRIBE employee_entries")
        columns = cursor.fetchall()
        
        print("\nGüncel tablo yapısı:")
        for column in columns:
            print(f"- {column[0]}: {column[1]}")
        
        connection.commit()
        cursor.close()
        connection.close()
        print("\nVeritabanı güncellemesi tamamlandı!")
        return True
        
    except mysql.connector.Error as err:
        print(f"\nHata: {err}")
        return False

if __name__ == "__main__":
    print("=== VERİTABANI GÜNCELLEME PROGRAMI ===\n")
    success = update_database()
    
    if success:
        print("\nGüncelleme başarıyla tamamlandı!")
    else:
        print("\nGüncelleme sırasında hata oluştu!")
