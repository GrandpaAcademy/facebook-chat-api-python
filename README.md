# ST-FCA Python SDK

A powerful Facebook Chat API (FCA) SDK ported from Node.js to Python.

## Project Structure

- **src/core/**: Core logic including login, API methods, and MQTT real-time listener.
- **src/utils/**: Shared utility functions for ID generation, headers, and presence encoding.
- **src/http/**: (Placeholder) Future home for dedicated HTTP service logic.
- **src/graphql/**: (Placeholder) Future home for GraphQL-specific logic.
- **docs/**: Project documentation and guides.

## Features

- [x] **Login**: Supports both `appState` (cookies) and email/password.
- [x] **Messaging**: Send messages, replies, and manage threads.
- [x] **Real-time**: MQTT listener for typing notifications and presence updates.
- [x] **Anti-Suspension**: Integrated presence heartbeats and robust session management.

## Installation

```bash
# Using uv (recommended)
uv build
uv sync
```

## Quick Start

```python
from src.core.core import login
import asyncio

async def main():
    # Login via appstate
    api = await login(app_state=your_app_state)
    
    # Send a message
    await api["sendMessage"]("Hello from ST-FCA Python!", thread_id="...")
    
    # Start MQTT listener
    def on_event(err, event):
        if event:
             print(f"Event: {event}")
             
    await api["listenMqtt"](on_event)

asyncio.run(main())
```

## Maintenance
Maintained & Enhanced by ST | Sheikh Tamim
