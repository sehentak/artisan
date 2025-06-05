from vulca.mqtt_instance import mqtt
import struct
import time

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

# === Encode TLV util
def encode_tlv_int(tag: int, value: int) -> bytes:
    val_bytes = struct.pack(">I", value)
    return struct.pack("B", tag) + struct.pack("B", len(val_bytes)) + val_bytes

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
    mqtt.send(payload)