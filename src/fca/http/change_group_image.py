from ..utils.utils import (
    post,
    parse_and_check_login,
    generate_offline_threading_id,
    generate_timestamp_relative,
)
import time


async def change_group_image(ctx, image, thread_id: str):
    # Handle upload first
    url_upload = "https://upload.facebook.com/ajax/mercury/upload.php"
    files = {"attachment[]": image}
    form_upload = {"images_only": "true"}

    res_upload = await ctx.client.post(
        url_upload, data=form_upload, files=files, headers=ctx.client.headers
    )
    res_data_upload = parse_and_check_login(ctx)(res_upload)

    if not res_data_upload or res_data_upload.get("error"):
        raise Exception(
            f"changeGroupImage upload error: {res_data_upload.get('error') if res_data_upload else 'Empty response'}"
        )

    thread_image_id = res_data_upload["payload"]["metadata"][0]["image_id"]

    # Now set the image
    otid = generate_offline_threading_id()
    form = {
        "client": "mercury",
        "action_type": "ma-type:log-message",
        "author": f"fbid:{ctx.user_id}",
        "author_email": "",
        "ephemeral_ttl_mode": "0",
        "is_filtered_content": False,
        "is_filtered_content_account": False,
        "is_filtered_content_bh": False,
        "is_filtered_content_invalid_app": False,
        "is_filtered_content_quasar": False,
        "is_forward": False,
        "is_spoof_warning": False,
        "is_unread": False,
        "log_message_type": "log:thread-image",
        "manual_retry_cnt": "0",
        "message_id": otid,
        "offline_threading_id": otid,
        "source": "source:chat:web",
        "source_tags[0]": "source:chat",
        "status": "0",
        "thread_fbid": thread_id,
        "thread_id": thread_id,
        "timestamp": int(time.time() * 1000),
        "timestamp_absolute": "Today",
        "timestamp_relative": generate_timestamp_relative(),
        "timestamp_time_passed": "0",
        "thread_image_id": thread_image_id,
    }

    res = await post("https://www.facebook.com/messaging/set_thread_image/", ctx, form)
    res_data = parse_and_check_login(ctx)(res)

    if res_data.get("error"):
        raise Exception(f"changeGroupImage set error: {res_data.get('error')}")

    return {"success": True}
