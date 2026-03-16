from typing import Any, Dict, Optional
from ..utils.utils import parse_and_check_login


async def create_poll(
    post_func,
    ctx: Any,
    title: str,
    thread_id: str,
    options: Optional[Dict[str, bool]] = None,
):
    if not options:
        options = {}

    form = {
        "target_id": thread_id,
        "question_text": title,
    }

    for i, (opt_text, is_selected) in enumerate(options.items()):
        form[f"option_text_array[{i}]"] = opt_text
        form[f"option_is_selected_array[{i}]"] = "1" if is_selected else "0"

    url = "https://www.facebook.com/messaging/group_polling/create_poll/?dpr=1"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if (
        res_data
        and "payload" in res_data
        and res_data["payload"].get("status") != "success"
    ):
        raise Exception(f"createPoll error: {res_data['payload'].get('status')}")

    return res_data
