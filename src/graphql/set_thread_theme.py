import json
from typing import Any
from ..utils.utils import generate_offline_threading_id


async def set_thread_theme(ctx: Any, thread_id: str, theme_fbid: str):
    if not hasattr(ctx, "mqtt_client") or not ctx.mqtt_client:
        raise Exception("Not connected to MQTT")

    ctx.ws_req_number = getattr(ctx, "ws_req_number", 0) + 1
    ctx.ws_task_number = getattr(ctx, "ws_task_number", 0) + 1
    base_task_number = ctx.ws_task_number

    def make_task(label, queue_name, extra_payload=None):
        nonlocal base_task_number
        payload = {
            "thread_key": str(thread_id),
            "theme_fbid": str(theme_fbid),
            "sync_group": 1,
        }
        if extra_payload:
            payload.update(extra_payload)

        task = {
            "failure_count": None,
            "label": str(label),
            "payload": json.dumps(payload),
            "queue_name": (
                queue_name if isinstance(queue_name, str) else json.dumps(queue_name)
            ),
            "task_id": base_task_number,
        }
        base_task_number += 1
        return task

    tasks_configs = [
        {"label": 1013, "queue": ["ai_generated_theme", str(thread_id)]},
        {"label": 1037, "queue": ["msgr_custom_thread_theme", str(thread_id)]},
        {"label": 1028, "queue": ["thread_theme_writer", str(thread_id)]},
        {
            "label": 43,
            "queue": "thread_theme",
            "extra": {"source": None, "payload": None},
        },
    ]

    for config in tasks_configs:
        ctx.ws_req_number += 1
        msg = {
            "app_id": "772021112871879",
            "payload": json.dumps(
                {
                    "epoch_id": int(generate_offline_threading_id()),
                    "tasks": [
                        make_task(config["label"], config["queue"], config.get("extra"))
                    ],
                    "version_id": "24227364673632991",
                }
            ),
            "request_id": ctx.ws_req_number,
            "type": 3,
        }
        ctx.mqtt_client.publish("/ls_req", json.dumps(msg), qos=1, retain=False)

    ctx.ws_task_number = base_task_number
    return True
