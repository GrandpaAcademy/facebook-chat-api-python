# Facebook Messenger Python SDK

A high-performance, asynchronous, and modular Python port of the Facebook Messenger (FCA) SDK. This SDK provides 100% feature parity with the popular Node.js implementation, supporting HTTP, GraphQL, and real-time MQTT protocols.

## ✨ Key Features

- **Async/Await Native**: Built from the ground up using `httpx` and `asyncio`.
- **Modular Design**: Separated into `core`, `http`, and `graphql` layers for maintainability.
- **Real-time MQTT**: High-speed message listening and actions (edit, react, block).
- **Comprehensive API**: Supports 70+ Messenger features including group management, stories, and polls.

## 🚀 Installation

Install the required dependencies:

```bash
pip install httpx beautifulsoup4 paho-mqtt npmlog
```

## 🔐 Authentication

The SDK supports both credential-based login and session-based (appstate) login via a simplified facade.

### Credential Login
```python
from fca import login

async def main():
    api = await login(email="your_email", password="your_password")
    # Your code here
```

### Appstate (Session) Login
Recommended to avoid frequent logins and checkpoints.
```python
from fca import login
import json

async def main():
    with open("appstate.json", "r") as f:
        app_state = json.load(f)
    api = await login(app_state=app_state)
```

## 🛠 Usage Examples

### Sending a basic message
```python
await api["sendMessage"]({"body": "Hello World!"}, "THREAD_ID")
```

### High-speed MQTT actions
If connected via MQTT, these actions are synchronized natively.
```python
await api["sendMessageMqtt"]({"body": "Fast Message"}, "THREAD_ID")
await api["editMessage"]("New Content", "MESSAGE_ID")
```

### Handling Events (MQTT)
```python
async def on_message(event):
    if event.get("type") == "message":
        print(f"New message: {event['body']}")

await api["listenMqtt"](on_message)
```

## 📚 API Reference

### Messaging
- `sendMessage`: Send standard messages (supports body, attachments, mentions).
- `sendMessageDM`: Alias for sending direct messages.
- `sendMessageMqtt`: Send message via MQTT for higher speed.
- `editMessage`: Edit a previously sent message (MQTT).
- `setMessageReaction`: Set a message reaction (GQL).
- `setMessageReactionMqtt`: Set reaction via MQTT.
- `unsendMessage`: Unsend a message.
- `deleteMessage`: Delete messages for the current user.

### Thread & Group Management
- `getThreadInfo`: Get detailed information about a thread.
- `getThreadList`: Fetch latest threads.
- `getThreadHistory`: Retrieve message history.
- `createNewGroup`: Create a new group chat.
- `changeGroupImage`: Update group avatar.
- `addUserToGroup` / `removeUserFromGroup`: Manage participants.
- `changeAdminStatus`: Set/unset group admins.
- `setTitle` / `changeNickname`: Update thread details.
- `changeThreadColor` / `changeThreadEmoji`: Customize styling.
- `muteThread` / `deleteThread`: Manage notifications and visibility.

### User & Social
- `getUserInfo`: Get user profile details.
- `getUID`: Resolve Facebook link/username to UID.
- `createNote` / `deleteNote`: Messenger Notes support.
- `createPoll`: Create polls in groups.
- `createPost` / `createCommentPost`: Interaction with Facebook posts.
- `setStoryReaction` / `setStorySeen`: Story interactions.
- `changeBio` / `changeName`: Profile customization.

## 🏗 Modular Architecture

The SDK is designed for maximum clarity and extensibility.

### Internal Layers
1. **`src.core.core`**: Handles session initialization, cookie parsing, and `revision` extraction. It builds the `Context` object shared by all services.
2. **`src.core.api`**: The assembly point. It maps modular service functions to the user-facing `api` dictionary.
3. **`src.http`**: Atomic implementations of standard Facebook web endpoints.
4. **`src.graphql`**: Complex data fetching using Facebook's GraphQL engine, includes response formatters in `src.graphql.formatter`.
5. **`src.core.mqtt`**: An event-driven client using `paho-mqtt` over WebSockets, optimized for real-time interaction.

### The `Context` Object
Most functions require a `ctx` object. This object holds:
- Active `httpx.AsyncClient`
- Current `fb_dtsg` token and `revision`
- User UID and ClientID
- MQTT Client instance (if connected)

## ✅ Contribution & Quality
This SDK is strictly linted and follows PEP 8.
- **Formatter**: `black`
- **Linter**: `ruff`, `flake8`

---
*Note: This is a port of the `ST-FCA` project. Ensure you comply with Meta's Terms of Service when using this SDK.*

## 📜 License

This project is licensed under the [MIT License](LICENSE).
