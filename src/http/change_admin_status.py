from typing import Any, List, Union
from ..utils.utils import parse_and_check_login

async def change_admin_status(post_func, ctx: Any, thread_id: str, admin_ids: Union[str, List[str]], admin_status: bool):
    if isinstance(admin_ids, str):
        admin_ids = [admin_ids]
        
    form = {
        "thread_fbid": thread_id,
        "add": "true" if admin_status else "false"
    }
    
    for i, u_id in enumerate(admin_ids):
        form[f"admin_ids[{i}]"] = u_id
        
    res = await post_func("https://www.facebook.com/messaging/save_admins/?dpr=1", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        raise Exception("Failed to change admin status.")
        
    if res_data.get("error"):
        error_code = res_data["error"]
        if error_code == 1976004:
            raise Exception("Cannot alter admin status: you are not an admin.")
        elif error_code == 1357031:
            raise Exception("Cannot alter admin status: this thread is not a group chat.")
        else:
            raise Exception(f"Cannot alter admin status: unknown error code {error_code}.")
            
    return res_data
