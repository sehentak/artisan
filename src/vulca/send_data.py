import paho.mqtt.client as mqtt
import ssl
import certifi
import json
import time
from threading import Thread, Event
import struct
import threading
from vulca.get_config import load_mqtt_config

# Ambil konfigurasi MQTT dari API
mqtt_cfg = load_mqtt_config()
if not mqtt_cfg:
    print("[ERROR] Failed to load MQTT configuration.")
    exit(1)

print(f"[MQTT] Broker: {mqtt_cfg['broker']}")

# Konfigurasi MQTT
MQTT_BROKER = mqtt_cfg["broker"]
MQTT_PORT = mqtt_cfg["port"]
MQTT_TOPIC = mqtt_cfg["topic"]
USERNAME = mqtt_cfg["username"]
PASSWORD = mqtt_cfg["password"]

# === TAG DEFINITIONS ===
TAG_BT        = 0x01
TAG_LIMIT_BT  = 0x02
TAG_ET        = 0x03
TAG_LIMIT_ET  = 0x04
TAG_AIRFLOW   = 0x05
TAG_DRUMSPEED = 0x06
TAG_TIMESTAMP = 0x07
TAG_DELTA_BT  = 0x08
TAG_DELTA_ET  = 0x09
TAG_TIMER     = 0x0A

# === MQTT Setup ===
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(
    ca_certs=certifi.where(),
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1_2
)

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] on_connect triggered with RC={rc}")
    if rc == 0:
        print("[MQTT] Connected successfully.")
    else:
        print(f"[MQTT] Failed to connect, return code {rc}")

def on_log(client, userdata, level, buf):
    print(f"[MQTT LOG] {buf}")

client.on_connect = on_connect
client.on_log = on_log

# GANTI connect_async -> connect
print("[MQTT] Connecting (sync)...")
try:
    print("[MQTT] Starting loop...")
    client.loop_start()

    print("[MQTT] Connecting async...")
    client.connect_async(MQTT_BROKER, MQTT_PORT, 60)

    # 🕒 Tunggu sampai terkoneksi (maks. 5 detik)
    for i in range(10):
        if client.is_connected():
            print("[MQTT] Client is connected.")
            break
        print(f"[MQTT] Waiting for connection... ({i})")
        time.sleep(0.5)
    else:
        print("[MQTT] Timeout waiting for connection.")

except Exception as e:
    print(f"[MQTT ERROR] Connection failed: {e}")

# Cek thread aktif
print("[MQTT] Threads aktif:")
for t in threading.enumerate():
    print(f" - {t.name}")

# === Inisialisasi Threading ===
class MqttInterceptor:
    def __init__(self):
        self._stop_event = Event()
        self._last_send_time = 0
        self._min_interval = 1.0  # detik

    def publish_to_mqtt(self, et_value, bt_value, delta_et_value, delta_bt_value):
        Thread(target=self._publish_thread, args=(et_value, bt_value, delta_et_value, delta_bt_value)).start()

    def _publish_thread(self, et_value, bt_value, delta_et_value, delta_bt_value):
        now = time.time()
        if now - self._last_send_time < self._min_interval:
            return
        self._last_send_time = now

        if not self._stop_event.is_set():
            try:
                payload = (
                    self.encode_tlv_int(TAG_TIMESTAMP, int(time.time())) +
                    self.encode_tlv_int(TAG_ET, int(float(et_value))) +
                    self.encode_tlv_int(TAG_BT, int(float(bt_value))) +
                    self.encode_tlv_int(TAG_DELTA_BT, int(float(delta_bt_value))) +
                    self.encode_tlv_int(TAG_DELTA_ET, int(float(delta_et_value)))
                )

                result = client.publish(MQTT_TOPIC, payload)
                print(f"[MQTT PUBLISH] result={result.rc} topic='{MQTT_TOPIC}' ET={et_value}, BT={bt_value}")
            except Exception as e:
                print(f"[ERROR] MQTT Publish failed: {e}")

    def stop(self):
        self._stop_event.set()

    @staticmethod
    def encode_tlv_int(tag: int, value: int) -> bytes:
        val_bytes = struct.pack(">I", value)
        return struct.pack("B", tag) + struct.pack("B", len(val_bytes)) + val_bytes