import asyncio
import json
import os
from fca_python import login

async def run_example():
    try:
        # Load AppState from appstate.json
        appstate_path = os.path.join(os.path.dirname(__file__), "appstate.json")
        with open(appstate_path, "r") as f:
            app_state = json.load(f)
            
        print("Logging in via AppState...")
        api = await login(app_state=app_state)
        print("Login successful!")

        user_id = api["getCurrentUserID"]()
        print(f"Logged in as ID: {user_id}")

        info = await api["getUserInfo"]([user_id])
        if user_id in info:
            print(f"Name: {info[user_id]['name']}")
        else:
            print(f"User info for {user_id} not found: {info}")

    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_example())
