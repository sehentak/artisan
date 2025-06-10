import os
import uuid
import threading
import requests

SESSION_FILE = os.path.join(os.path.dirname(__file__), "../session_id.txt")
MACHINE_ID = os.getenv("MACHINE_ID")
USER_ID = os.getenv("USER_ID", None)
HOST_URL = os.getenv("HOST_URL")
API_URL = f"{HOST_URL}/batches"

def create_session_id():
    """
    Generate UUID v4, simpan ke file, dan post ke API precreate.
    Return session ID tersebut.
    """
    session_id = str(uuid.uuid4())
    
    # Simpan ke file
    with open(SESSION_FILE, "w") as f:
        f.write(session_id)
    
    # Kirim ke API precreate
    def post_precreate():
        try:
            payload = {
                "uuid": session_id,
                "machine_id": MACHINE_ID
            }
            if USER_ID:
                payload["user_id"] = USER_ID

            requests.post(API_URL, json=payload, timeout=3)
        except Exception as e:
            print(f"[session_id] Precreate API failed: {e}")
    
    threading.Thread(target=post_precreate, daemon=True).start()

    return session_id

def load_session_id() -> str:
    """
    Ambil session ID dari file. Return "" jika tidak ada.
    """
    if not os.path.exists(SESSION_FILE):
        return ""
    with open(SESSION_FILE, "r") as f:
        return f.read().strip()

def clear_session_id():
    """
    Hapus file session ID.
    """
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)