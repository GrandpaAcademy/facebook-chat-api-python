from typing import Any
from ..utils.utils import parse_and_check_login

async def resolve_photo_url(get_func, ctx: Any, photo_id: str):
    form = {
        "photo_id": photo_id,
    }
    res = await get_func("https://www.facebook.com/mercury/attachments/photo", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        return None
    if res_data.get("error"):
        raise Exception(f"resolvePhotoUrl error: {res_data['error']}")
        
    try:
        # Based on Node.js: const photoUrl = resData.jsmods.require[0][3][0];
        photo_url = res_data["jsmods"]["require"][0][3][0]
        return photo_url
    except (KeyError, IndexError):
        return None
