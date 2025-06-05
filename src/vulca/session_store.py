import os
import uuid

SESSION_FILE = os.path.join(os.path.dirname(__file__), "../session_id.txt")

def create_session_id():
    """
    Generate UUID v4 dan simpan ke file. Return session ID tersebut.
    """
    session_id = str(uuid.uuid4())
    with open(SESSION_FILE, "w") as f:
        f.write(session_id)
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