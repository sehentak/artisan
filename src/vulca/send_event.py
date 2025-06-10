from vulca.mqtt_instance import mqtt
from vulca.tlv_util import encode_tlv_int, encode_tlv_str, TAG_EVENT, TAG_TIMESTAMP
import time

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