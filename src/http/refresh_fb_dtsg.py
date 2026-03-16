from typing import Any, Dict
from ..utils.utils import get, get_from

async def refresh_fb_dtsg(get_func, ctx: Any):
    # This is a simplified version of refreshFb_dtsg
    url = "https://m.facebook.com/"
    res = await get_func(url, ctx, None)
    html = res.text
    
    fb_dtsg = get_from(html, 'name="fb_dtsg" value="', '"')
    jazoest = get_from(html, 'name="jazoest" value="', '"')
    
    if fb_dtsg:
        ctx.fb_dtsg = fb_dtsg
    if jazoest:
        ctx.ttstamp = jazoest
        
    return {
        "fb_dtsg": fb_dtsg,
        "jazoest": jazoest
    }
