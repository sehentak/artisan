from vulca.get_config import load_mqtt_config
from vulca.mqtt_helper import VulcaMQTT

mqtt_cfg = load_mqtt_config()
mqtt = VulcaMQTT(
    broker=mqtt_cfg["broker"],
    port=mqtt_cfg["port"],
    username=mqtt_cfg["username"],
    password=mqtt_cfg["password"],
    topic=mqtt_cfg["topic"],
    use_queue=True
)