from typing import Any, Optional, List, Dict

from ..utils.utils import (
    get,
    post,
)

from .mqtt import listen_mqtt

# Global-like imports from modular services
from ..http.send_message import send_message as http_send_message
from ..http.get_user_info import get_user_info as http_get_user_info
from ..http.mark_as_read import mark_as_read as http_mark_as_read
from ..http.set_title import set_title as http_set_title
from ..http.logout import logout as http_logout
from ..http.delete_message import delete_message as http_delete_message
from ..http.unsend_message import unsend_message as http_unsend_message
from ..http.change_nickname import change_nickname as http_change_nickname
from ..http.change_thread_emoji import change_thread_emoji as http_change_thread_emoji
from ..http.add_user_to_group import add_user_to_group as http_add_user_to_group
from ..http.remove_user_from_group import (
    remove_user_from_group as http_remove_user_from_group,
)
from ..http.change_admin_status import change_admin_status as http_change_admin_status
from ..http.send_typing_indicator import (
    send_typing_indicator as http_send_typing_indicator,
)
from ..http.get_user_id import get_user_id as http_get_user_id
from ..http.resolve_photo_url import resolve_photo_url as http_resolve_photo_url
from ..http.mark_as_delivered import mark_as_delivered as http_mark_as_delivered
from ..http.get_friends_list import get_friends_list as http_get_friends_list
from ..http.change_avatar import change_avatar as http_change_avatar
from ..http.upload_attachment import upload_attachment as http_upload_attachment

# New features
from ..graphql.create_new_group import create_new_group as graphql_create_new_group
from ..http.change_group_image import change_group_image as http_change_group_image
from ..http.change_blocked_status import (
    change_blocked_status as http_change_blocked_status,
)
from ..http.remove_suspicious_account import (
    remove_suspicious_account as http_remove_suspicious_account,
)
from ..http.get_uid import get_uid as http_get_uid


from ..graphql.set_message_reaction import (
    set_message_reaction as gql_set_message_reaction,
)

from ..graphql.get_thread_info import get_thread_info as gql_get_thread_info
from ..graphql.get_thread_list import get_thread_list as gql_get_thread_list
from ..graphql.set_active_status import set_active_status as gql_set_active_status
from ..graphql.get_thread_history import get_thread_history as gql_get_thread_history
from ..graphql.change_thread_color import change_thread_color as gql_change_thread_color

from ..http.delete_thread import delete_thread as http_delete_thread
from ..http.mute_thread import mute_thread as http_mute_thread
from ..http.change_archived_status import (
    change_archived_status as http_change_archived_status,
)
from ..http.search_for_thread import search_for_thread as http_search_for_thread
from ..http.get_thread_pictures import get_thread_pictures as http_get_thread_pictures
from ..graphql.get_thread_theme import get_thread_theme as gql_get_thread_theme
from ..graphql.set_thread_theme import set_thread_theme as gql_set_thread_theme

from ..http.change_bio import change_bio as http_change_bio
from ..http.change_name import change_name as http_change_name
from ..http.change_username import change_username as http_change_username
from ..http.set_profile_lock import set_profile_lock as http_set_profile_lock
from ..http.get_access import get_access as http_get_access
from ..http.get_avatar_user import get_avatar_user as http_get_avatar_user

from ..http.send_friend_request import send_friend_request as http_send_friend_request
from ..http.handle_friend_request import (
    handle_friend_request as http_handle_friend_request,
)
from ..http.unfriend import unfriend as http_unfriend
from ..http.follow import follow as http_follow
from ..graphql.search_friends import search_friends as gql_search_friends
from ..graphql.suggest_friend import suggest_friend as gql_suggest_friend

from ..http.note import check_note, create_note, delete_note
from ..http.share_contact import share_contact as http_share_contact
from ..http.share_link import share_link as http_share_link
from ..http.forward_attachment import forward_attachment as http_forward_attachment
from ..http.create_poll import create_poll as http_create_poll

from ..http.create_post import create_post as http_create_post
from ..http.create_comment_post import create_comment_post as http_create_comment_post
from ..http.set_post_reaction import set_post_reaction as http_set_post_reaction
from ..http.set_story_reaction import set_story_reaction as http_set_story_reaction
from ..http.set_story_seen import set_story_seen as http_set_story_seen
from ..http.story_manager import story_manager as http_story_manager

from ..http.mark_as_seen import mark_as_seen as http_mark_as_seen
from ..http.mark_as_read_all import mark_as_read_all as http_mark_as_read_all
from ..http.refresh_fb_dtsg import refresh_fb_dtsg as http_refresh_fb_dtsg
from ..http.get_region import get_region as http_get_region
from ..graphql.search_stickers import search_stickers as gql_search_stickers

from ..http.handle_message_request import (
    handle_message_request as http_handle_message_request,
)
from ..http.change_cover import change_cover as http_change_cover


