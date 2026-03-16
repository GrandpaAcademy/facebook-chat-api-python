import time
from typing import Any, List, Union
from ..utils.utils import parse_and_check_login


async def forward_attachment(
    post_func, ctx: Any, attachment_id: str, user_or_users: Union[str, List[str]]
):
    if not isinstance(user_or_users, list):
        user_or_users = [user_or_users]

    timestamp = int(time.time())
    form = {
        "attachment_id": attachment_id,
    }

    for i, user_id in enumerate(user_or_users):
        form[f"recipient_map[{timestamp + i}]"] = user_id

    url = "https://www.facebook.com/mercury/attachments/forward/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("error"):
        raise Exception(f"forwardAttachment error: {res_data['error']}")

    return res_data
