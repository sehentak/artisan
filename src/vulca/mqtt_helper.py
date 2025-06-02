import time
import ssl
import certifi
import threading
from queue import Queue, Empty
import paho.mqtt.client as mqtt

class VulcaMQTT:
    def __init__(self, broker, port, username, password, client_id="", tls=True, keepalive=60, topic=None, use_queue=False):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.keepalive = keepalive
        self.topic = topic
        self.use_queue = use_queue

        self.client = mqtt.Client(client_id=self.client_id)
        self._connected = False
        self._queue = Queue()

        self._init_client(tls)
        self._connect_and_wait()

        if self.use_queue:
            self._start_queue_worker()

    def _init_client(self, tls):
        self.client.username_pw_set(self.username, self.password)

        if tls:
            self.client.tls_set(
                ca_certs=certifi.where(),
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_log = self._on_log

    def _connect_and_wait(self, wait_timeout=5):
        print("[MQTT] Starting loop...")
        self.client.loop_start()
        print("[MQTT] Connecting async...")
        self.client.connect_async(self.broker, self.port, self.keepalive)

        for i in range(int(wait_timeout * 2)):
            if self.client.is_connected():
                print("[MQTT] Client is connected.")
                return
            print(f"[MQTT] Waiting for connection... ({i})")
            time.sleep(0.5)

        print("[MQTT] Timeout. Fallback to sync connect...")
        try:
            self.client.connect(self.broker, self.port, self.keepalive)
            self._connected = True
        except Exception as e:
            print(f"[MQTT ERROR] Sync fallback failed: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] on_connect RC={rc}")
        if rc == 0:
            self._connected = True
            print("[MQTT] Connected successfully.")
        else:
            print(f"[MQTT] Failed to connect with RC={rc}")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        print(f"[MQTT] Disconnected (RC={rc})")

    def _on_log(self, client, userdata, level, buf):
        print(f"[MQTT LOG] {buf}")

    def _start_queue_worker(self):
        def worker():
            while True:
                try:
                    topic, payload = self._queue.get(timeout=1)
                    self._publish(topic, payload)
                except Empty:
                    continue
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def send(self, payload: bytes, topic: str = None):
        topic_to_use = topic or self.topic
        if not topic_to_use:
            print("[MQTT] No topic specified.")
            return

        if self.use_queue:
            self._queue.put((topic_to_use, payload))
        else:
            self._publish(topic_to_use, payload)

    def _publish(self, topic: str, payload: bytes):
        if not self._connected:
            print("[MQTT] Not connected. Cannot send.")
            return
        result = self.client.publish(topic, payload)
        print(f"[MQTT] Publish result={result.rc} topic='{topic}'")

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()