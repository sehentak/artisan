from vulca.mqtt_instance import mqtt
import struct
import time

# === TAG DEFINITIONS ===
TAG_EVENT     = 0x10
TAG_TIMESTAMP = 0x07

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

    # Send ke topic tambahan /events
    topic_with_suffix = mqtt.topic.rstrip("/") + "/events"
    mqtt.send(payload, topic=topic_with_suffix)