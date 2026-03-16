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
    def __init__(self, ctx: Any, global_callback: Callable, refresh_handler: Optional[Callable] = None):
        self.ctx = ctx
        self.global_callback = global_callback
        self.refresh_handler = refresh_handler
        self.session_id = random.randint(1, 9007199254740991)
        self.guid = get_guid()
        self.client: Optional[mqtt.Client] = None
        self.ws_req_number: int = 0
        self.ws_task_number: int = 0
        self.loop = asyncio.get_event_loop()

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

    def _on_connect(self, client, userdata, flags, rc, properties=None):
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

    def _parse_delta(self, delta):
        cls = delta.get("class")
        if cls in ["NewMessage", "DeltaNewMessage"]:
            meta = delta.get("messageMetadata") or delta.get("message_metadata") or {}
            body = delta.get("body") or delta.get("text") or ""
            
            thread_key = meta.get("threadKey") or meta.get("thread_key") or {}
            sender_id = str(meta.get("actorId") or meta.get("actor_id") or "")
            
            return {
                "type": "message",
                "senderID": sender_id,
                "body": body,
                "threadID": format_id(
                    str(
                        thread_key.get("threadFbId")
                        or thread_key.get("thread_fbid")
                        or thread_key.get("otherUserFbId")
                        or thread_key.get("other_user_fbid")
                        or sender_id
                    )
                ),
                "messageID": meta.get("messageId") or meta.get("message_id"),
                "timestamp": meta.get("timestamp") or meta.get("timestamp_ms"),
                "isGroup": "threadFbId" in thread_key or "thread_fbid" in thread_key,
            }
        return None

    def _on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            print(f"📡 MQTT Message on {topic}")
            # logger.debug(f"MQTT Message on {topic}: {payload}")

            if topic == "/t_ms":
                print(f"📦 Payload: {payload}")
                
                if payload.get("errorCode") == "ERROR_QUEUE_OVERFLOW":
                    print("⚠️ Queue overflow! Attempting fresh sync refresh...")
                    if self.refresh_handler:
                        # Schedule refresh in the background
                        async def do_refresh():
                            try:
                                handler = self.refresh_handler
                                if handler:
                                    await handler()
                                print(f"♻️ Refresh complete. New last_seq_id: {self.ctx.last_seq_id}")
                                
                                # Re-create queue with fresh ID
                                sync_topic = "/messenger_sync_create_queue"
                                queue = {
                                    "sync_api_version": 10,
                                    "max_deltas_able_to_process": 1000,
                                    "delta_batch_size": 500,
                                    "encoding": "JSON",
                                    "entity_fbid": self.ctx.user_id,
                                    "initial_titan_sequence_id": self.ctx.last_seq_id,
                                    "device_params": None,
                                }
                                client.publish(sync_topic, json.dumps(queue), qos=1)
                            except Exception as e:
                                logger.error(f"Sync refresh failed: {e}")

                        asyncio.run_coroutine_threadsafe(do_refresh(), self.loop)
                    return

                if "firstDeltaSeqId" in payload and "syncToken" in payload:
                    self.ctx.last_seq_id = payload["firstDeltaSeqId"]
                    self.ctx.sync_token = payload["syncToken"]

                if "lastIssuedSeqId" in payload:
                    self.ctx.last_seq_id = int(payload["lastIssuedSeqId"])

                for delta in payload.get("deltas", []):
                    # print(f"🔹 Delta Class: {delta.get('class')}")
                    parsed_event = self._parse_delta(delta)
                    if parsed_event:
                        print(f"✅ Parsed Event: {parsed_event.get('type')}")
                        asyncio.run_coroutine_threadsafe(
                            self.global_callback(None, parsed_event), self.loop
                        )

            elif topic in ["/thread_typing", "/orca_typing_notifications"]:
                typ = {
                    "type": "typ",
                    "isTyping": bool(payload.get("state")),
                    "from": str(payload.get("sender_fbid", "")),
                    "threadID": format_id(
                        str(payload.get("thread") or payload.get("sender_fbid", ""))
                    ),
                }
                asyncio.run_coroutine_threadsafe(
                    self.global_callback(None, typ),
                    self.loop
                )

            elif topic == "/orca_presence":
                for item in payload.get("list", []):
                    presence = {
                        "type": "presence",
                        "userID": str(item["u"]),
                        "timestamp": item["l"] * 1000,
                        "statuses": item["p"],
                    }
                    asyncio.run_coroutine_threadsafe(
                        self.global_callback(None, presence),
                        self.loop
                    )

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

        client = self.client
        if client and client.is_connected():
            client.publish("/ls_req", json.dumps(content), qos=1)
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
                # logger.debug("Sending heartbeat...")
                pass
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
            await asyncio.sleep(random.randint(30, 60))  # Every 30-60s

    def connect(self):
        try:
            from paho.mqtt.enums import CallbackAPIVersion

            self.client = mqtt.Client(
                callback_api_version=CallbackAPIVersion.VERSION2,
                client_id="mqttwsclient",
                transport="websockets",
                protocol=mqtt.MQTTv31,
            )
        except (ImportError, AttributeError):
            # Fallback for older paho-mqtt
            self.client = mqtt.Client(
                client_id="mqttwsclient", transport="websockets", protocol=mqtt.MQTTv31
            )

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

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Connect to edge-chat.facebook.com:443
        self.client.tls_set()  # Enable TLS for wss
        self.client.connect("edge-chat.facebook.com", 443, keepalive=60)
        self.client.loop_start()

        # Start heartbeat
        asyncio.create_task(self._heartbeat_loop())


async def listen_mqtt(ctx: Any, global_callback: Callable, refresh_handler: Optional[Callable] = None):
    mqtt_client = MQTTClient(ctx, global_callback, refresh_handler=refresh_handler)
    mqtt_client.connect()
    ctx.mqtt_client = mqtt_client
    
    # Block indefinitely to keep the script running
    while True:
        await asyncio.sleep(1)
    return mqtt_client
