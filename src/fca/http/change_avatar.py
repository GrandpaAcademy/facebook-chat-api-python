import json
from typing import Any, Optional
from ..utils.utils import parse_and_check_login


async def change_avatar(
    post_func, ctx: Any, image: Any, caption: str = "", timestamp: Optional[int] = None
):
    # Step 1: Upload the image
    upload_url = "https://www.facebook.com/profile/picture/upload/"
    # image can be bytes or file-like object
    files = {"file": image}
    form = {
        "profile_id": ctx.user_id,
        "photo_source": 57,
        "av": ctx.user_id,
    }

    # Use ctx.client directly for file upload
    res = await ctx.client.post(
        upload_url, data=form, files=files, headers=ctx.client.headers
    )
    res_data = parse_and_check_login(ctx, res)
    if not res_data or res_data.get("error"):
        raise Exception(
            f"changeAvatar upload error: {res_data.get('error') if res_data else 'Empty response'}"
        )

    fbid = res_data["payload"]["fbid"]

    # Step 2: Set the profile picture via GraphQL
    gql_url = "https://www.facebook.com/api/graphql/"
    variables = {
        "input": {
            "caption": caption,
            "existing_photo_id": fbid,
            "expiration_time": timestamp,
            "profile_id": ctx.user_id,
            "profile_pic_method": "EXISTING",
            "profile_pic_source": "TIMELINE",
            "scaled_crop_rect": {
                "height": 1,
                "width": 1,
                "x": 0,
                "y": 0,
            },
            "skip_cropping": True,
            "actor_id": ctx.user_id,
            "client_mutation_id": str(ctx.client_mutation_id),
        },
        "isPage": False,
        "isProfile": True,
        "scale": 3,
    }
    ctx.client_mutation_id += 1

    gql_form = {
        "av": ctx.user_id,
        "fb_api_req_friendly_name": "ProfileCometProfilePictureSetMutation",
        "fb_api_caller_class": "RelayModern",
        "doc_id": "5066134240065849",
        "variables": json.dumps(variables),
    }

    res_gql = await post_func(gql_url, ctx, gql_form)
    res_gql_data = parse_and_check_login(ctx, res_gql)

    if not res_gql_data or res_gql_data.get("errors"):
        raise Exception(
            f"changeAvatar mutation error: {res_gql_data.get('errors') if res_gql_data else 'Empty response'}"
        )

    return res_gql_data[0]["data"]["profile_picture_set"]
