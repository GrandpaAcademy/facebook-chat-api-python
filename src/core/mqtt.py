import json
import time
import asyncio
import random
import logging
import paho.mqtt.client as mqtt
from typing import Any, Dict, List, Optional, Callable
from ..utils.utils import get_guid, format_id

logger = logging.getLogger("fca_python.mqtt")

TOPICS = [
    "/legacy_web",
    "/webrtc",
    "/rtc_multi",
    "/onevc",
    "/br_sr",
    "/sr_res",
    "/t_ms",
    "/thread_typing",
    "/orca_typing_notifications",
    "/notify_disconnect",
    "/orca_presence",
    "/inbox",
    "/mercury",
    "/messaging_events",
    "/orca_message_notifications",
    "/pp",
    "/webrtc_response",
]

class MQTTClient:
    def __init__(self, ctx: Any, global_callback: Callable):
        self.ctx = ctx
        self.global_callback = global_callback
        self.session_id = random.randint(1, 9007199254740991)
        self.guid = get_guid()
        self.client: Optional[mqtt.Client] = None
        
    def _get_username(self) -> str:
        username = {
            "u": self.ctx.user_id,
            "s": self.session_id,
            "chat_on": self.ctx.options.get("online", True),
            "fg": False,
            "d": self.guid,
            "ct": "websocket",
            "aid": "219994525426954",
            "aids": None,
            "mqtt_sid": "",
            "cp": 3,
            "ecp": 10,
            "st": [],
            "pm": [],
            "dc": "",
            "no_auto_fg": True,
            "gas": None,
            "pack": [],
            "p": None,
            "php_override": ""
        }
        return json.dumps(username)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("FCA MQTT Connected")
            for topic in TOPICS:
                client.subscribe(topic)
            
            # Initial sync
            topic = "/messenger_sync_create_queue"
            queue = {
                "sync_api_version": 10,
                "max_deltas_able_to_process": 1000,
                "delta_batch_size": 500,
                "encoding": "JSON",
                "entity_fbid": self.ctx.user_id,
                "initial_titan_sequence_id": self.ctx.last_seq_id,
                "device_params": None,
            }
            client.publish(topic, json.dumps(queue), qos=1)
        else:
            logger.error(f"MQTT Connection failed with code {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            # logger.debug(f"MQTT Message on {topic}: {payload}")
            
            if topic == "/t_ms":
                if "firstDeltaSeqId" in payload and "syncToken" in payload:
                    self.ctx.last_seq_id = payload["firstDeltaSeqId"]
                    self.ctx.sync_token = payload["syncToken"]
                
                if "lastIssuedSeqId" in payload:
                    self.ctx.last_seq_id = int(payload["lastIssuedSeqId"])
                
                for delta in payload.get("deltas", []):
                    # Placeholder for parse_delta
                    self.global_callback(None, {"type": "delta", "delta": delta})
            
            elif topic in ["/thread_typing", "/orca_typing_notifications"]:
                typ = {
                    "type": "typ",
                    "isTyping": bool(payload.get("state")),
                    "from": str(payload.get("sender_fbid", "")),
                    "threadID": format_id(str(payload.get("thread") or payload.get("sender_fbid", "")))
                }
                self.global_callback(None, typ)
                
            elif topic == "/orca_presence":
                for item in payload.get("list", []):
                    presence = {
                        "type": "presence",
                        "userID": str(item["u"]),
                        "timestamp": item["l"] * 1000,
                        "statuses": item["p"]
                    }
                    self.global_callback(None, presence)

        except Exception as e:
            logger.error(f"Error parsing MQTT message: {e}")

    async def _heartbeat_loop(self):
        """Periodic presence update to prevent suspension."""
        while self.client and self.client.is_connected():
            try:
                from .api import set_active_status
                logger.debug("Sending heartbeat presence update...")
                await set_active_status(self.ctx, True)
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
            await asyncio.sleep(random.randint(30, 60)) # Every 30-60s

    def connect(self):
        # paho-mqtt version 1.x or 2.x? Let's check. 
        # Using CallbackAPIVersion for paho-mqtt 2.0+
        client = None
        try:
            from paho.mqtt.enums import CallbackAPIVersion
            client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1, client_id="mqttwsclient", transport="websockets", protocol=mqtt.MQTTv31)
        except (ImportError, AttributeError):
            client = mqtt.Client(client_id="mqttwsclient", transport="websockets", protocol=mqtt.MQTTv31)
            
        self.client = client
        self.client.username_pw_set(self._get_username())
        
        # SSL and Cookies
        host = f"wss://edge-chat.facebook.com/chat?sid={self.session_id}&cid={self.guid}"
        if self.ctx.region:
            host = f"wss://edge-chat.facebook.com/chat?region={self.ctx.region.lower()}&sid={self.session_id}&cid={self.guid}"
            
        cookie_str = "; ".join([f"{c.name}={c.value}" for c in self.ctx.client.cookies.jar])
        
        self.client.ws_set_options(path=host.split(".com")[1], headers={
            "Cookie": cookie_str,
            "Origin": "https://www.facebook.com",
            "User-Agent": self.ctx.options.get("userAgent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"),
            "Referer": "https://www.facebook.com/",
            "Host": "edge-chat.facebook.com",
            "Sec-WebSocket-Protocol": "mqtt"
        })
        
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        # Connect to edge-chat.facebook.com:443
        self.client.tls_set() # Enable TLS for wss
        self.client.connect("edge-chat.facebook.com", 443, keepalive=60)
        self.client.loop_start()
        
        # Start heartbeat
        import asyncio
        asyncio.create_task(self._heartbeat_loop())

def listen_mqtt(ctx: Any, global_callback: Callable):
    mqtt_client = MQTTClient(ctx, global_callback)
    mqtt_client.connect()
    ctx.mqtt_client = mqtt_client
    return mqtt_client
