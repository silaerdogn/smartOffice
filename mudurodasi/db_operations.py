import mysql.connector
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="database-1.cb8k2y8iy0eb.eu-central-1.rds.amazonaws.com",
                user="admin",
                password="raspberrypi",
                database="office_management"
            )
            self.cursor = self.connection.cursor()
            print("Veritabanı bağlantısı başarılı!")
        except Exception as e:
            print(f"Veritabanı bağlantı hatası: {str(e)}")
            raise

    def verify_manager(self, name):
        try:
            self.cursor.execute("""
                SELECT is_manager 
                FROM employees 
                WHERE name = %s AND is_manager = TRUE
            """, (name,))
            result = self.cursor.fetchone()
            return bool(result)
        except Exception as e:
            print(f"Veritabanı sorgulama hatası: {str(e)}")
            return False

    def log_access(self, person_name, confidence, status, office_location="Müdür Odası"):
        try:
            # Son durumu kontrol et
            self.cursor.execute("""
                SELECT status FROM employee_entries 
                WHERE employee_name = %s 
                ORDER BY entry_time DESC LIMIT 1
            """, (person_name,))
            last_status = self.cursor.fetchone()
            
            # Eğer son durum GIRIS ise CIKIS, değilse GIRIS yap
            new_status = 'CIKIS' if last_status and last_status[0] == 'GIRIS' else 'GIRIS'
            
            # Access logs tablosuna kaydet
            sql_access = """
            INSERT INTO access_logs 
            (person_name, access_time, confidence, status, office_location)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql_access, (person_name, datetime.now(), confidence, status, office_location))
            
            # Employee entries tablosuna kaydet
            sql_entry = """
            INSERT INTO employee_entries 
            (employee_name, entry_time, status, confidence, action)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql_entry, (person_name, datetime.now(), new_status, confidence, status))
            
            self.connection.commit()
            print(f"Giriş kaydı başarıyla oluşturuldu: {person_name}")
            return new_status
            
        except Exception as e:
            print(f"Log kayıt hatası: {str(e)}")
            return None

    def save_face_data(self, name, role, face_data):
        try:
            # Önce varolan kaydı kontrol et
            self.cursor.execute("SELECT id FROM authorized_users WHERE name = %s", (name,))
            existing = self.cursor.fetchone()
            
            if existing:
                # Güncelle
                sql = """
                UPDATE authorized_users 
                SET face_data = %s, role = %s, is_manager = %s
                WHERE name = %s
                """
                self.cursor.execute(sql, (face_data, role, True if role == "manager" else False, name))
            else:
                # Yeni kayıt ekle
                sql = """
                INSERT INTO authorized_users 
                (name, role, is_manager, face_data)
                VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(sql, (name, role, True if role == "manager" else False, face_data))
            
            self.connection.commit()
            print(f"Yüz verileri başarıyla {'güncellendi' if existing else 'kaydedildi'}: {name}")
        except Exception as e:
            print(f"Yüz verisi kayıt hatası: {str(e)}")

    def get_employee_status(self, name):
        """Çalışanın son durumunu kontrol et"""
        try:
            self.cursor.execute("""
                SELECT status, entry_time 
                FROM employee_entries 
                WHERE employee_name = %s 
                ORDER BY entry_time DESC LIMIT 1
            """, (name,))
            result = self.cursor.fetchone()
            if result:
                return {"status": result[0], "last_time": result[1]}
            return None
        except Exception as e:
            print(f"Durum sorgulama hatası: {str(e)}")
            return None

    def get_all_managers(self):
        """Tüm müdürleri ve durumlarını getir"""
        try:
            self.cursor.execute("""
                SELECT name FROM employees 
                WHERE is_manager = TRUE
            """)
            managers = self.cursor.fetchall()
            
            manager_statuses = []
            for manager in managers:
                status = self.get_employee_status(manager[0])
                manager_statuses.append({
                    "name": manager[0],
                    "status": status["status"] if status else "DIŞARIDA",
                    "last_time": status["last_time"] if status else None
                })
            return manager_statuses
        except Exception as e:
            print(f"Müdür listesi sorgulama hatası: {str(e)}")
            return []

    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
            print("Veritabanı bağlantısı kapatıldı.")
        except Exception as e:
            print(f"Bağlantı kapatma hatası: {str(e)}")
