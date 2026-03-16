import asyncio
import os
from fca_python.core import login

async def main():
    # This is a dummy test to see if imports and basic logic work
    # In a real scenario, you'd provide actual app_state or email/pass
    print("Testing fca_python SDK...")
    try:
        # We expect this to fail because we're not providing credentials,
        # but it should fail at the network/parsing stage, not import stage.
        api = await login(email="test@example.com", password="password")
        print("Login successful (unexpected without real credentials)")
    except Exception as e:
        print(f"Caught expected error or login failure: {e}")

if __name__ == "__main__":
    asyncio.run(main())
