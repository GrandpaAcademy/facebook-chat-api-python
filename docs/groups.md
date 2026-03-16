# 👥 Group Management

The SDK provides comprehensive tools for managing group threads using Facebook's GraphQL engine.

## 🏗️ Creating Groups

You can create a new group by providing a list of participant IDs and an optional title.

```python
# Create a group with 3 users
thread_id = await api["createNewGroup"](["ID1", "ID2", "ID3"], "Dev Team")
```

## 🖼️ Customization

```python
# Change group name
await api["setTitle"]("New Group Name", "THREAD_ID")

# Change group image
await api["changeGroupImage"](open("group_pic.png", "rb"), "THREAD_ID")

# Change thread color/theme
await api["changeThreadColor"]("COLOR_ID", "THREAD_ID")
```

## 👥 Participant Management

```python
# Add user
await api["addUserToGroup"]("USER_ID", "THREAD_ID")

# Kick user
await api["removeUserFromGroup"]("USER_ID", "THREAD_ID")

# Promote to Admin
await api["changeAdminStatus"]("USER_ID", True, "THREAD_ID")
```

