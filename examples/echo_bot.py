import asyncio
import json
import os
from fca import login

async def main():
    """
    Example: Basic Echo Bot
    This bot listens for incoming messages and replies with the same text.
    """
    
    # 1. Login (Using appstate.json for stability)
    if os.path.exists("appstate.json"):
        with open("appstate.json", "r") as f:
            app_state = json.load(f)
        api = await login(app_state=app_state)
    else:
        # Fallback to credentials if appstate doesn't exist
        email = input("Email: ")
        password = input("Password: ")
        api = await login(email=email, password=password)
        # Save appstate for next time
        with open("appstate.json", "w") as f:
            json.dump(api.getSession(), f)

    print("🤖 Echo Bot is running! Press Ctrl+C to stop.")

    # 2. Define the Message Listener
    async def listener(event):
        # We only care about incoming messages
        if event.get("type") == "message" and event.get("body"):
            print(f"📩 Received: {event['body']} from {event['senderID']}")
            
            # 3. Echo the message back
            await api["sendMessage"](
                {"body": f"Echo: {event['body']}"}, 
                event["threadID"]
            )

    # 4. Start Listening
    await api["listenMqtt"](listener)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
筋
