import os
import time
import uuid
import threading
import requests
from typing import Optional

SESSION_FILE = os.path.join(os.path.dirname(__file__), "../session_id.txt")
MACHINE_ID = os.getenv("MACHINE_ID")
USER_ID = os.getenv("USER_ID", None)
HOST_URL = os.getenv("HOST_URL")
API_PRECREATE_URL = f"{HOST_URL}/batches"
API_STOP_URL = f"{API_PRECREATE_URL}/stop"
LOG_FILE = "/tmp/debug_event.log"

def send_json_post(endpoint: str, payload: dict, label: str = "REQUEST") -> None:
    """
    Kirim POST request dengan JSON dan log hasilnya ke file.
    """
    try:
        response = requests.post(endpoint, json=payload, timeout=3)
        response.raise_for_status()  # Raise exception for 4xx/5xx

        log = (
            f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {label} SUCCESS\n"
            f"Endpoint     : {endpoint}\n"
            f"Payload      : {payload}\n"
            f"Status Code  : {response.status_code}\n"
            f"Response     : {response.text}\n"
        )
    except requests.exceptions.HTTPError as http_err:
        log = (
            f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {label} HTTP ERROR\n"
            f"Endpoint     : {endpoint}\n"
            f"Payload      : {payload}\n"
            f"Status Code  : {getattr(http_err.response, 'status_code', '?')}\n"
            f"Response     : {getattr(http_err.response, 'text', 'No response')}\n"
            f"Error        : {http_err}\n"
        )
    except requests.exceptions.ConnectionError as conn_err:
        log = (
            f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {label} CONNECTION ERROR\n"
            f"Endpoint     : {endpoint}\n"
            f"Payload      : {payload}\n"
            f"Error        : {conn_err}\n"
        )
    except requests.exceptions.Timeout as timeout_err:
        log = (
            f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {label} TIMEOUT\n"
            f"Endpoint     : {endpoint}\n"
            f"Payload      : {payload}\n"
            f"Error        : {timeout_err}\n"
        )
    except requests.exceptions.RequestException as req_err:
        log = (
            f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {label} REQUEST ERROR\n"
            f"Endpoint     : {endpoint}\n"
            f"Payload      : {payload}\n"
            f"Error        : {req_err}\n"
        )
    except Exception as e:
        log = (
            f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {label} GENERAL EXCEPTION\n"
            f"Endpoint     : {endpoint}\n"
            f"Payload      : {payload}\n"
            f"Exception    : {e}\n"
        )

    try:
        with open(LOG_FILE, "a") as f:
            f.write(log)
    except Exception as file_err:
        print(f"Failed to write log: {file_err}")


def post_precreate(session_id: str):
    payload = {
        "uuid": session_id,
        "machine_id": MACHINE_ID
    }
    send_json_post(API_PRECREATE_URL, payload, label="PRECREATE")


def post_stop_session(session_id: str):
    payload = {"uuid": session_id}
    send_json_post(API_STOP_URL, payload, label="STOP SESSION")


def create_session_id() -> str:
    clear_session_id()

    session_id = str(uuid.uuid4())

    with open(SESSION_FILE, "w") as f:
        f.write(session_id)

    threading.Thread(target=post_precreate, args=(session_id,), daemon=True).start()
    return session_id

def stop_session_id():
    """
    Ambil session ID dari file dan kirim ke API stop.
    """
    session_id = load_session_id()
    if session_id:
        threading.Thread(target=post_stop_session, args=(session_id,), daemon=True).start()

def load_session_id() -> str:
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