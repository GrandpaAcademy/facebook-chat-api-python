from .src.core.core import login as core_login
from .src.core.api import get_api

async def login(email=None, password=None, app_state=None, options=None):
    """
    Simplified login interface for the Facebook Messenger SDK.
    Returns the API object directly.
    """
    return await core_login(app_state=app_state, email=email, password=password, options=options)

# Helper for those who might want to manually get the API from a context
get_fca_api = get_api
