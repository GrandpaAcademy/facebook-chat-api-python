import time
import httpx
import json
import re
from typing import Any, Optional, Dict, List

from ..utils.utils import (
    generate_offline_threading_id, 
    generate_threading_id, 
    get_headers, 
    parse_and_check_login, 
    get_from,
    get_signature_id
)

from .mqtt import listen_mqtt 

def build_form_defaults(ctx: Any, form: Dict[str, Any]) -> Dict[str, Any]:
    jazoest = "2"
    if ctx.fb_dtsg:
        for c in ctx.fb_dtsg:
            jazoest += str(ord(c))
            
    defaults = {
        "__user": ctx.user_id,
        "__req": ctx.req_counter,
        "__rev": ctx.revision,
        "__a": "1",
        "fb_dtsg": ctx.fb_dtsg,
        "jazoest": jazoest
    }
    
    for k, v in defaults.items():
        if k not in form:
            form[k] = v
    return form

async def post(url: str, ctx: Any, form: Dict[str, Any]) -> httpx.Response:
    headers = get_headers(url, ctx.options, ctx)
    form = build_form_defaults(ctx, form)
    
    def to_base36(n):
        chars = '0123456789abcdefghijklmnopqrstuvwxyz'
        if n == 0: return '0'
        res = ''
        while n:
            res = chars[n % 36] + res
            n //= 36
        return res

    form["__req"] = to_base36(ctx.req_counter)
    ctx.req_counter += 1
    
    # Use the persistent client from context
    res = await ctx.client.post(url, data=form, headers=headers)
    print(f"DEBUG: Request to {url} headers: {res.request.headers}")
    print(f"DEBUG: Request body (first 100 chars): {str(res.request.read())[:100]}")
    return res

async def send_message(ctx: Any, msg: Any, thread_id: str, is_single_user: Optional[bool] = None, reply_to_message: Optional[str] = None):
    if isinstance(msg, str):
        msg = {"body": msg}
    message_and_otid = generate_offline_threading_id()
    form = {
        "client": "mercury",
        "action_type": "ma-type:user-generated-message",
        "author": f"fbid:{ctx.user_id}",
        "timestamp": int(time.time() * 1000),
        "timestamp_absolute": "Today",
        "timestamp_relative": "Now",
        "timestamp_time_passed": "0",
        "is_unread": "false",
        "is_cleared": "false",
        "is_forward": "false",
        "is_filtered_content": "false",
        "source": "source:chat:web",
        "body": msg.get("body", ""),
        "offline_threading_id": message_and_otid,
        "message_id": message_and_otid,
        "threading_id": generate_threading_id(ctx.client_id),
    }
    if reply_to_message:
        form["replied_to_message_id"] = reply_to_message
    if is_single_user:
        form["specific_to_list[0]"] = f"fbid:{thread_id}"
        form["specific_to_list[1]"] = f"fbid:{ctx.user_id}"
        form["other_user_fbid"] = thread_id
    else:
        form["thread_fbid"] = thread_id
    res = await post("https://www.facebook.com/messaging/send/", ctx, form)
    return res.json()

async def get_user_info(ctx: Any, ids: List[str]):
    form = {}
    for i, user_id in enumerate(ids):
        form[f"ids[{i}]"] = user_id
    res = await post("https://www.facebook.com/chat/user_info/", ctx, form)
    body = res.text
    body = re.sub(r'for\s*\(\s*;\s*;\s*\)\s*;\s*', '', body)
    if not body:
        raise Exception("Facebook returned an empty response body.")
    res_data = json.loads(body)
    if isinstance(res_data, list):
        res_data = res_data[0]
    if res_data.get("error"):
        raise Exception(res_data)
    profiles = {}
    if "payload" in res_data and "profiles" in res_data["payload"]:
        data = res_data["payload"]["profiles"]
        for user_id, user_data in data.items():
            profiles[user_id] = {
                "name": user_data.get("name", "Unknown"),
                "firstName": user_data.get("firstName", "Unknown"),
                "vanity": user_data.get("vanity", ""),
                "thumbSrc": user_data.get("thumbSrc", ""),
                "profileUrl": user_data.get("uri", f"https://www.facebook.com/{user_id}"),
                "gender": user_data.get("gender", ""),
                "type": user_data.get("type", "user"),
                "isFriend": user_data.get("is_friend", False),
                "isBirthday": user_data.get("is_birthday", False)
            }
    return profiles

