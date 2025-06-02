import os
import json
import requests
from pathlib import Path

CACHE_FILE = Path("/tmp/configs.json")
MACHINE_ID = os.getenv("MACHINE_ID")
HOST_URL = os.getenv("HOST_URL")
API_URL = f"{HOST_URL}/configs/{MACHINE_ID}"

def fetch_and_cache_config():
    try:
        resp = requests.get(API_URL, timeout=5)
        data = resp.json()
        if data.get("isSuccess"):
            CACHE_FILE.write_text(json.dumps(data["data"]))
            return data["data"]
        raise Exception(f"[CONFIG] Failed: {data.get('message')}")
    except Exception as e:
        print(f"[CONFIG] Error fetching config: {e}")
        if CACHE_FILE.exists():
            print("[CONFIG] Using cached config instead.")
            return json.loads(CACHE_FILE.read_text())
        raise e

def load_mqtt_config():
    config = fetch_and_cache_config()
    mqtt = config["mqtt"]
    topic_cfg = mqtt["topics"][0]
    pub_cred = next(c for c in topic_cfg["credentials"] if c["type"] == "publisher")
    return {
        "broker": mqtt["broker"],
        "port": mqtt["port"],
        "topic": topic_cfg["topic"],
        "username": pub_cred["user"],
        "password": pub_cred["pass"],
    }