import json
from typing import Any
from ..utils.utils import parse_and_check_login


async def search_stickers(post_func, ctx: Any, query: str = ""):
    form = {
        "fb_api_req_friendly_name": "StickersFlyoutTagSelectorQuery",
        "variables": json.dumps(
            {
                "stickerWidth": 64,
                "stickerHeight": 64,
                "stickerInterface": "messages",
                "query": query,
            }
        ),
        "doc_id": "4642836929159953",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"searchStickers errors: {res_data['errors']}")

    stickers = []
    try:
        edges = res_data["data"]["sticker_search"]["sticker_results"]["edges"]
        for edge in edges:
            node = edge["node"]
            stickers.append(
                {
                    "id": node.get("id"),
                    "image": node.get("image"),
                    "package": (
                        {"name": node["pack"].get("name"), "id": node["pack"].get("id")}
                        if node.get("pack")
                        else {}
                    ),
                    "label": node.get("label"),
                }
            )
    except Exception:
        pass

    return stickers
