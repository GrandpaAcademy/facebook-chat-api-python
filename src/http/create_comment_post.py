import json
import base64
import random
from typing import Any, Optional, Dict, Union
from ..utils.utils import parse_and_check_login, get_guid

async def create_comment_post(post_func, ctx: Any, msg_info: Union[str, Dict[str, Any]], post_id: str, reply_comment_id: Optional[str] = None):
    if isinstance(msg_info, str):
        msg_info = {"body": msg_info}
        
    body = msg_info.get("body", "")
    
    # feedback:POST_ID format
    feedback_id = base64.b64encode(f"feedback:{post_id}".encode()).decode()
    
    parent_comment_id = None
    if reply_comment_id:
        parent_comment_id = reply_comment_id if not reply_comment_id.isdigit() else base64.b64encode(f"comment:{post_id}_{reply_comment_id}".encode()).decode()

    variables = {
        "feedLocation": "NEWSFEED",
        "feedbackSource": 1,
        "groupID": None,
        "input": {
            "client_mutation_id": str(random.randint(0, 19)),
            "actor_id": ctx.user_id,
            "attachments": [],
            "feedback_id": feedback_id,
            "formatting_style": None,
            "message": {
                "ranges": [],  
                "text": body
            }, 
            "reply_comment_parent_fbid": parent_comment_id,
            "reply_target_clicked": bool(reply_comment_id),
            "attribution_id_v2": "CometHomeRoot.react,comet.home,via_cold_start,156248,4748854339,,",
            "vod_video_timestamp": None,
            "feedback_referrer": "/",
            "is_tracking_encrypted": True,
            "tracking": [], 
            "feedback_source": "NEWS_FEED", 
            "idempotence_token": f"client:{get_guid()}",
            "session_id": get_guid()
        },
        "inviteShortLinkKey": None,
        "renderLocation": None,
        "scale": 1,
        "useDefaultActor": False, 
        "focusCommentID": None
    }

    form = {
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "useCometUFICreateCommentMutation",
        "variables": json.dumps(variables),
        "server_timestamps": True,
        "doc_id": "6993516810709754"
    }
    
    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("errors"):
        raise Exception(f"createCommentPost errors: {res_data['errors']}")
        
    try:
        comment_data = res_data["data"]["comment_create"]
        return {
            "id": comment_data["feedback_comment_edge"]["node"]["id"],
            "url": comment_data["feedback_comment_edge"]["node"]["feedback"]["url"],
            "count": comment_data["feedback"]["total_comment_count"]
        }
    except:
        return res_data
