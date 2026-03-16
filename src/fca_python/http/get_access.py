import re
import json
from typing import Any
from urllib.parse import quote
from ..utils.utils import get_from


async def get_access(ctx: Any, auth_code: str = ""):
    if hasattr(ctx, "access_token") and ctx.access_token:
        return ctx.access_token

    base_url = "https://business.facebook.com/"
    cm_url = base_url + "content_management"

    # Step 1: Get Content Management page to find LSD
    headers = {
        "Origin": base_url,
    }
    res = await ctx.client.get(cm_url, headers={**ctx.client.headers, **headers})
    html = res.text

    lsd = get_from(html, '["LSD",[],{"token":"', '"}')

    async def submit_code(code: str):
        referer = f"{base_url}security/twofactor/reauth/?twofac_next={quote(cm_url)}&type=avoid_bypass&app_id=0&save_device=0"
        form = {"approvals_code": code, "save_device": True, "lsd": lsd}
        post_headers = {"Referer": referer, "Origin": base_url}
        post_res = await ctx.client.post(
            base_url + "security/twofactor/reauth/enter/",
            data=form,
            headers={**ctx.client.headers, **post_headers},
        )

        # Response might be a JS redirect or similar
        try:
            res_json = json.loads(post_res.text.split(";").pop())
            if res_json.get("payload") and not res_json["payload"].get("codeConfirmed"):
                raise Exception(
                    res_json["payload"].get("message", "Code confirmation failed")
                )
        except Exception:
            pass  # Sometimes it just works and redirects

        # Get CM again to find token
        cm_res = await ctx.client.get(cm_url, headers=ctx.client.headers)
        cm_html = cm_res.text

        token_match = re.search(r'"accessToken":"(\S+)","clientID":', cm_html)
        if not token_match:
            raise Exception("Access token not found in page")

        ctx.access_token = token_match.group(1)
        return ctx.access_token

    if auth_code and len(auth_code) == 6:
        return await submit_code(auth_code)
    else:
        # If no code provided, it might already be authorized or need 2FA
        token_match = re.search(r'"accessToken":"(\S+)","clientID":', html)
        if token_match:
            ctx.access_token = token_match.group(1)
            return ctx.access_token
        else:
            raise Exception(
                "2FA required or Access token not found. Please provide an auth_code."
            )
