import json
import random
from typing import Any
from ..utils.utils import generate_offline_threading_id

async def share_link(ctx: Any, text: str, url: str, thread_id: str):
    if not hasattr(ctx, "mqtt_client") or not ctx.mqtt_client:
        raise Exception("Not connected to MQTT")

    ctx.ws_req_number = getattr(ctx, "ws_req_number", 0) + 1
    
    payload = {
        "otid": generate_offline_threading_id(),
        "source": 524289,
        "sync_group": 1,
        "send_type": 6,
        "mark_thread_read": 0,
        "url": url or "https://www.facebook.com/",
        "text": text or "",
        "thread_id": str(thread_id),
        "initiating_source": 0
    }
    
    task = {
        "label": 46,
        "payload": json.dumps(payload),
        "queue_name": str(thread_id),
        "task_id": random.randint(0, 1000),
        "failure_count": None,
    }
    
    msg = {
        "app_id": "2220391788200892",
        "payload": json.dumps({
            "tasks": [task],
            "epoch_id": int(generate_offline_threading_id()),
            "version_id": '7191105584331330',
        }),
        "request_id": ctx.ws_req_number,
        "type": 3
    }
    
    ctx.mqtt_client.publish('/ls_req', json.dumps(msg), qos=1, retain=False)
    return True
