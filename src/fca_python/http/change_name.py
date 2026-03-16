import json
from typing import Any
from ..utils.utils import parse_and_check_login, get_guid


async def change_name(post_func, ctx: Any, name_info: dict, format: str = "complete"):
    # name_info: {"first_name": "...", "middle_name": "...", "last_name": "..."}
    first_name = name_info.get("first_name")
    middle_name = name_info.get("middle_name", "")
    last_name = name_info.get("last_name")

    if not first_name or not last_name:
        raise Exception("first_name and last_name are required")

    full_name = ""
    if format == "complete":
        full_name = (
            f"{last_name} {middle_name + ' ' if middle_name else ''}{first_name}"
        )
    elif format == "standard":
        full_name = f"{last_name} {first_name}"
    elif format == "reversed":
        full_name = (
            f"{first_name} {middle_name + ' ' if middle_name else ''}{last_name}"
        )
    else:
        full_name = (
            f"{last_name} {middle_name + ' ' if middle_name else ''}{first_name}"
        )

    variables = {
        "client_mutation_id": get_guid(),
        "family_device_id": "device_id_fetch_datr",
        "identity_ids": [ctx.user_id],
        "full_name": full_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "interface": "FB_WEB",
    }

    form = {
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "useFXIMUpdateNameMutation",
        "variables": json.dumps(variables),
        "server_timestamps": True,
        "doc_id": "5763510853763960",
    }

    headers = {
        "Origin": "https://accountscenter.facebook.com",
        "Referer": f"https://accountscenter.facebook.com/profiles/{ctx.user_id}/name",
    }

    url = "https://accountscenter.facebook.com/api/graphql/"
    # We'll use ctx.client.post directly to pass custom headers
    res = await ctx.client.post(
        url, data=form, headers={**ctx.client.headers, **headers}
    )
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"changeName errors: {res_data['errors']}")

    if (
        res_data
        and "data" in res_data
        and res_data["data"].get("fxim_update_identity_name", {}).get("error")
    ):
        raise Exception(
            f"changeName data error: {res_data['data']['fxim_update_identity_name']['error']}"
        )

    return res_data
