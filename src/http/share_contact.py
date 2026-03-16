import json
import random
from typing import Any
from ..utils.utils import generate_offline_threading_id


async def share_contact(ctx: Any, text: str, sender_id: str, thread_id: str):
    if not hasattr(ctx, "mqtt_client") or not ctx.mqtt_client:
        raise Exception("Not connected to MQTT")

    ctx.ws_req_number = getattr(ctx, "ws_req_number", 0) + 1

    query_payload = {
        "contact_id": str(sender_id),
        "sync_group": 1,
        "text": text or "",
        "thread_id": str(thread_id),
    }

    query = {
        "failure_count": None,
        "label": "359",
        "payload": json.dumps(query_payload),
        "queue_name": "messenger_contact_sharing",
        "task_id": random.randint(0, 1000),
    }

    msg = {
        "app_id": "2220391788200892",
        "payload": json.dumps(
            {
                "tasks": [query],
                "epoch_id": int(generate_offline_threading_id()),
                "version_id": "7214102258676893",
            }
        ),
        "request_id": ctx.ws_req_number,
        "type": 3,
    }

    ctx.mqtt_client.publish("/ls_req", json.dumps(msg), qos=1, retain=False)
    return True
