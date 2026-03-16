import json
from typing import Any, Optional, List
from ..utils.utils import parse_and_check_login
from .get_thread_info import format_thread_graphql_response


async def get_thread_list(
    post_func,
    ctx: Any,
    limit: int,
    timestamp: Optional[int] = None,
    tags: List[str] = [""],
):
    form = {
        "queries": json.dumps(
            {
                "o0": {
                    "doc_id": "3336396659757871",
                    "query_params": {
                        "limit": limit + (1 if timestamp else 0),
                        "before": timestamp,
                        "tags": tags,
                        "includeDeliveryReceipts": True,
                        "includeSeqID": False,
                    },
                }
            }
        ),
        "batch_name": "MessengerGraphQLThreadlistFetcher",
    }
    res = await post_func("https://www.facebook.com/api/graphqlbatch/", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        raise Exception("Failed to parse getThreadList response")
    threads = []
    if isinstance(res_data, list) and len(res_data) > 0:
        nodes = (
            res_data[0]
            .get("o0", {})
            .get("data", {})
            .get("viewer", {})
            .get("message_threads", {})
            .get("nodes", [])
        )
        if timestamp and nodes:
            nodes.pop(0)
        for node in nodes:
            threads.append(format_thread_graphql_response({"message_thread": node}))
    return threads
