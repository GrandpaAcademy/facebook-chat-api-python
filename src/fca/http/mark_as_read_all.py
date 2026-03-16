from typing import Any
from ..utils.utils import parse_and_check_login


async def mark_as_read_all(post_func, ctx: Any):
    form = {"folder": "inbox"}

    url = "https://www.facebook.com/ajax/mercury/mark_folder_as_read.php"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("error"):
        raise Exception(f"markAsReadAll error: {res_data['error']}")

    return res_data
