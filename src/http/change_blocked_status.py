from ..utils.utils import post, parse_and_check_login, save_cookies


async def change_blocked_status(ctx, user_id: str, block: bool):
    url = f"https://www.facebook.com/messaging/{'' if block else 'un'}block_messages/"
    form = {"fbid": user_id}

    res = await post(url, ctx, form)
    save_cookies(ctx.client)(res)
    res_data = parse_and_check_login(ctx)(res)

    if res_data.get("error"):
        raise Exception(f"changeBlockedStatus error: {res_data.get('error')}")

    return {"success": True}
