import mysql.connector

# Veritabanı bağlantı bilgileri
DB_CONFIG = {
    'host': '....',
    'user': '....',
    'password': '....',
    'database': '....'
}


def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        return None

def list_employees():
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, is_manager FROM employees ORDER BY id")
        employees = cursor.fetchall()
        
        print("\nMevcut Personel Listesi:")
        print("-" * 50)
        for id, name, is_manager in employees:
            print(f"ID: {id} | İsim: {name} | Müdür mü: {'Evet' if is_manager else 'Hayır'}")
        print("-" * 50)
        
        cursor.close()
        connection.close()
        return employees
    return []

def toggle_manager_status():
    employees = list_employees()
    if not employees:
        return
    
    while True:
        try:
            employee_id = int(input("\nMüdür durumunu değiştirmek istediğiniz personelin ID'sini girin: "))
            found = False
            
            for id, name, is_manager in employees:
                if id == employee_id:
                    found = True
                    connection = connect_db()
                    if connection:
                        cursor = connection.cursor()
                        new_status = not is_manager
                        
                        update_query = """
                            UPDATE employees 
                            SET is_manager = %s 
                            WHERE id = %s
                        """
                        cursor.execute(update_query, (new_status, employee_id))
                        connection.commit()
                        
                        print(f"\n{name} artık {'müdür' if new_status else 'müdür değil'}!")
                        
                        cursor.close()
                        connection.close()
                    break
            
            if not found:
                print("\nBu ID'ye sahip personel bulunamadı!")
            
            break
            
        except ValueError:
            print("\nLütfen geçerli bir ID girin!")

def main():
    while True:
        print("\n=== MÜDÜR YÖNETİM SİSTEMİ ===")
        print("1. Personel Listesini Göster")
        print("2. Müdür Durumunu Değiştir")
        print("3. Çıkış")
        
        choice = input("\nSeçiminiz (1-3): ")
        
        if choice == '1':
            list_employees()
        elif choice == '2':
            toggle_manager_status()
        elif choice == '3':
            print("\nProgram kapatılıyor...")
            break
        else:
            print("\nGeçersiz seçim! Lütfen 1-3 arası bir sayı girin.")

if __name__ == "__main__":
    main()
