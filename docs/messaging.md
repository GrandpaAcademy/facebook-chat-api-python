# 💬 Messaging Guide

**fca-python** supports multiple messaging protocols (HTTP and MQTT) to provide both reliability and speed.

## 📝 Sending Messages

The primary way to send messages is through the `sendMessage` function.

```python
# Simple text
await api["sendMessage"]({"body": "Hello!"}, "THREAD_ID")

# With attachments
await api["sendMessage"]({
    "body": "Check this image",
    "attachment": open("image.jpg", "rb")
}, "THREAD_ID")

# With Mentions
await api["sendMessage"]({
    "body": "Hello @User",
    "mentions": [{
        "tag": "@User",
        "id": "USER_ID"
    }]
}, "THREAD_ID")
```

## 🚀 High-Speed MQTT Actions

MQTT is used for real-time bidirectional communication. It is significantly faster than standard HTTP requests for messaging.

```python
# Fast Message
await api["sendMessageMqtt"]({"body": "Instant reply"}, "THREAD_ID")

# Fast Reaction
await api["setMessageReactionMqtt"]("👍", "MESSAGE_ID")
```

## 🧹 Managing Messages

You can unsend or delete messages easily.

```python
# Unsend (removes for everyone)
await api["unsendMessage"]("MESSAGE_ID")

# Delete (removes only for you)
await api["deleteMessage"]("MESSAGE_ID")
```
筋
