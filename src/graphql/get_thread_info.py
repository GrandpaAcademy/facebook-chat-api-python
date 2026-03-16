import json
from typing import Any, Optional, Dict
from ..utils.utils import parse_and_check_login

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

async def get_thread_info(post_func, ctx: Any, thread_id: str):
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
    res = await post_func("https://www.facebook.com/api/graphqlbatch/", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        raise Exception("Failed to parse getThreadInfo response")
    if isinstance(res_data, list) and len(res_data) > 0:
        actual_data = res_data[0].get("o0", {}).get("data")
        return format_thread_graphql_response(actual_data)
    return None