def format_thread_graphql_response(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not data or "message_thread" not in data:
        return None
    t = data["message_thread"]
    thread_id = t["thread_key"]["thread_fbid"] or t["thread_key"]["other_user_id"]
    return {
        "threadID": thread_id,
        "name": t.get("name"),
        "participantIDs": [e["node"]["messaging_actor"]["id"] for e in t["all_participants"]["edges"]],
        "unreadCount": t.get("unread_count"),
        "messageCount": t.get("messages_count"),
        "timestamp": t.get("updated_time_precise"),
        "isGroup": t.get("thread_type") == "GROUP",
        "emoji": t.get("customization_info", {}).get("emoji") if t.get("customization_info") else None,
        "color": t.get("customization_info", {}).get("outgoing_bubble_color", "")[2:] if t.get("customization_info") and t["customization_info"].get("outgoing_bubble_color") else None,
        "nicknames": {v["participant_id"]: v["nickname"] for v in t.get("customization_info", {}).get("participant_customizations", []) if v.get("nickname")} if t.get("customization_info") else {},
        "adminIDs": [a["id"] for a in t.get("thread_admins", [])],
    }

async def get_thread_info(ctx: Any, thread_id: str):
    form = {
        "queries": json.dumps({
            "o0": {
                "doc_id": "3449967031715030",
                "query_params": {
                    "id": thread_id,
                    "message_limit": 0,
                    "load_messages": False,
                    "load_read_receipts": False,
                    "before": None
                }
            }
        }),
        "batch_name": "MessengerGraphQLThreadFetcher"
    }
    res = await post("https://www.facebook.com/api/graphqlbatch/", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        raise Exception("Failed to parse getThreadInfo response")
    if isinstance(res_data, list) and len(res_data) > 0:
        actual_data = res_data[0].get("o0", {}).get("data")
        return format_thread_graphql_response(actual_data)
    return None

async def get_thread_list(ctx: Any, limit: int, timestamp: Optional[int] = None, tags: List[str] = [""]):
    form = {
        "queries": json.dumps({
            "o0": {
                "doc_id": "3336396659757871",
                "query_params": {
                    "limit": limit + (1 if timestamp else 0),
                    "before": timestamp,
                    "tags": tags,
                    "includeDeliveryReceipts": True,
                    "includeSeqID": False
                }
            }
        }),
        "batch_name": "MessengerGraphQLThreadlistFetcher"
    }
    res = await post("https://www.facebook.com/api/graphqlbatch/", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        raise Exception("Failed to parse getThreadList response")
    threads = []
    if isinstance(res_data, list) and len(res_data) > 0:
        nodes = res_data[0].get("o0", {}).get("data", {}).get("viewer", {}).get("message_threads", {}).get("nodes", [])
        if timestamp and nodes:
            nodes.pop(0)
        for node in nodes:
            threads.append(format_thread_graphql_response({"message_thread": node}))
    return threads

async def mark_as_read(ctx: Any, thread_id: str, read: bool = True):
    form = {
        "ids[" + thread_id + "]": "true" if read else "false",
        "watermarkTimestamp": int(time.time() * 1000),
        "shouldSendReadReceipt": "true",
        "commerce_last_message_type": ""
    }
    res = await post("https://www.facebook.com/ajax/mercury/change_read_status.php", ctx, form)
    return parse_and_check_login(ctx, res)

async def set_title(ctx: Any, new_title: str, thread_id: str):
    message_and_otid = generate_offline_threading_id()
    form = {
        "client": "mercury",
        "action_type": "ma-type:log-message",
        "author": f"fbid:{ctx.user_id}",
        "timestamp": int(time.time() * 1000),
        "timestamp_absolute": "Today",
        "timestamp_relative": "Now",
        "timestamp_time_passed": "0",
        "is_unread": "false",
        "is_cleared": "false",
        "is_forward": "false",
        "is_filtered_content": "false",
        "source": "source:chat:web",
        "offline_threading_id": message_and_otid,
        "message_id": message_and_otid,
        "threading_id": generate_threading_id(ctx.client_id),
        "thread_fbid": thread_id,
        "thread_name": new_title,
        "thread_id": thread_id,
        "log_message_type": "log:thread-name",
    }
    res = await post("https://www.facebook.com/messaging/set_thread_name/", ctx, form)
    return parse_and_check_login(ctx, res)

async def logout(ctx: Any):
    menu_url = "https://www.facebook.com/bluebar/modern_settings_menu/?help_type=364455653583099&show_contextual_help=1"
    res = await post(menu_url, ctx, {"pmid": "0"})
    res_data = parse_and_check_login(ctx, res)
    if not res_data or "jsmods" not in res_data:
        raise Exception("Failed to get logout menu data")
    markup = json.dumps(res_data["jsmods"].get("markup", []))
    fb_dtsg = get_from(markup, 'fb_dtsg\\\\" value=\\\\"', '\\\\"')
    h = get_from(markup, 'h\\\\" value=\\\\"', '\\\\"')
    ref = get_from(markup, 'ref\\\\" value=\\\\"', '\\\\"')
    logout_form = {"fb_dtsg": fb_dtsg, "h": h, "ref": ref}
    await post("https://www.facebook.com/logout.php", ctx, logout_form)
    ctx.logged_in = False
    return True

async def set_active_status(ctx: Any, is_active: bool):
    form = {}
    sig = get_signature_id()
    form.update({
        "__aaid": "0",
        "__req": sig,
        "__hs": "20351.HYP:comet_pkg.2.1...0",
        "dpr": "1",
        "__ccg": "EXCELLENT",
        "__rev": ctx.revision,
        "__s": sig,
        "__hsi": "7552256848274926554",
        "__comet_req": "15",
        "lsd": ctx.fb_dtsg,
        "__spin_r": ctx.revision,
        "__spin_b": "trunk",
        "__spin_t": str(int(time.time())),
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "UpdatePresenceSettingsMutation",
        "variables": json.dumps({
            "input": {
                "online_policy": "ALLOWLIST",
                "web_allowlist": [],
                "web_visibility": is_active,
                "actor_id": str(ctx.user_id),
                "client_mutation_id": "1"
            }
        }),
        "server_timestamps": "true",
        "doc_id": "9444355898946246"
    })
    
    res = await post("https://www.facebook.com/api/graphql/", ctx, form)
    return parse_and_check_login(ctx, res)

def get_api(ctx: Any):
    return {
        "sendMessage": lambda msg, thread_id, is_single_user=None, reply_to_message=None: send_message(ctx, msg, thread_id, is_single_user, reply_to_message),
        "getUserInfo": lambda ids: get_user_info(ctx, ids),
        "getThreadInfo": lambda thread_id: get_thread_info(ctx, thread_id),
        "getThreadList": lambda limit, timestamp=None, tags=[""]: get_thread_list(ctx, limit, timestamp, tags),
        "markAsRead": lambda thread_id, read=True: mark_as_read(ctx, thread_id, read),
        "setTitle": lambda new_title, thread_id: set_title(ctx, new_title, thread_id),
        "logout": lambda: logout(ctx),
        "setActiveStatus": lambda is_active: set_active_status(ctx, is_active),
        "listenMqtt": lambda callback: listen_mqtt(ctx, callback),
        "getCurrentUserID": lambda: ctx.user_id,
    }
