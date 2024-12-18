import RPi.GPIO as GPIO
import time

# GPIO modunu ayarla
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pin tanımlamaları
PIR_PIN = 17            # Hareket sensörü (PIN 11)
IC_YESIL_LED = 24      # İç yeşil LED - Otomatik ışık (PIN 18)
DIS_YESIL_LED = 23     # Dış yeşil LED - Boş (PIN 16)
DIS_KIRMIZI_LED = 25   # Dış kırmızı LED - Dolu (PIN 22)

# Pin ayarları
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(IC_YESIL_LED, GPIO.OUT)
GPIO.setup(DIS_YESIL_LED, GPIO.OUT)
GPIO.setup(DIS_KIRMIZI_LED, GPIO.OUT)

# Başlangıçta dış yeşil LED yanık, diğerleri sönük
GPIO.output(DIS_YESIL_LED, GPIO.HIGH)
GPIO.output(DIS_KIRMIZI_LED, GPIO.LOW)
GPIO.output(IC_YESIL_LED, GPIO.LOW)

# Hareket algılandıktan sonra bekleme süresi
HAREKET_BEKLEME_SURESI = 30

son_hareket_zamani = 0
lavabo_dolu = False

try:
    print("\n=== LAVABO DURUM SİSTEMİ ===")
    print("Sistem başlatıldı")
    print("Durum: LAVABO BOŞ")
    
    while True:
        simdiki_zaman = time.time()
        
        if GPIO.input(PIR_PIN):  # Hareket algılandı
            if not lavabo_dolu:  # Durum değiştiğinde yazdır
                print("\nDurum: LAVABO DOLU")
                print("Otomatik Işık: AÇIK")
                # Kırmızı LED ve iç yeşil LED'i yak, dış yeşil LED'i söndür
                GPIO.output(DIS_KIRMIZI_LED, GPIO.HIGH)
                GPIO.output(IC_YESIL_LED, GPIO.HIGH)
                GPIO.output(DIS_YESIL_LED, GPIO.LOW)
            
            son_hareket_zamani = simdiki_zaman
            lavabo_dolu = True
            
        else:
            # Son hareketten beri geçen süreyi kontrol et
            if (simdiki_zaman - son_hareket_zamani) > HAREKET_BEKLEME_SURESI:
                if lavabo_dolu:  # Durum değiştiğinde yazdır
                    print("\nDurum: LAVABO BOŞ")
                    # Sadece dış yeşil LED'i yak, diğerlerini söndür
                    GPIO.output(DIS_YESIL_LED, GPIO.HIGH)
                    GPIO.output(DIS_KIRMIZI_LED, GPIO.LOW)
                    GPIO.output(IC_YESIL_LED, GPIO.LOW)
                    
                lavabo_dolu = False
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\nProgram sonlandırılıyor...")
    GPIO.cleanup()
