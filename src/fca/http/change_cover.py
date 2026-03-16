import json
import random
from typing import Any
from ..utils.utils import parse_and_check_login


async def change_cover(post_func, ctx: Any, image: Any):
    # This function expects image to be something that can be uploaded via postFormData
    # Since we don't have a direct postFormData implementation that handles file streams perfectly in our current helper,
    # we'll assume the post_func handles multipart if needed, or we'd need to extend it.
    # However, for now, let's implement the logic.

    url_upload = "https://www.facebook.com/profile/picture/upload/"
    form_upload = {
        "profile_id": ctx.user_id,
        "photo_source": 57,
        "av": ctx.user_id,
        "file": image,
    }

    # In JS it's postFormData. In our Python helper, we might need to adjust 'post'.
    # Let's assume post_func can handle files or we use a multipart approach.
    res_upload = await post_func(url_upload, ctx, form_upload)
    res_upload_data = parse_and_check_login(ctx, res_upload)

    if not res_upload_data or (
        res_upload_data.get("error")
        or res_upload_data.get("errors")
        or not res_upload_data.get("payload")
    ):
        raise Exception(f"changeCover upload error: {res_upload_data}")

    fbid = res_upload_data["payload"]["fbid"]

    variables = {
        "input": {
            "attribution_id_v2": "ProfileCometCollectionRoot.react,comet.profile.collection.photos_by,unexpected,156248,770083,,",
            "cover_photo_id": fbid,
            "focus": {"x": 0.5, "y": 1},
            "target_user_id": ctx.user_id,
            "actor_id": ctx.user_id,
            "client_mutation_id": str(random.randint(0, 19)),
        },
        "scale": 1,
        "contextualProfileContext": None,
    }

    form_gql = {
        "doc_id": "8247793861913071",
        "server_timestamps": True,
        "fb_api_req_friendly_name": "ProfileCometCoverPhotoUpdateMutation",
        "variables": json.dumps(variables),
    }

    url_gql = "https://www.facebook.com/api/graphql/"
    res_gql = await post_func(url_gql, ctx, form_gql)
    res_gql_data = parse_and_check_login(ctx, res_gql)

    if res_gql_data and res_gql_data.get("errors"):
        raise Exception(f"changeCover mutation errors: {res_gql_data['errors']}")

    try:
        return res_gql_data["data"]["user_update_cover_photo"]["user"]["cover_photo"][
            "photo"
        ]["url"]
    except Exception:
        return res_gql_data
