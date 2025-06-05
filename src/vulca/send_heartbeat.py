import time
import threading
import struct
from vulca.mqtt_instance import mqtt  # pakai shared instance

# TAG TLV
TAG_TIMESTAMP = 0x07
TAG_EVENT     = 0x10

def encode_tlv_str(tag: int, value: str) -> bytes:
    val_bytes = value.encode("utf-8")
    return struct.pack("B", tag) + struct.pack("B", len(val_bytes)) + val_bytes

def encode_tlv_int(tag: int, value: int) -> bytes:
    val_bytes = struct.pack(">I", value)
    return struct.pack("B", tag) + struct.pack("B", len(val_bytes)) + val_bytes

def start_heartbeat():
    def loop():
        while True:
            try:
                timestamp = int(time.time())
                payload = (
                    encode_tlv_int(TAG_TIMESTAMP, timestamp) +
                    encode_tlv_str(TAG_EVENT, "HEARTBEAT")
                )
                topic = mqtt.topic.rstrip("/") + "/heartbeat"
                mqtt.send(payload, topic=topic)
                print(f"[HEARTBEAT] Sent at {timestamp}")
                time.sleep(5)
            except Exception as e:
                print(f"[HEARTBEAT ERROR] {e}")
                time.sleep(5)
    threading.Thread(target=loop, daemon=True).start()