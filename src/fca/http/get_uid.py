import httpx


async def get_uid(link: str):
    async def get_uid_fast(url: str):
        form = {"link": url}
        async with httpx.AsyncClient() as client:
            res = await client.post("https://id.traodoisub.com/api.php", data=form)
            data = res.json()
            if data.get("error"):
                raise Exception(data["error"])
            return data.get("id", "Not found")

    async def get_uid_slow(url: str):
        # This uses a different service, sometimes needed
        form = {"username": url.split("/")[-1]}  # Simplified
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.findids.net/api/get-uid-from-username", data=form
            )
            data = res.json()
            if data.get("status") != 200:
                raise Exception("Error occurred!")
            return data.get("data", {}).get("id", "Not found")

    try:
        uid = await get_uid_fast(link)
        if uid and uid != "Not found":
            return uid
        return await get_uid_slow(link)
    except Exception:
        return None
