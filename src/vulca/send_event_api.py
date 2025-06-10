import os
import time
import threading
import requests

MACHINE_ID = os.getenv("MACHINE_ID")
HOST_URL = os.getenv("HOST_URL")
API_URL = f"{HOST_URL}/events"
SESSION_FILE = os.path.join(os.path.dirname(__file__), "../session_id.txt")
LOG_FILE = "/tmp/debug_event.log"

def load_session_id():
    if not os.path.exists(SESSION_FILE):
        return ""
    with open(SESSION_FILE, "r") as f:
        return f.read().strip()

def send_event_to_api(event: str, timestamp: int = None):
    if timestamp is None:
        timestamp = int(time.time())

    data = {
        "machine_id": MACHINE_ID,
        "event": event,
        "timestamp": timestamp
    }

    # Tambahkan session_id kalau event-nya start/stop
    if event in ("START_RECORD", "STOP_RECORD"):
        session_id = load_session_id()
        if session_id:
            data["session_id"] = session_id

    def post_data():
        try:
            response = requests.post(API_URL, json=data, timeout=3)
            log = (
                f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] EVENT SENT\n"
                f"Request JSON : {data}\n"
                f"Response Code: {response.status_code}\n"
                f"Response Body: {response.text}\n"
            )
        except Exception as e:
            log = (
                f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] ERROR\n"
                f"Request JSON : {data}\n"
                f"Exception     : {e}\n"
            )

        try:
            with open(LOG_FILE, "a") as f:
                f.write(log)
        except Exception as file_err:
            # optional: fallback log
            print(f"Failed to write to log file: {file_err}")

    threading.Thread(target=post_data, daemon=True).start()