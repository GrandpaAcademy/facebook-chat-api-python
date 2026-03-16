from typing import Any, Dict, Optional, List

def get_extension(original_extension: str, filename: str = "") -> str:
    if original_extension:
        return original_extension
    else:
        parts = filename.split(".")
        if len(parts) > 1:
            return parts[-1]
        return ""

def format_attachments_graphql_response(attachment: Dict[str, Any]) -> Dict[str, Any]:
    typename = attachment.get("__typename")
    if typename == "MessageImage":
        return {
            "type": "photo",
            "ID": attachment.get("legacy_attachment_id"),
            "filename": attachment.get("filename"),
            "original_extension": get_extension(attachment.get("original_extension", ""), attachment.get("filename", "")),
            "thumbnailUrl": attachment.get("thumbnail", {}).get("uri"),
            "previewUrl": attachment.get("preview", {}).get("uri"),
            "previewWidth": attachment.get("preview", {}).get("width"),
            "previewHeight": attachment.get("preview", {}).get("height"),
            "largePreviewUrl": attachment.get("large_preview", {}).get("uri"),
            "largePreviewHeight": attachment.get("large_preview", {}).get("height"),
            "largePreviewWidth": attachment.get("large_preview", {}).get("width"),
            "url": attachment.get("large_preview", {}).get("uri"),
            "width": attachment.get("large_preview", {}).get("width"),
            "height": attachment.get("large_preview", {}).get("height"),
            "name": attachment.get("filename"),
            "attributionApp": {
                "attributionAppID": attachment["attribution_app"]["id"],
                "name": attachment["attribution_app"]["name"],
                "logo": attachment["attribution_app"]["square_logo"]
            } if attachment.get("attribution_app") else None
        }
    elif typename == "MessageAnimatedImage":
        return {
            "type": "animated_image",
            "ID": attachment.get("legacy_attachment_id"),
            "filename": attachment.get("filename"),
            "original_extension": get_extension(attachment.get("original_extension", ""), attachment.get("filename", "")),
            "previewUrl": attachment.get("preview_image", {}).get("uri"),
            "previewWidth": attachment.get("preview_image", {}).get("width"),
            "previewHeight": attachment.get("preview_image", {}).get("height"),
            "url": attachment.get("animated_image", {}).get("uri"),
            "width": attachment.get("animated_image", {}).get("width"),
            "height": attachment.get("animated_image", {}).get("height"),
            "thumbnailUrl": attachment.get("preview_image", {}).get("uri"),
            "name": attachment.get("filename"),
            "attributionApp": {
                "attributionAppID": attachment["attribution_app"]["id"],
                "name": attachment["attribution_app"]["name"],
                "logo": attachment["attribution_app"]["square_logo"]
            } if attachment.get("attribution_app") else None
        }
    elif typename == "MessageVideo":
        return {
            "type": "video",
            "ID": attachment.get("legacy_attachment_id"),
            "filename": attachment.get("filename"),
            "original_extension": get_extension(attachment.get("original_extension", ""), attachment.get("filename", "")),
            "duration": attachment.get("playable_duration_in_ms"),
            "thumbnailUrl": attachment.get("large_image", {}).get("uri"),
            "previewUrl": attachment.get("large_image", {}).get("uri"),
            "previewWidth": attachment.get("large_image", {}).get("width"),
            "previewHeight": attachment.get("large_image", {}).get("height"),
            "url": attachment.get("playable_url"),
            "width": attachment.get("original_dimensions", {}).get("x"),
            "height": attachment.get("original_dimensions", {}).get("y"),
            "videoType": attachment.get("video_type", "").lower()
        }
    elif typename == "MessageFile":
        return {
            "type": "file",
            "ID": attachment.get("message_file_fbid"),
            "filename": attachment.get("filename"),
            "original_extension": get_extension(attachment.get("original_extension", ""), attachment.get("filename", "")),
            "url": attachment.get("url"),
            "isMalicious": attachment.get("is_malicious"),
            "contentType": attachment.get("content_type"),
            "name": attachment.get("filename")
        }
    elif typename == "MessageAudio":
        return {
            "type": "audio",
            "ID": attachment.get("url_shimhash"),
            "filename": attachment.get("filename"),
            "original_extension": get_extension(attachment.get("original_extension", ""), attachment.get("filename", "")),
            "duration": attachment.get("playable_duration_in_ms"),
            "audioType": attachment.get("audio_type"),
            "url": attachment.get("playable_url"),
            "isVoiceMail": attachment.get("is_voicemail")
        }
    return {"error": f"Don't know about attachment type {typename}"}

