import time
import random
import json
import re
from typing import Optional, Dict, Any, List
import httpx
from urllib.parse import quote

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

def get_signature_id() -> str:
    return hex(random.randint(0, 2147483647))[2:]

PRESENCE_MAP = {
    "_": "%",
    "A": "%2",
    "B": "000",
    "C": "%7d",
    "D": "%7b%22",
    "E": "%2c%22",
    "F": "%22%3a",
    "G": "%2c%22ut%22%3a1",
    "H": "%2c%22bls%22%3a",
    "I": "%2c%22n%22%3a%22%",
    "J": "%22%3a%7b%22i%22%3a0%7d",
    "K": "%2c%22pt%22%3a0%2c%22vis%22%3a",
    "L": "%2c%22ch%22%3a%7b%22h%22%3a%22",
    "M": "%7b%22v%22%3a2%2c%22time%22%3a1",
    "N": ".channel%22%2c%22sub%22%3a%5b",
    "O": "%2c%22sb%22%3a1%2c%22t%22%3a%5b",
    "P": "%2c%22ud%22%3a100%2c%22lc%22%3a0",
    "Q": "%5d%2c%22f%22%3anull%2c%22uct%22%3a",
    "R": ".channel%22%2c%22sub%22%3a%5b1%5d",
    "S": "%22%2c%22m%22%3a0%7d%2c%7b%22i%22%3a",
    "T": "%2c%22blc%22%3a1%2c%22snd%22%3a1%2c%22ct%22%3a",
    "U": "%2c%22blc%22%3a0%2c%22snd%22%3a1%2c%22ct%22%3a",
    "V": "%2c%22blc%22%3a0%2c%22snd%22%3a0%2c%22ct%22%3a",
    "W": "%2c%22s%22%3a0%2c%22blo%22%3a0%7d%2c%22bl%22%3a%7b%22ac%22%3a",
    "X": "%2c%22ri%22%3a0%7d%2c%22state%22%3a%7b%22p%22%3a0%2c%22ut%22%3a1",
    "Y": "%2c%22pt%22%3a0%2c%22vis%22%3a1%2c%22bls%22%3a0%2c%22blc%22%3a0%2c%22snd%22%3a1%2c%22ct%22%3a",
    "Z": "%2c%22sb%22%3a1%2c%22t%22%3a%5b%5d%2c%22f%22%3anull%2c%22uct%22%3a0%2c%22s%22%3a0%2c%22blo%22%3a0%7d%2c%22bl%22%3a%7b%22ac%22%3a"
}

def presence_encode(str_val: str) -> str:
    encoded = quote(str_val)
    
    def manual_encode(match):
        m = match.group(0)
        if len(m) == 1:
            return f"%{ord(m):02x}"
        return m
    
    encoded = re.sub(r'([_A-Z])|%..', manual_encode, encoded).lower()
    
    keys = sorted(PRESENCE_MAP.values(), key=len, reverse=True)
    pattern = '|'.join(re.escape(k) for k in keys)
    inv_map = {v: k for k, v in PRESENCE_MAP.items()}
    
    def replace_map(match):
        return inv_map[match.group(0)]
    
    return re.sub(pattern, replace_map, encoded)

def generate_presence(user_id: str) -> str:
    now_ms = int(time.time() * 1000)
    state = {
        "v": 3,
        "time": now_ms // 1000,
        "user": user_id,
        "state": {
            "ut": 0,
            "t2": [],
            "lm2": None,
            "uct2": now_ms,
            "tr": None,
            "tw": random.randint(1, 4294967295),
            "at": now_ms
        },
        "ch": {
            f"p_{user_id}": 0
        }
    }
    return "E" + presence_encode(json.dumps(state))
