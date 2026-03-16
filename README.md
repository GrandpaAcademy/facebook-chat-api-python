# fca-python: Facebook Messenger Async SDK 🚀

[![PyPI version](https://img.shields.io/pypi/v/fca-python.svg?color=blue)](https://pypi.org/project/fca-python/)
[![Python versions](https://img.shields.io/pypi/pyversions/fca-python.svg)](https://pypi.org/project/fca-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/GrandpaAcademy/facebook-chat-api-python/graphs/commit-activity)

**fca-python** is a high-performance, asynchronous, and modular Python SDK for Facebook Messenger. Engineered for speed and reliability, it provides 100% feature parity with the popular Node.js FCA implementation while leveraging Python's modern `asyncio` ecosystem.

---

## 🔝 Key Advantages

*   **⚡ Extreme Performance**: Built on `httpx` and `paho-mqtt` for non-blocking I/O.
*   **🧩 Modular Architecture**: Cleanly separated into Core, HTTP, GraphQL, and MQTT layers.
*   **📡 Real-time Synchronization**: Native MQTT support for instant message listening and high-speed actions.
*   **🛠️ Feature Rich**: 70+ functions covering messaging, group management, stories, and polls.
*   **🛡️ Privacy First**: Secure session handling and automated privacy scrubbing.

---

## 🚀 Quick Start

### 1. Installation
Install the SDK via pip:
```bash
pip install fca-python
```

### 2. Basic Setup
The SDK provides a simplified facade for instant productivity.

```python
import asyncio
from fca import login

async def main():
    # Authenticate via Email/Password or AppState (Recommended)
    api = await login(email="your_email", password="your_password")
    
    # Send a simple message
    await api["sendMessage"]({"body": "Hello from fca-python!"}, "THREAD_ID")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. High-Speed MQTT Usage
For real-time applications, use the integrated MQTT listener:

```python
async def on_message(event):
    if event.get("type") == "message":
        print(f"📩 New message: {event['body']}")

await api["listenMqtt"](on_message)
```

---

## 📚 API Capabilities

| Category | Supported Features |
| :--- | :--- |
| **Messaging** | `sendMessage`, `editMessage`, `unsendMessage`, `setMessageReaction`, `forwardAttachment` |
| **Groups** | `createNewGroup`, `changeGroupImage`, `addUserToGroup`, `removeUserFromGroup`, `changeAdminStatus` |
| **User Profile** | `getUserInfo`, `getUID`, `changeName`, `changeBio`, `changeUsername`, `setProfileLock` |
| **Social** | `createPoll`, `createPost`, `setStoryReaction`, `handleFriendRequest`, `createNote` |
| **Maintenance** | `getThreadList`, `deleteThread`, `muteThread`, `markAsSeen`, `getThreadHistory` |

---

## 🏗️ Architecture Deep Dive

The SDK is organized into logical layers to ensure maximum extensibility:
1.  **Core**: Authentication, session management, and API factory.
2.  **HTTP**: Native Facebook web endpoint implementations.
3.  **GraphQL**: High-level data queries using the Facebook GQL engine.
4.  **MQTT**: Event-driven WebSocket client for real-time interaction.

---

## ⚖️ License & Disclaimer

This project is licensed under the **MIT License**.

> [!IMPORTANT]
> This is a port of the `ST-FCA` project. This software is provided **as-is**, without any warranty or guarantee of maintenance. The author is not responsible for any illegal usage. Use responsibly and comply with Meta's Terms of Service.

---
Built with ❤️ for the Python community.