def format_extensible_attachment(attachment: Dict[str, Any]) -> Dict[str, Any]:
    story = attachment.get("story_attachment")
    if story:
        media = story.get("media")
        return {
            "type": "share",
            "ID": attachment.get("legacy_attachment_id"),
            "url": story.get("url"),
            "title": story.get("title_with_entities", {}).get("text"),
            "description": story.get("description", {}).get("text") if story.get("description") else None,
            "source": story.get("source", {}).get("text") if story.get("source") else None,
            "image": (media.get("animated_image") or media.get("image", {})).get("uri") if media and (media.get("animated_image") or media.get("image")) else None,
            "width": (media.get("animated_image") or media.get("image", {})).get("width") if media and (media.get("animated_image") or media.get("image")) else None,
            "height": (media.get("animated_image") or media.get("image", {})).get("height") if media and (media.get("animated_image") or media.get("image")) else None,
            "playable": media.get("is_playable") if media else None,
            "duration": media.get("playable_duration_in_ms") if media else None,
            "playableUrl": media.get("playable_url") if media else None,
            "subattachments": story.get("subattachments"),
            "properties": {p["key"]: p["value"].get("text") for p in story.get("properties", [])}
        }
    return {"error": "Don't know what to do with extensible_attachment."}

def format_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
    if not event: return {}
    typename = event.get("__typename")
    if typename == "ThemeColorExtensibleMessageAdminText":
        return {"color": event.get("theme_color")}
    elif typename == "ThreadNicknameExtensibleMessageAdminText":
        return {"nickname": event.get("nickname"), "participantID": event.get("participant_id")}
    elif typename == "ThreadIconExtensibleMessageAdminText":
        return {"threadIcon": event.get("thread_icon")}
    elif typename == "InstantGameUpdateExtensibleMessageAdminText":
        return {
            "gameID": event["game"]["id"] if event.get("game") else None,
            "update_type": event.get("update_type"),
            "collapsed_text": event.get("collapsed_text"),
            "expanded_text": event.get("expanded_text"),
            "instant_game_update_data": event.get("instant_game_update_data")
        }
    elif typename == "GameScoreExtensibleMessageAdminText":
        return {"game_type": event.get("game_type")}
    elif typename == "RtcCallLogExtensibleMessageAdminText":
        return {
            "event": event.get("event"),
            "is_video_call": event.get("is_video_call"),
            "server_info_data": event.get("server_info_data")
        }
    elif typename == "GroupPollExtensibleMessageAdminText":
        return {
            "event_type": event.get("event_type"),
            "total_count": event.get("total_count"),
            "question": event.get("question")
        }
    elif typename == "AcceptPendingThreadExtensibleMessageAdminText":
        return {"accepter_id": event.get("accepter_id"), "requester_id": event.get("requester_id")}
    elif typename == "ConfirmFriendRequestExtensibleMessageAdminText":
        return {"friend_request_recipient": event.get("friend_request_recipient"), "friend_request_sender": event.get("friend_request_sender")}
    elif typename == "AddContactExtensibleMessageAdminText":
        return {"contact_added_id": event.get("contact_added_id"), "contact_adder_id": event.get("contact_adder_id")}
    elif typename == "AdExtensibleMessageAdminText":
        return {
            "ad_client_token": event.get("ad_client_token"),
            "ad_id": event.get("ad_id"),
            "ad_preferences_link": event.get("ad_preferences_link"),
            "ad_properties": event.get("ad_properties")
        }
    return {}
