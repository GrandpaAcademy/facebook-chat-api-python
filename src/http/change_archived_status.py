from typing import Any, List, Union
from ..utils.utils import parse_and_check_login


async def change_archived_status(
    post_func, ctx: Any, thread_or_threads: Union[str, List[str]], archive: bool
):
    form = {}

    if not isinstance(thread_or_threads, list):
        thread_or_threads = [thread_or_threads]

    for thread_id in thread_or_threads:
        form[f"ids[{thread_id}]"] = "true" if archive else "false"

    url = "https://www.facebook.com/ajax/mercury/change_archived_status.php"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("error"):
        raise Exception(f"changeArchivedStatus error: {res_data['error']}")
    return res_data
