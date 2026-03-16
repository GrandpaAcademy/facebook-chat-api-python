from src.core.core import login
import asyncio
import json
import os

async def main():
    """
    Main entry point for testing the SDK.
    """
    print("ST-FCA Python SDK Loading...")
    
    # Example usage (requires appstate.json)
    if os.path.exists("appstate.json"):
        with open("appstate.json", "r") as f:
            app_state = json.load(f)
        
        try:
            api = await login(app_state=app_state)
            print(f"Logged in as: {api['getCurrentUserID']()}")
        except Exception as e:
            print(f"Login failed: {e}")
    else:
        print("appstate.json not found. Please provide one to test the connection.")

if __name__ == "__main__":
    asyncio.run(main())
