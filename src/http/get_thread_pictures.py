import asyncio
from typing import Any
from ..utils.utils import parse_and_check_login


async def get_thread_pictures(
    post_func, ctx: Any, thread_id: str, offset: int, limit: int
):
    url = "https://www.facebook.com/ajax/messaging/attachments/sharedphotos.php"
    form = {"thread_id": thread_id, "offset": offset, "limit": limit}

    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("error"):
        raise Exception(f"getThreadPictures error: {res_data['error']}")

    images_data = res_data.get("payload", {}).get("imagesData", [])

    async def get_image_detail(image_fbid):
        detail_form = {"thread_id": thread_id, "image_id": image_fbid}
        detail_res = await post_func(url, ctx, detail_form)
        detail_data = parse_and_check_login(ctx, detail_res)

        if detail_data and detail_data.get("error"):
            return None

        try:
            # Replicating the messy extraction logic from JS
            query_thread_id = detail_data["jsmods"]["require"][0][3][1][
                "query_metadata"
            ]["query_path"][0]["message_thread"]
            image_info = detail_data["jsmods"]["require"][0][3][1]["query_results"][
                query_thread_id
            ]["message_images"]["edges"][0]["node"]["image2"]
            return image_info
        except KeyError, IndexError:
            return None

    tasks = [get_image_detail(img["fbid"]) for img in images_data]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
