import asyncio
from typing import Any, List, Union
from ..utils.utils import parse_and_check_login


async def upload_attachment(post_func, ctx: Any, attachments: Union[Any, List[Any]]):
    if not isinstance(attachments, list):
        attachments = [attachments]

    url = "https://upload.facebook.com/ajax/mercury/upload.php"

    async def upload_one(attachment):
        # attachment can be a file-like object or bytes
        files = {"upload_1024": attachment}
        form = {"voice_clip": "true"}

        # We need our post_func to support files.
        # Let's use ctx.client directly for ease or adapt post_func.
        # Actually, let's assume post_func can handle files if passed.
        res = await ctx.client.post(
            url, data=form, files=files, headers=ctx.client.headers
        )
        res_data = parse_and_check_login(ctx, res)
        if not res_data or res_data.get("error"):
            raise Exception(
                f"uploadAttachment error: {res_data.get('error') if res_data else 'Empty response'}"
            )

        return res_data["payload"]["metadata"][0]

    tasks = [upload_one(a) for a in attachments]
    return await asyncio.gather(*tasks)
