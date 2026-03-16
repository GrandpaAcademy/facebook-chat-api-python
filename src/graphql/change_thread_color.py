import json
from typing import Any
from ..utils.utils import parse_and_check_login

async def change_thread_color(post_func, ctx: Any, color: str, thread_id: str):
    validated_color = color.lower() if color else None
    
    form = {
        "dpr": 1,
        "queries": json.dumps({
            "o0": {
                "doc_id": "1727493033983591",
                "query_params": {
                    "data": {
                        "actor_id": ctx.user_id,
                        "client_mutation_id": "0",
                        "source": "SETTINGS",
                        "theme_id": validated_color,
                        "thread_id": thread_id,
                    },
                },
            },
        }),
    }
    
    res = await post_func("https://www.facebook.com/api/graphqlbatch/", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data or not isinstance(res_data, list):
        raise Exception("Failed to parse changeThreadColor response")
        
    if res_data[-1].get("error_results", 0) > 0:
        raise Exception(f"Error changing thread color: {res_data[0].get('o0', {}).get('errors')}")
        
    return res_data
