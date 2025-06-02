import time
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vulca.send_data import mqtt_send_tlv

def simulate():
    print("[SIMULATOR] Start publishing dummy TLV every 1s...")
    while True:
        et = random.uniform(100, 150)
        bt = random.uniform(90, 140)
        delta_et = round(et - 100, 2)
        delta_bt = round(bt - 90, 2)
        airflow = random.randint(20, 80)
        drum_speed = random.randint(30, 70)

        print(f"[SIMULATOR] ET={et:.2f} BT={bt:.2f} ΔET={delta_et} ΔBT={delta_bt} AF={airflow} DR={drum_speed}")
        mqtt_send_tlv(
            et=et,
            bt=bt,
            delta_et=delta_et,
            delta_bt=delta_bt,
            airflow=airflow,
            drum_speed=drum_speed
        )
        time.sleep(1)

if __name__ == "__main__":
    simulate()