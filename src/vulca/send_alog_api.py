# send_alog_api.py
import os
import requests
import threading
import time

HOST_URL = os.getenv("HOST_URL")
UPLOAD_URL = f"{HOST_URL}/batches/upload-data"
SESSION_FILE = os.path.join(os.path.dirname(__file__), "../session_id.txt")
LOG_FILE = "/tmp/debug_event.log"

def log_to_file(text: str):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}")
    except:
        pass

def read_uuid_from_session():
    try:
        with open(SESSION_FILE, 'r') as f:
            return f.read().strip()
    except Exception as e:
        log_to_file(f"[ERROR] Tidak bisa baca session ID: {e}")
        return None

def send_alog_to_api(alog_content: str):
    def post_data():
        try:
            uuid = read_uuid_from_session()
            if not uuid:
                log_to_file("[ERROR] UUID tidak ditemukan.")
                return
            payload = {
                "uuid": uuid,
                "data": alog_content
            }
            log_to_file(f"[INFO] Kirim ALOG ke {UPLOAD_URL} UUID={uuid}")
            response = requests.post(UPLOAD_URL, json=payload, timeout=10)
            log_to_file(f"Response Code: {response.status_code}\nResponse Body: {response.text}")
        except Exception as e:
            log_to_file(f"[ERROR] Gagal kirim ALOG: {e}")

    threading.Thread(target=post_data, daemon=True).start()

# Untuk CLI manual (debug)
if __name__ == "__main__":
    try:
        alog_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp/alog_body.txt"))
        with open(alog_path, "r", encoding="utf-8") as f:
            content = f.read()
        send_alog_to_api(content)
    except Exception as e:
        log_to_file(f"[ERROR] CLI mode gagal: {e}")