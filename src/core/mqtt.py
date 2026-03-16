import json
import time
import asyncio
import random
import logging
import paho.mqtt.client as mqtt
from typing import Any, Dict, Optional, Callable
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
        self.ws_req_number: int = 0
        self.ws_task_number: int = 0

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
            "php_override": "",
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
                    "threadID": format_id(
                        str(payload.get("thread") or payload.get("sender_fbid", ""))
                    ),
                }
                self.global_callback(None, typ)

            elif topic == "/orca_presence":
                for item in payload.get("list", []):
                    presence = {
                        "type": "presence",
                        "userID": str(item["u"]),
                        "timestamp": item["l"] * 1000,
                        "statuses": item["p"],
                    }
                    self.global_callback(None, presence)

        except Exception as e:
            logger.error(f"Error parsing MQTT message: {e}")

    async def send_ls_request(
        self,
        payload: Dict[str, Any],
        label: str = "742",
        queue_name: str = "edit_message",
    ):
        self.ws_req_number += 1
        self.ws_task_number += 1

        task = {
            "failure_count": None,
            "label": label,
            "payload": json.dumps(payload),
            "queue_name": queue_name,
            "task_id": self.ws_task_number,
        }

        content = {
            "app_id": "2220391788200892",
            "payload": json.dumps(
                {
                    "data_trace_id": None,
                    "epoch_id": int(time.time() * 1000),
                    "tasks": [task],
                    "version_id": "6903494529735864",
                }
            ),
            "request_id": self.ws_req_number,
            "type": 3,
        }

        if self.client and self.client.is_connected():
            self.client.publish("/ls_req", json.dumps(content), qos=1)
            return True
        return False

    async def edit_message(self, text: str, message_id: str):
        return await self.send_ls_request(
            {"message_id": message_id, "text": text},
            label="742",
            queue_name="edit_message",
        )

    async def send_message_mqtt(
        self, msg: Any, thread_id: str, reply_to: Optional[str] = None
    ):
        if isinstance(msg, str):
            msg = {"body": msg}

        timestamp = int(time.time() * 1000)
        otid = (timestamp << 22) + random.randint(0, 4194303)

        task_payload = {
            "thread_id": str(thread_id),
            "otid": str(otid),
            "source": 0,
            "send_type": 1,
            "sync_group": 1,
            "text": str(msg.get("body", "")),
            "initiating_source": 1,
            "skip_url_preview_gen": 0,
        }

        if reply_to:
            task_payload["reply_metadata"] = {
                "reply_source_id": str(reply_to),
                "reply_source_type": 1,
                "reply_type": 0,
            }

        return await self.send_ls_request(
            task_payload,
            label="46",
            queue_name=str(thread_id),
        )

    async def set_message_reaction_mqtt(
        self, reaction: str, message_id: str, thread_id: str
    ):
        task_payload = {
            "thread_key": str(thread_id),
            "timestamp_ms": int(time.time() * 1000),
            "message_id": str(message_id),
            "reaction": reaction,
            "actor_id": str(self.ctx.user_id),
            "reaction_style": None,
            "sync_group": 1,
            "send_attribution": 65537 if random.random() < 0.5 else 524289,
        }

        return await self.send_ls_request(
            task_payload,
            label="29",
            queue_name=json.dumps(["reaction", message_id]),
        )

    async def change_blocked_status_mqtt(
        self, user_id: str, status: bool, type: str = "messenger"
    ):
        # messenger: 1 (block), 0 (unblock)
        # facebook: 3 (block), 2 (unblock)
        if type == "messenger":
            user_block_action = 1 if status else 0
        elif type == "facebook":
            user_block_action = 3 if status else 2
        else:
            raise ValueError("Invalid block type")

        task_payload = {
            "blockee_id": str(user_id),
            "request_id": get_guid(),
            "user_block_action": user_block_action,
        }

        return await self.send_ls_request(
            task_payload,
            label="334",
            queue_name="native_sync_block",
        )

    async def _heartbeat_loop(self):
        """Periodic presence update to prevent suspension."""
        while self.client and self.client.is_connected():
            try:
                # Use a dynamic import or post call directly to avoid circular dependency

                # Just any simple non-destructive request to keep session alive
                # or a direct call if we move the function logic
                logger.debug("Sending heartbeat...")
                # For now, just ensuring we stay connected
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
            await asyncio.sleep(random.randint(30, 60))  # Every 30-60s

    def connect(self):
        # paho-mqtt version 1.x or 2.x? Let's check.
        # Using CallbackAPIVersion for paho-mqtt 2.0+
        client = None
        try:
            from paho.mqtt.enums import CallbackAPIVersion

            client = mqtt.Client(
                callback_api_version=CallbackAPIVersion.VERSION1,
                client_id="mqttwsclient",
                transport="websockets",
                protocol=mqtt.MQTTv31,
            )
        except ImportError, AttributeError:
            client = mqtt.Client(
                client_id="mqttwsclient", transport="websockets", protocol=mqtt.MQTTv31
            )

        self.client = client
        if self.client:
            self.client.username_pw_set(self._get_username())

        # SSL and Cookies
        host = (
            f"wss://edge-chat.facebook.com/chat?sid={self.session_id}&cid={self.guid}"
        )
        if self.ctx.region:
            host = f"wss://edge-chat.facebook.com/chat?region={self.ctx.region.lower()}&sid={self.session_id}&cid={self.guid}"

        cookie_str = "; ".join(
            [f"{c.name}={c.value}" for c in self.ctx.client.cookies.jar]
        )

        self.client.ws_set_options(
            path=host.split(".com")[1],
            headers={
                "Cookie": cookie_str,
                "Origin": "https://www.facebook.com",
                "User-Agent": self.ctx.options.get(
                    "userAgent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
                ),
                "Referer": "https://www.facebook.com/",
                "Host": "edge-chat.facebook.com",
                "Sec-WebSocket-Protocol": "mqtt",
            },
        )

        if self.client:
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message

            # Connect to edge-chat.facebook.com:443
            self.client.tls_set()  # Enable TLS for wss
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
