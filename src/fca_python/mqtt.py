import json
import random
import time
import logging
from typing import Any, Dict, Optional, List, Callable
import paho.mqtt.client as mqtt
from .utils import get_guid

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
    def __init__(self, ctx: Any, callback: Callable):
        self.ctx = ctx
        self.callback = callback
        self.session_id = random.randint(1, 9007199254740991)
        self.guid = get_guid()
        
        username = {
            "u": ctx.user_id,
            "s": self.session_id,
            "chat_on": ctx.options.get("online", False),
            "fg": False,
            "d": self.guid,
            "ct": "websocket",
            "aid": "219994525426954",
            "cp": 3,
            "ecp": 10,
            "no_auto_fg": True,
        }
        
        self.client = mqtt.Client(client_id="mqttwsclient", transport="websockets")
        self.client.username_pw_set(json.dumps(username))
        
        host = ctx.mqtt_endpoint
        if not host:
            host = f"wss://edge-chat.facebook.com/chat?region={ctx.region.lower()}&sid={self.session_id}&cid={self.guid}"
        else:
            host = f"{host}&sid={self.session_id}&cid={self.guid}"
            
        self.host = host
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_error = self.on_error
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT Connected")
            for topic in TOPICS:
                client.subscribe(topic)
                
            queue = {
                "sync_api_version": 10,
                "max_deltas_able_to_process": 1000,
                "delta_batch_size": 500,
                "encoding": "JSON",
                "entity_fbid": self.ctx.user_id,
            }
            
            if self.ctx.sync_token:
                topic = "/messenger_sync_get_diffs"
                queue["last_seq_id"] = self.ctx.last_seq_id
                queue["sync_token"] = self.ctx.sync_token
            else:
                topic = "/messenger_sync_create_queue"
                queue["initial_titan_sequence_id"] = self.ctx.last_seq_id
                queue["device_params"] = None
                
            client.publish(topic, json.dumps(queue), qos=1)
        else:
            logger.error(f"MQTT Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic == "/t_ms":
                if "firstDeltaSeqId" in payload and "syncToken" in payload:
                    self.ctx.last_seq_id = payload["firstDeltaSeqId"]
                    self.ctx.sync_token = payload["syncToken"]
                
                if "lastIssuedSeqId" in payload:
                    self.ctx.last_seq_id = int(payload["lastIssuedSeqId"])
                    
                for delta in payload.get("deltas", []):
                    # parseDelta logic goes here
                    self.callback({"type": "message", "delta": delta})
            
            elif topic in ["/thread_typing", "/orca_typing_notifications"]:
                typ = {
                    "type": "typ",
                    "isTyping": bool(payload.get("state")),
                    "from": str(payload.get("sender_fbid")),
                    "threadID": str(payload.get("thread") or payload.get("sender_fbid"))
                }
                self.callback(typ)
                
        except Exception as e:
            logger.error(f"Error parsing MQTT message: {e}")

    def on_error(self, client, userdata, level, string):
        logger.error(f"MQTT Error: {string}")

    def listen(self):
        # We need to extract the hostname and part from the wss:// URL
        # paho-mqtt's connect() takes (host, port)
        from urllib.parse import urlparse
        parsed = urlparse(self.host)
        
        # Paho MQTT doesn't natively support WSS with path well in connect()
        # It expects the host and port. For websockets with custom path/query,
        # we might need to use the 'ws_path' option in client.ws_set_options().
        
        self.client.ws_set_options(path=f"{parsed.path}?{parsed.query}")
        
        # Facebook uses port 443 for WSS
        self.client.tls_set() # Required for WSS
        self.client.connect(parsed.hostname, 443)
        self.client.loop_start()

def listen_mqtt(ctx: Any, callback: Callable):
    client = MQTTClient(ctx, callback)
    client.listen()
    return client
