import time
import random
import json
import re
from typing import Optional, Dict, Any
import httpx

def set_proxy(url: Optional[str] = None):
    # httpx doesn't use a global proxy setting like 'request' in Node.js
    # Proxy should be passed to the client
    pass

def get_headers(url_str: str, options: Dict[str, Any], ctx: Optional[Any] = None, custom_header: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.facebook.com/",
        "Origin": "https://www.facebook.com",
        "User-Agent": options.get("userAgent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"),
        "Connection": "keep-alive",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if custom_header:
        headers.update(custom_header)
    if ctx:
        if hasattr(ctx, "region") and ctx.region:
            headers["X-MSGR-Region"] = ctx.region
        if hasattr(ctx, "user_id") and ctx.user_id:
            headers["av"] = ctx.user_id
    return headers

def generate_threading_id(client_id: str) -> str:
    k = int(time.time() * 1000)
    l_val = random.randint(0, 4294967295)
    return f"<{k}:{l_val}-{client_id}@mail.projektitan.com>"

def binary_to_decimal(data: str) -> str:
    if not data or data == "0":
        return "0"
    ret = ""
    curr_data = data
    while curr_data != "0" and curr_data:
        end = 0
        full_name = ""
        for char in curr_data:
            end = 2 * end + int(char)
            if end >= 10:
                full_name += "1"
                end -= 10
            else:
                full_name += "0"
        ret = f"{end}{ret}"
        first_one = full_name.find("1")
        curr_data = full_name[first_one:] if first_one != -1 else "0"
    return ret

def generate_offline_threading_id() -> str:
    ret = int(time.time() * 1000)
    value = random.randint(0, 4294967295)
    str_val = bin(value)[2:].zfill(22)
    msgs = str(bin(ret)[2:]) + str(str_val)
    return binary_to_decimal(msgs)

def get_guid() -> str:
    section_length = [int(time.time() * 1000)] # Use list for closure mutability
    def replace_char(match):
        r = int((section_length[0] + random.random() * 16) % 16)
        section_length[0] //= 16
        char = match.group(0)
        return hex(r if char == 'x' else (r & 7) | 8)[2:]
    
    return re.sub(r'[xy]', replace_char, "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx")

def format_id(f_id: Any) -> Optional[str]:
    if f_id is not None:
        return str(f_id).replace("fbid:", "").replace("id:", "")
    return None

def get_from(source: str, start: str, end: str) -> Optional[str]:
    try:
        a = source.index(start) + len(start)
        b = source.index(end, a)
        return source[a:b]
    except ValueError:
        return None

def parse_and_check_login(ctx: Any, response: httpx.Response) -> Any:
    # Basic implementation of parseAndCheckLogin
    try:
        data = response.text
        if data.startswith("for (;;);"):
            data = data[9:]
        return json.loads(data)
    except Exception:
        return None
