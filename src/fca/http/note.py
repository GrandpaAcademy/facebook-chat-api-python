import json
import random
import time
from typing import Any, Optional, Dict
from ..utils.utils import parse_and_check_login, get_guid


async def check_note(post_func, ctx: Any):
    form = {
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "MWInboxTrayNoteCreationDialogQuery",
        "variables": json.dumps({"scale": 2}),
        "doc_id": "30899655739648624",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"checkNote errors: {res_data['errors']}")

    current_note = (
        res_data.get("data", {})
        .get("viewer", {})
        .get("actor", {})
        .get("msgr_user_rich_status")
    )

    return {
        "note": current_note,
        "hasActiveNote": bool(current_note),
        "userId": ctx.user_id,
        "timestamp": int(time.time() * 1000),
        "expiresAt": (
            (current_note["created_time"] * 1000) + (24 * 60 * 60 * 1000)
            if current_note
            else None
        ),
    }


async def create_note(
    post_func, ctx: Any, text: str, options: Optional[Dict[str, Any]] = None
):
    if not options:
        options = {}

    privacy = options.get("privacy", "FRIENDS")
    duration = options.get("duration", 86400)
    note_type = options.get("noteType", "TEXT_NOTE")

    variables = {
        "input": {
            "client_mutation_id": str(random.randint(0, 1000000)),
            "actor_id": ctx.user_id,
            "description": text.strip(),
            "duration": duration,
            "note_type": note_type,
            "privacy": privacy,
            "session_id": get_guid(),
        },
    }

    form = {
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "MWInboxTrayNoteCreationDialogCreationStepContentMutation",
        "variables": json.dumps(variables),
        "doc_id": "24060573783603122",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"createNote errors: {res_data['errors']}")

    status = res_data.get("data", {}).get("xfb_rich_status_create", {}).get("status")
    if not status:
        raise Exception("Could not find note status in the server response.")

    return {
        **status,
        "createdAt": int(time.time() * 1000),
        "expiresAt": int(time.time() * 1000) + (duration * 1000),
        "characterCount": len(text.strip()),
        "privacy": privacy,
    }


async def delete_note(post_func, ctx: Any, note_id: str):
    variables = {
        "input": {
            "client_mutation_id": str(random.randint(0, 1000000)),
            "actor_id": ctx.user_id,
            "rich_status_id": note_id,
        },
    }

    form = {
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "useMWInboxTrayDeleteNoteMutation",
        "variables": json.dumps(variables),
        "doc_id": "9532619970198958",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"deleteNote errors: {res_data['errors']}")

    deleted_status = res_data.get("data", {}).get("xfb_rich_status_delete")
    if not deleted_status:
        raise Exception("Could not find deletion status in the server response.")

    return {**deleted_status, "deletedAt": int(time.time() * 1000), "noteId": note_id}
