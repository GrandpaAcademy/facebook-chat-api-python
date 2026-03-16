# 🔐 Authentication Guide

Security is the most important part of interacting with Facebook's API. Frequent logins with email/password can trigger security checkpoints or temporary bans.

## 📦 AppState (Highly Recommended)

The `AppState` is an array of cookies that represents an active session. Using it allows you to bypass the login phase entirely.

### How to obtain AppState
You can use browser extensions (like "EditThisCookie" or "c3c-fbstate") to export your Facebook cookies in JSON format. Alternatively, `fca-python` generates this automatically upon a successful credential login.

### Using AppState
```python
from fca import login
import json

with open("appstate.json", "r") as f:
    state = json.load(f)

api = await login(app_state=state)
```

## 📧 Credential Login

If you don't have an AppState, you can login with your email and password.

```python
api = await login(email="...", password="...")
```

> [!WARNING]
> If your account has **Two-Factor Authentication (2FA)** enabled, you must provide the 2FA code if prompted, or use an AppState generated from a browser where you've already authenticated.

## 💾 Saving the Session

After logging in with credentials, always save the session to avoid logging in again next time.

```python
session = api.getSession()
with open("appstate.json", "w") as f:
    json.dump(session, f)
```
筋
