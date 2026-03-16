import json
import random
import time
from typing import Any, Dict, Union
from ..utils.utils import parse_and_check_login, get_guid


async def create_post(post_func, ctx: Any, msg_info: Union[str, Dict[str, Any]]):
    if isinstance(msg_info, str):
        msg_info = {"body": msg_info}

    body = msg_info.get("body", "")
    group_id = msg_info.get("groupID")
    url_attachment = msg_info.get("url")
    allow_user_ids = msg_info.get("allowUserID", [])
    if not isinstance(allow_user_ids, list):
        allow_user_ids = [allow_user_ids]

    session_id = get_guid()

    # Base state for privacy: EVERYONE, FRIENDS, SELF
    base_states = ["EVERYONE", "FRIENDS", "SELF"]
    base_state_idx = msg_info.get("baseState", 1) - 1
    if base_state_idx < 0 or base_state_idx >= len(base_states):
        base_state_idx = 0

    variables = {
        "input": {
            "composer_entry_point": (
                "share_modal"
                if (not group_id and url_attachment)
                else "inline_composer"
            ),
            "composer_source_surface": (
                "feed_story"
                if (not group_id and url_attachment)
                else "group" if group_id else "timeline"
            ),
            "composer_type": (
                "share"
                if (not group_id and url_attachment)
                else "group" if group_id else "timeline"
            ),
            "idempotence_token": f"{session_id}_FEED",
            "source": "WWW",
            "attachments": [],
            "audience": (
                {"to_id": group_id}
                if group_id
                else {
                    "privacy": {
                        "allow": allow_user_ids,
                        "base_state": (
                            base_states[2]
                            if allow_user_ids
                            else base_states[base_state_idx]
                        ),
                        "deny": [],
                        "tag_expansion_state": "UNSPECIFIED",
                    }
                }
            ),
            "message": {"ranges": [], "text": body},
            "with_tags_ids": [],
            "inline_activities": [],
            "explicit_place_id": 0,
            "text_format_preset_id": 0,
            "logging": {"composer_session_id": session_id},
            "navigation_data": {
                "attribution_id_v2": (
                    f"CometGroupDiscussionRoot.react,comet.group,tap_search_bar,{int(time.time()*1000)},909538,2361831622,"
                    if group_id
                    else f"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,via_cold_start,{int(time.time()*1000)},796829,190055527696468,"
                )
            },
            "is_tracking_encrypted": bool(url_attachment),
            "tracking": [],
            "event_share_metadata": {"surface": "newsfeed"},
            "actor_id": ctx.user_id,
            "client_mutation_id": str(random.randint(0, 19)),
        },
        "displayCommentsFeedbackContext": None,
        "displayCommentsContextEnableComment": None,
        "displayCommentsContextIsAdPreview": None,
        "displayCommentsContextIsAggregatedShare": None,
        "displayCommentsContextIsStorySet": None,
        "feedLocation": "GROUP" if group_id else "TIMELINE",
        "feedbackSource": 0,
        "focusCommentID": None,
        "gridMediaWidth": 230,
        "groupID": None,
        "scale": 1,
        "privacySelectorRenderLocation": "COMET_STREAM",
        "renderLocation": "group" if group_id else "timeline",
        "useDefaultActor": False,
        "inviteShortLinkKey": None,
        "isFeed": False,
        "isFundraiser": False,
        "isFunFactPost": False,
        "isGroup": bool(group_id),
        "isEvent": False,
        "isTimeline": not group_id,
        "isSocialLearning": False,
        "isPageNewsFeed": False,  # Assuming no page ID support for now
        "isProfileReviews": False,
        "isWorkSharedDraft": False,
        "UFI2CommentsProvider_commentsKey": (
            "CometGroupDiscussionRootSuccessQuery"
            if group_id
            else "ProfileCometTimelineRoute"
        ),
        "hashtag": None,
        "canUserManageOffers": False,
        "__relay_internal__pv__CometUFIIsRTAEnabledrelayprovider": False,
        "__relay_internal__pv__IsWorkUserrelayprovider": False,
        "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
        "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": False,
        "__relay_internal__pv__StoriesRingrelayprovider": False,
    }

    # Handling Attachments (simplified, not handling file uploads here yet)
    if url_attachment:
        # Link preview scrape would go here
        pass

    form = {
        "fb_api_req_friendly_name": "ComposerStoryCreateMutation",
        "variables": json.dumps(variables),
        "server_timestamps": True,
        "doc_id": "6255089511280268",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"createPost errors: {res_data['errors']}")

    try:
        post_url = res_data["data"]["story_create"]["story"]["url"]
        return post_url
    except Exception:
        return res_data
