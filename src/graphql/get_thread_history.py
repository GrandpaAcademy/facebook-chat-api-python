import json
from typing import Any, Optional, List, Dict
from ..utils.utils import parse_and_check_login
from .formatter import (
    format_attachments_graphql_response,
    format_extensible_attachment,
    format_event_data
)

def format_reactions_graphql(reaction: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "reaction": reaction.get("reaction"),
        "userID": reaction.get("user", {}).get("id")
    }

def format_messages_graphql_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    message_thread = data.get("message_thread")
    if not message_thread: return []
    thread_id = message_thread["thread_key"].get("thread_fbid") or message_thread["thread_key"].get("other_user_id")
    
    messages = []
    for d in message_thread.get("messages", {}).get("nodes", []):
        typename = d.get("__typename")
        if typename == "UserMessage":
            sticker_attachment = []
            if d.get("sticker"):
                s = d["sticker"]
                sticker_attachment = [{
                    "type": "sticker",
                    "ID": s.get("id"),
                    "url": s.get("url"),
                    "packID": s.get("pack", {}).get("id"),
                    "spriteUrl": s.get("sprite_image"),
                    "spriteUrl2x": s.get("sprite_image_2x"),
                    "width": s.get("width"),
                    "height": s.get("height"),
                    "caption": d.get("snippet"),
                    "description": s.get("label"),
                    "frameCount": s.get("frame_count"),
                    "frameRate": s.get("frame_rate"),
                    "framesPerRow": s.get("frames_per_row"),
                    "framesPerCol": s.get("frames_per_col"),
                    "stickerID": s.get("id"),
                    "spriteURI": s.get("sprite_image"),
                    "spriteURI2x": s.get("sprite_image_2x")
                }]
            
            mentions = {}
            if d.get("message"):
                text = d["message"].get("text", "")
                for r in d["message"].get("ranges", []):
                    offset = r.get("offset")
                    length = r.get("length")
                    mentions[r["entity"]["id"]] = text[offset:offset+length]

            messages.append({
                "type": "message",
                "attachments": sticker_attachment if sticker_attachment else (
                    [format_attachments_graphql_response(a) for a in d.get("blob_attachments", [])] +
                    ([format_extensible_attachment(d["extensible_attachment"])] if d.get("extensible_attachment") else [])
                ),
                "body": d.get("message", {}).get("text") if d.get("message") else "",
                "isGroup": message_thread.get("thread_type") == "GROUP",
                "messageID": d.get("message_id"),
                "senderID": d.get("message_sender", {}).get("id"),
                "threadID": thread_id,
                "timestamp": d.get("timestamp_precise"),
                "mentions": mentions,
                "isUnread": d.get("unread"),
                "messageReactions": [format_reactions_graphql(r) for r in d.get("message_reactions", [])] if d.get("message_reactions") else None,
                "isSponsored": d.get("is_sponsored"),
                "snippet": d.get("snippet")
            })
        elif typename in ["ThreadNameMessage", "ThreadImageMessage", "ParticipantLeftMessage", "ParticipantsAddedMessage", "VideoCallMessage", "VoiceCallMessage", "GenericAdminTextMessage"]:
            event_type_map = {
                "ThreadNameMessage": "change_thread_name",
                "ThreadImageMessage": "change_thread_image",
                "ParticipantLeftMessage": "remove_participants",
                "ParticipantsAddedMessage": "add_participants",
                "VideoCallMessage": "video_call",
                "VoiceCallMessage": "voice_call"
            }
            event_type = event_type_map.get(typename) or d.get("extensible_message_admin_text_type", "").lower()
            
            event_data = {}
            if typename == "ThreadNameMessage":
                event_data = {"threadName": d.get("thread_name")}
            elif typename == "ThreadImageMessage":
                img = d.get("image_with_metadata")
                if img:
                    event_data = {"threadImage": {
                        "attachmentID": img.get("legacy_attachment_id"),
                        "width": img.get("original_dimensions", {}).get("x"),
                        "height": img.get("original_dimensions", {}).get("y"),
                        "url": img.get("preview", {}).get("uri")
                    }}
            elif typename == "ParticipantLeftMessage":
                event_data = {"participantsRemoved": [p["id"] for p in d.get("participants_removed", [])]}
            elif typename == "ParticipantsAddedMessage":
                event_data = {"participantsAdded": [p["id"] for p in d.get("participants_added", [])]}
            elif typename == "GenericAdminTextMessage":
                event_data = format_event_data(d.get("extensible_message_admin_text"))

            messages.append({
                "type": "event",
                "messageID": d.get("message_id"),
                "threadID": thread_id,
                "isGroup": message_thread.get("thread_type") == "GROUP",
                "senderID": d.get("message_sender", {}).get("id"),
                "timestamp": d.get("timestamp_precise"),
                "eventType": event_type,
                "snippet": d.get("snippet"),
                "eventData": event_data
            })
    return messages

async def get_thread_history(post_func, ctx: Any, thread_id: str, amount: int, timestamp: Optional[int] = None):
    form = {
        "av": ctx.user_id,
        "queries": json.dumps({
            "o0": {
                "doc_id": "1498317363570230",
                "query_params": {
                    "id": thread_id,
                    "message_limit": amount,
                    "load_messages": 1,
                    "load_read_receipts": False,
                    "before": timestamp
                }
            }
        })
    }
    res = await post_func("https://www.facebook.com/api/graphqlbatch/", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data or not isinstance(res_data, list):
        raise Exception("Failed to parse getThreadHistory response")
    
    if res_data[-1].get("error_results", 0) != 0:
        raise Exception("There was an error_result in getThreadHistory.")
        
    return format_messages_graphql_response(res_data[0].get("o0", {}).get("data", {}))
