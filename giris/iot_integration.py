import time
import json
import logging
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from datetime import datetime

# Logging ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# AWS IoT ayarları
ENDPOINT = "acme69k7r90ak-ats.iot.eu-central-1.amazonaws.com"
CLIENT_ID = "RaspberryPi_OfficeSystem"
PATH_TO_CERT = "/home/pi/certs/certificate.pem.crt"
PATH_TO_KEY = "/home/pi/certs/private.pem.key"
PATH_TO_ROOT = "/home/pi/certs/root.pem"
TOPIC = "office/entries"

def setup_aws_iot():
    # Önce dosyaların varlığını kontrol et
    if not all([os.path.exists(p) for p in [PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT]]):
        print("Hata: Sertifika dosyalarından biri veya birkaçı bulunamadı!")
        print(f"Sertifika dosyası mevcut: {os.path.exists(PATH_TO_CERT)}")
        print(f"Private key dosyası mevcut: {os.path.exists(PATH_TO_KEY)}")
        print(f"Root CA dosyası mevcut: {os.path.exists(PATH_TO_ROOT)}")
        raise FileNotFoundError("Sertifika dosyaları eksik!")

    myAWSIoTMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
    myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
    myAWSIoTMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)
    myAWSIoTMQTTClient.configureDrainingFrequency(2)
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(20)
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(10)

    print("AWS IoT'ye bağlanılıyor...")
    
    try:
        connected = myAWSIoTMQTTClient.connect()
        print("Bağlantı başarılı!")
        return myAWSIoTMQTTClient
    except Exception as e:
        print(f"Bağlantı hatası: {str(e)}")
        raise

def publish_entry(client, person_name, status, entry_time):
    message = {
        "device_id": CLIENT_ID,
        "timestamp": entry_time.strftime("%Y-%m-%d %H:%M:%S"),
        "person_name": person_name,
        "status": status,
        "office_location": "Ana Ofis"
    }
    
    try:
        result = client.publish(TOPIC, json.dumps(message), 1)
        print(f"AWS IoT mesajı gönderildi: {message}")
        return True
    except Exception as e:
        print(f"AWS IoT gönderim hatası: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        client = setup_aws_iot()
        test_message = {
            "test": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "Test bağlantısı başarılı!"
        }
        result = client.publish(TOPIC, json.dumps(test_message), 1)
        print(f"Publish sonucu: {result}")
        print("Test mesajı başarıyla gönderildi!")
        client.disconnect()
    except Exception as e:
        print(f"Test hatası: {str(e)}")
        logger.exception("Detaylı hata:")
