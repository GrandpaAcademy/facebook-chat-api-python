import asyncio
import json
from fca import login

async def main():
    """
    Example: Reliable Authentication
    Demonstrates how to login once with credentials and reuse the session 
    via appstate.json to avoid security checkpoints and blocks.
    """
    
    APPSTATE_FILE = "appstate.json"

    try:
        # 1. Try to login with AppState
        print("🔄 Attempting to login with session data...")
        with open(APPSTATE_FILE, "r") as f:
            app_state = json.load(f)
        
        api = await login(app_state=app_state)
        print("✅ Logged in successfully via AppState!")

    except (FileNotFoundError, Exception):
        # 2. Fallback to Credentials if AppState is missing or expired
        print("⚠️ AppState invalid or missing. Logging in with credentials...")
        
        email = "your-email@example.com"
        password = "your-password"
        
        api = await login(email=email, password=password)
        
        # 3. Save the new session data for future use
        new_appstate = api.getSession()
        with open(APPSTATE_FILE, "w") as f:
            json.dump(new_appstate, f, indent=2)
        
        print(f"✅ Session saved to {APPSTATE_FILE}")

    # 4. Perform an action to verify
    user_info = await api["getUserInfo"](api.getCurrentUserID())
    print(f"👋 Hello, {user_info[api.getCurrentUserID()]['name']}!")

if __name__ == "__main__":
    asyncio.run(main())

