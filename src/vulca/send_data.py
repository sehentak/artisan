import os
import time
from vulca.mqtt_instance import mqtt
from vulca.tlv_util import (
    encode_tlv_int, encode_tlv_str,  # pastikan encode_tlv_str ada
    TAG_TIMESTAMP, TAG_ET, TAG_BT,
    TAG_DELTA_ET, TAG_DELTA_BT,
    TAG_AIRFLOW, TAG_DRUMSPEED
)

# Tag baru untuk session_id
TAG_SESSION_ID = 0x20

SESSION_FILE = os.path.join(os.path.dirname(__file__), "../session_id.txt")

def load_session_id():
    if not os.path.exists(SESSION_FILE):
        return ""
    with open(SESSION_FILE, "r") as f:
        return f.read().strip()

# === Fungsi untuk kirim data TLV roasting
def mqtt_send_tlv(
    et: float = 0,
    bt: float = 0,
    delta_et: float = 0,
    delta_bt: float = 0,
    airflow: int = 0,
    drum_speed: int = 0,
    timestamp: int = None
):
    """
    Kirim data roasting dalam format TLV via MQTT.
    Semua parameter bersifat opsional dan akan default ke 0 jika tidak diberikan.
    """

    if timestamp is None:
        timestamp = int(time.time())

    payload = (
        encode_tlv_int(TAG_TIMESTAMP, timestamp) +
        encode_tlv_int(TAG_ET, int(float(et))) +
        encode_tlv_int(TAG_BT, int(float(bt))) +
        encode_tlv_int(TAG_DELTA_BT, int(float(delta_bt))) +
        encode_tlv_int(TAG_DELTA_ET, int(float(delta_et))) +
        encode_tlv_int(TAG_AIRFLOW, int(airflow)) +
        encode_tlv_int(TAG_DRUMSPEED, int(drum_speed))
    )

    session_id = load_session_id()
    if session_id:
        payload += encode_tlv_str(TAG_SESSION_ID, session_id)

    mqtt.send(payload)