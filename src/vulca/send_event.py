from vulca.get_config import load_mqtt_config
from vulca.mqtt_helper import VulcaMQTT
import struct
import time

# === TAG DEFINITIONS ===
TAG_EVENT     = 0x10
TAG_TIMESTAMP = 0x07

# === Load config & tambahkan "/events" ke topic
mqtt_cfg = load_mqtt_config()
event_topic = mqtt_cfg["topic"].rstrip("/") + "/events"

mqtt = VulcaMQTT(
    broker=mqtt_cfg["broker"],
    port=mqtt_cfg["port"],
    username=mqtt_cfg["username"],
    password=mqtt_cfg["password"],
    topic=event_topic,
    use_queue=True
)

# === Encode TLV util
def encode_tlv_str(tag: int, value: str) -> bytes:
    val_bytes = value.encode("utf-8")
    return struct.pack("B", tag) + struct.pack("B", len(val_bytes)) + val_bytes

def encode_tlv_int(tag: int, value: int) -> bytes:
    val_bytes = struct.pack(">I", value)
    return struct.pack("B", tag) + struct.pack("B", len(val_bytes)) + val_bytes

# === Fungsi untuk kirim event TLV
def mqtt_send_event(event: str, timestamp: int = None):
    """
    Kirim event string dalam format TLV ke MQTT.
    Contoh event: 'ON_MONITOR', 'OFF_MONITOR', 'ROAST_START', dll.
    """
    if timestamp is None:
        timestamp = int(time.time())

    payload = (
        encode_tlv_int(TAG_TIMESTAMP, timestamp) +
        encode_tlv_str(TAG_EVENT, event)
    )
    mqtt.send(payload)