def get_api(ctx: Any) -> Dict[str, Any]:
    api = {
        "sendMessage": lambda msg, thread_id, is_single_user=None, reply_to_message=None: http_send_message(
            post, ctx, msg, thread_id, is_single_user, reply_to_message
        ),
        "getUserInfo": lambda ids: http_get_user_info(post, ctx, ids),
        "getThreadInfo": lambda thread_id: gql_get_thread_info(post, ctx, thread_id),
        "getThreadList": lambda limit, timestamp=None, tags=[""]: gql_get_thread_list(
            post, ctx, limit, timestamp, tags
        ),
        "markAsRead": lambda thread_id, read=True: http_mark_as_read(
            post, ctx, thread_id, read
        ),
        "setTitle": lambda new_title, thread_id: http_set_title(
            post, ctx, new_title, thread_id
        ),
        "logout": lambda: http_logout(post, ctx),
        "setActiveStatus": lambda is_active: gql_set_active_status(
            post, ctx, is_active
        ),
        "getThreadHistory": lambda thread_id, amount, timestamp=None: gql_get_thread_history(
            post, ctx, thread_id, amount, timestamp
        ),
        "deleteMessage": lambda message_ids: http_delete_message(
            post, ctx, message_ids
        ),
        "unsendMessage": lambda message_id: http_unsend_message(post, ctx, message_id),
        "changeNickname": lambda nickname, thread_id, participant_id: http_change_nickname(
            post, ctx, nickname, thread_id, participant_id
        ),
        "changeThreadColor": lambda color, thread_id: gql_change_thread_color(
            post, ctx, color, thread_id
        ),
        "changeThreadEmoji": lambda emoji, thread_id: http_change_thread_emoji(
            post, ctx, emoji, thread_id
        ),
        "addUserToGroup": lambda user_id, thread_id: http_add_user_to_group(
            post, ctx, user_id, thread_id
        ),
        "removeUserFromGroup": lambda user_id, thread_id: http_remove_user_from_group(
            post, ctx, user_id, thread_id
        ),
        "changeAdminStatus": lambda thread_id, admin_ids, admin_status: http_change_admin_status(
            post, ctx, thread_id, admin_ids, admin_status
        ),
        "sendTypingIndicator": lambda thread_id, is_typing, is_group=None: http_send_typing_indicator(
            post,
            lambda t_id: http_get_user_info(get, ctx, t_id),
            ctx,
            thread_id,
            is_typing,
            is_group,
        ),
        "getUserID": lambda name: http_get_user_id(get, ctx, name),
        "resolvePhotoUrl": lambda photo_id: http_resolve_photo_url(get, ctx, photo_id),
        "markAsDelivered": lambda thread_id, message_id: http_mark_as_delivered(
            post, ctx, thread_id, message_id
        ),
        "getFriendsList": lambda: http_get_friends_list(post, ctx),
        "setMessageReaction": lambda reaction, message_id: gql_set_message_reaction(
            post, ctx, reaction, message_id
        ),
        "changeAvatar": lambda image, caption="", timestamp=None: http_change_avatar(
            post, ctx, image, caption, timestamp
        ),
        # Thread Management
        "deleteThread": lambda thread_ids: http_delete_thread(post, ctx, thread_ids),
        "muteThread": lambda thread_id, duration: http_mute_thread(
            post, ctx, thread_id, duration
        ),
        "changeArchivedStatus": lambda thread_ids, archive: http_change_archived_status(
            post, ctx, thread_ids, archive
        ),
        "searchForThread": lambda name: http_search_for_thread(post, ctx, name),
        "getThreadPictures": lambda thread_id, offset, limit: http_get_thread_pictures(
            post, ctx, thread_id, offset, limit
        ),
        "getThreadTheme": lambda thread_id: gql_get_thread_theme(post, ctx, thread_id),
        "setThreadTheme": lambda thread_id, theme_id: gql_set_thread_theme(
            ctx, thread_id, theme_id
        ),
        # User & Profile
        "changeBio": lambda bio, publish=False: http_change_bio(
            post, ctx, bio, publish
        ),
        "changeName": lambda first, middle, last: http_change_name(
            post, ctx, first, middle, last
        ),
        "changeUsername": lambda username: http_change_username(post, ctx, username),
        "changeCover": lambda image: http_change_cover(post, ctx, image),
        "setProfileLock": lambda enabled: http_set_profile_lock(post, ctx, enabled),
        "getAccess": lambda: http_get_access(get, post, ctx),
        "getAvatarUser": lambda user_ids, size=50: http_get_avatar_user(
            get, ctx, user_ids, size
        ),
        # Social & Interaction
        "sendFriendRequest": lambda user_id: http_send_friend_request(
            post, ctx, user_id
        ),
        "handleFriendRequest": lambda user_id, accept: http_handle_friend_request(
            post, ctx, user_id, accept
        ),
        "unfriend": lambda user_id: http_unfriend(post, ctx, user_id),
        "follow": lambda user_id, enable=True: http_follow(post, ctx, user_id, enable),
        "handleMessageRequest": lambda thread_id, accept: http_handle_message_request(
            post, ctx, thread_id, accept
        ),
        "searchFriends": lambda query: gql_search_friends(post, ctx, query),
        "suggestFriend": lambda count=30, cursor=None: gql_suggest_friend(
            post, ctx, count, cursor
        ),
        # Messenger Features
        "checkNote": lambda: check_note(post, ctx),
        "createNote": lambda text, options=None: create_note(post, ctx, text, options),
        "deleteNote": lambda note_id: delete_note(post, ctx, note_id),
        "shareContact": lambda text, sender_id, thread_id: http_share_contact(
            ctx, text, sender_id, thread_id
        ),
        "shareLink": lambda text, url, thread_id: http_share_link(
            ctx, text, url, thread_id
        ),
        "forwardAttachment": lambda attachment_id, user_or_users: http_forward_attachment(
            post, ctx, attachment_id, user_or_users
        ),
        "createPoll": lambda title, thread_id, options=None: http_create_poll(
            post, ctx, title, thread_id, options
        ),
        # Post & Stories
        "createPost": lambda msg_info: http_create_post(post, ctx, msg_info),
        "createCommentPost": lambda msg_info, post_id, reply_id=None: http_create_comment_post(
            post, ctx, msg_info, post_id, reply_id
        ),
        "setPostReaction": lambda post_id, type: http_set_post_reaction(
            post, ctx, post_id, type
        ),
        "setStoryReaction": lambda story_id, react: http_set_story_reaction(
            post, ctx, story_id, react
        ),
        "setStorySeen": lambda story_id: http_set_story_seen(post, ctx, story_id),
        "storyManager": lambda options: http_story_manager(post, ctx, options),
        # Status & Maintenance
        "markAsSeen": lambda timestamp=None: http_mark_as_seen(post, ctx, timestamp),
        "markAsReadAll": lambda: http_mark_as_read_all(post, ctx),
        "getRegion": lambda: http_get_region(ctx),
        "searchStickers": lambda query="": gql_search_stickers(post, ctx, query),
        "listenMqtt": lambda callback: listen_mqtt(ctx, callback),
        "uploadAttachment": lambda attachments: http_upload_attachment(
            post, ctx, attachments
        ),
        "getFreshDtsg": lambda: http_refresh_fb_dtsg(post, ctx),
        # New features
        "createNewGroup": lambda participant_ids, group_title=None: graphql_create_new_group(
            ctx, participant_ids, group_title
        ),
        "changeGroupImage": lambda image, thread_id: http_change_group_image(
            ctx, image, thread_id
        ),
        "changeBlockedStatus": lambda user_id, block: http_change_blocked_status(
            ctx, user_id, block
        ),
        "removeSuspiciousAccount": lambda: http_remove_suspicious_account(ctx),
        "getUID": lambda link: http_get_uid(link),
    }

    # High-speed MQTT actions (if connected)
    if hasattr(ctx, "mqtt_client") and ctx.mqtt_client:
        api.update(
            {
                "editMessage": lambda text, message_id: ctx.mqtt_client.edit_message(
                    text, message_id
                ),
                "sendMessageMqtt": lambda msg, thread_id, reply_to=None: ctx.mqtt_client.send_message_mqtt(
                    msg, thread_id, reply_to
                ),
                "setMessageReactionMqtt": lambda reaction, message_id, thread_id: ctx.mqtt_client.set_message_reaction_mqtt(
                    reaction, message_id, thread_id
                ),
                "changeBlockedStatusMqtt": lambda user_id, status, type="messenger": ctx.mqtt_client.change_blocked_status_mqtt(
                    user_id, status, type
                ),
            }
        )

    # Aliases
    api["sendMessageDM"] = lambda msg, thread_id, reply_to=None: http_send_message(
        post, ctx, msg, thread_id, reply_to=reply_to, is_single_user=True
    )

    # Fallback logic for sendMessage
    original_send_message = api["sendMessage"]

    async def sendMessageWithFallback(msg, thread_id, reply_to=None):
        try:
            return await original_send_message(msg, thread_id, reply_to=reply_to)
        except Exception as e:
            # If MQTT is connected, we might try sendMessageMqtt as fallback or vice versa
            # But the JS logic fallbacks to a different method entirely sometimes.
            # Here we'll just log and try the HTTP method if MQTT failed, or just re-raise if it's already HTTP.
            raise e

    api["sendMessage"] = sendMessageWithFallback

    return api


async def get_thread_list(
    ctx: Any, limit: int, timestamp: Optional[int] = None, tags: List[str] = [""]
):
    return await gql_get_thread_list(post, ctx, limit, timestamp, tags)
