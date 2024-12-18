import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

def setup_aws_iot():
    # AWS IoT ayarları
    endpoint = "a2d7b27136j9em-ats.iot.eu-central-1.amazonaws.com"
    client_id = "RaspberryPi_OfficeSystem"
    root_ca_path = "/home/pi/akilliofis/certs/Amazon-root-CA-1.pem"
    private_key_path = "/home/pi/akilliofis/certs/private.pem.key"
    certificate_path = "/home/pi/akilliofis/certs/certificate.pem.crt"

    # AWS IoT Client oluştur
    mqtt_client = AWSIoTMQTTClient(client_id)
    mqtt_client.configureEndpoint(endpoint, 8883)
    mqtt_client.configureCredentials(root_ca_path, private_key_path, certificate_path)

    # MQTT bağlantı ayarları
    mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    mqtt_client.configureOfflinePublishQueueing(-1)
    mqtt_client.configureDrainingFrequency(2)
    mqtt_client.configureConnectDisconnectTimeout(10)
    mqtt_client.configureMQTTOperationTimeout(5)

    # Bağlantıyı başlat
    try:
        mqtt_client.connect()
        print("AWS IoT bağlantısı başarılı")
        return mqtt_client
    except Exception as e:
        print(f"AWS IoT bağlantı hatası: {str(e)}")
        return None
