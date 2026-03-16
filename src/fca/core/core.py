import httpx
from bs4 import BeautifulSoup
import logging
import re
import random
from typing import Dict, Any, Optional, List

from ..utils.utils import get_headers

logger = logging.getLogger("fca_python")


class Context:
    def __init__(
        self,
        user_id: str,
        client_id: str,
        options: Dict[str, Any],
        client: httpx.AsyncClient,
    ):
        self.user_id: str = user_id
        self.client_id: str = client_id
        self.options: Dict[str, Any] = options
        self.client: httpx.AsyncClient = client
        self.jar: httpx.Cookies = client.cookies
        self.fb_dtsg: Optional[str] = None
        self.revision: Optional[str] = None
        self.req_counter: int = 1
        self.region: str = "PNB"
        self.mqtt_endpoint: Optional[str] = None
        self.sync_token: Optional[str] = None
        self.last_seq_id: Optional[str] = None
        self.logged_in: bool = True
        self.client_mutation_id: int = 0
        self.req_id: int = 0
        self.ws_req_number: int = 0
        self.ws_task_number: int = 0


async def build_api(
    global_options: Dict[str, Any], html: str, client: httpx.AsyncClient
):
    fb_dtsg = None
    iris_seq_id = None

    # Try multiple DTSG patterns
    patterns = [
        r'\["DTSGInitialData",\[\],{"token":"([^"]+)"}\]',
        r'\["DTSGInitData",\[\],{"token":"([^"]+)"',
        r'"token":"([^"]+)"',
        r'{\\"token\\":\\"([^"\\]+)\\"',
        r',\{"token":"([^"]+)"\},\d+\]',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            fb_dtsg = match.group(1)
            break

    if not fb_dtsg:
        soup = BeautifulSoup(html, "html.parser")
        dtsg_input = soup.find("input", {"name": "fb_dtsg"})
        if dtsg_input:
            fb_dtsg = dtsg_input.get("value")

    seq_match = re.search(r'irisSeqID":"([^"]+)"', html)
    if seq_match:
        iris_seq_id = seq_match.group(1)

    revision_match = re.search(r'revision":(\d+),', html)
    if not revision_match:
        revision_match = re.search(r'client_revision":(\d+),', html)

    revision = revision_match.group(1) if revision_match else "103"

    # Robust User ID extraction from cookies
    user_id = None
    for key in ["c_user", "i_user"]:
        if key in client.cookies:
            user_id = client.cookies[key]
            break

    if not user_id or user_id == "0":
        user_id_match = re.search(r'"USER_ID":"(\d+)"', html)
        if user_id_match and user_id_match.group(1) != "0":
            user_id = user_id_match.group(1)

    if not user_id or user_id == "0":
        # Check for another pattern often found in JS
        user_id_match = re.search(
            r'\["CurrentUserInitialData",\[\],{"USER_ID":"(\d+)"}', html
        )
        if user_id_match and user_id_match.group(1) != "0":
            user_id = user_id_match.group(1)

    if not user_id or user_id == "0":
        raise Exception("Login failed: User ID not found or invalid (0).")

    client_id = hex(random.getrandbits(31))[2:]

    mqtt_endpoint = f"wss://edge-chat.facebook.com/chat?region=pnb&sid={user_id}"
    region = "PNB"

    endpoint_match = re.search(r'"endpoint":"([^"]+)"', html)
    if endpoint_match:
        mqtt_endpoint = endpoint_match.group(1).replace("\\/", "/")
        try:
            from urllib.parse import urlparse, parse_qs

            parsed_url = urlparse(mqtt_endpoint)
            region_list = parse_qs(parsed_url.query).get("region")
            if region_list:
                region = region_list[0].upper()
        except Exception:
            pass

    ctx = Context(user_id, client_id, global_options, client)
    ctx.fb_dtsg = fb_dtsg
    ctx.revision = revision
    ctx.last_seq_id = iris_seq_id
    ctx.mqtt_endpoint = mqtt_endpoint
    ctx.region = region

    from .api import get_api, get_thread_list

    if not ctx.last_seq_id:
        try:
            # Try to fetch seq_id via GraphQL if not in HTML
            await get_thread_list(ctx, 1, tags=["INBOX"])
            # The get_thread_list implementation should ideally store the seq_id in the ctx
            # or we need to modify it to return it.
            # Actually, standard FCA fetches it from a separate doc_id if needed.
            # Let's assume for now irisSeqID was there or we'll fetch it explicitly if needed.
            pass
        except Exception:
            pass

    api = get_api(ctx)
    return ctx, api


async def handle_redirect(
    res: httpx.Response, client: httpx.AsyncClient, global_options: Dict[str, Any]
) -> httpx.Response:
    if res.status_code in (301, 302, 303, 307, 308) and "Location" in res.headers:
        redirect_url = res.headers["Location"]
        if redirect_url.startswith("/"):
            redirect_url = "https://www.facebook.com" + redirect_url
        res = await client.get(
            redirect_url, headers=get_headers(redirect_url, global_options)
        )
        return await handle_redirect(res, client, global_options)

    reg = r'<meta http-equiv="refresh" content="0;url=([^"]+)[^>]+>'
    match = re.search(reg, res.text)
    if match:
        redirect_url = match.group(1).replace("&amp;", "&")
        if redirect_url.startswith("/"):
            redirect_url = "https://www.facebook.com" + redirect_url
        res = await client.get(
            redirect_url, headers=get_headers(redirect_url, global_options)
        )
        return await handle_redirect(res, client, global_options)

    return res


async def make_login(
    client: httpx.AsyncClient, email: str, password: str, global_options: Dict[str, Any]
) -> httpx.Response:
    login_url = "https://www.facebook.com/login/device-based/regular/login/"
    form = {
        "email": email,
        "pass": password,
        "lsd": None,
        "default_persistent": "0",
        "timezone": "-420",
        "lgndim": "",
        "lgnjs": "n",
        "lgnvv": "1",
        "next": "https://www.facebook.com/",
    }

    res = await client.get(
        "https://www.facebook.com/",
        headers=get_headers("https://www.facebook.com/", global_options),
    )
    res = await handle_redirect(res, client, global_options)

    lsd_match = re.search(r'name="lsd" value="([^"]+)"', res.text)
    if lsd_match:
        form["lsd"] = lsd_match.group(1)

    res = await client.post(
        login_url, data=form, headers=get_headers(login_url, global_options)
    )
    return await handle_redirect(res, client, global_options)


async def login(
    app_state: Optional[List[Dict[str, Any]]] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
):
    global_options = {
        "selfListen": False,
        "listenEvents": True,
        "listenTyping": False,
        "updatePresence": False,
        "forceLogin": False,
        "autoMarkDelivery": False,
        "autoMarkRead": False,
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    if options:
        global_options.update(options)

    jar = httpx.Cookies()
    if app_state:
        for cookie in app_state:
            key = cookie.get("key") or cookie.get("name")
            value = cookie.get("value")
            domain = cookie.get("domain", "facebook.com")
            path = cookie.get("path", "/")
            if key and value:
                jar.set(key, str(value), domain=domain, path=path)

    client = httpx.AsyncClient(cookies=jar, follow_redirects=False, timeout=60.0)
    try:
        if email and password:
            res = await make_login(client, email, password, global_options)
        else:
            res = await client.get(
                "https://www.facebook.com/",
                headers=get_headers("https://www.facebook.com/", global_options),
            )
            res = await handle_redirect(res, client, global_options)

        if not res or not res.text:
            res = await client.get(
                "https://www.facebook.com/messages",
                headers=get_headers(
                    "https://www.facebook.com/messages", global_options
                ),
            )
            res = await handle_redirect(res, client, global_options)

        build_res = await build_api(global_options, res.text if res else "", client)
        ctx, api = build_res
        return api
    except Exception:
        await client.aclose()
        raise
