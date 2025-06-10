# === vulca/tlv_util.py ===
import struct

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
TAG_EVENT     = 0x10
TAG_TIMER     = 0x0A

def encode_tlv_str(tag: int, value: str) -> bytes:
    val_bytes = value.encode("utf-8")
    return struct.pack("B", tag) + struct.pack("B", len(val_bytes)) + val_bytes

def encode_tlv_int(tag: int, value: int) -> bytes:
    val_bytes = struct.pack(">I", value)
    return struct.pack("B", tag) + struct.pack("B", len(val_bytes)) + val_bytes