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
                        "includeSeqID": True,
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

    # Handle both single object and list of objects
    if isinstance(res_data, dict):
        batch_results = [res_data]
    elif isinstance(res_data, list):
        batch_results = res_data
    else:
        batch_results = []

    threads = []
    if batch_results:
        message_threads = (
            batch_results[0]
            .get("o0", {})
            .get("data", {})
            .get("viewer", {})
            .get("message_threads", {})
        )
        
        # Extract irisSeqID/sync_id/sync_sequence_id if present
        sync_id = message_threads.get("sync_id") or message_threads.get("sync_sequence_id") or message_threads.get("irisSeqID")
        if sync_id:
            ctx.last_seq_id = str(sync_id)

        nodes = message_threads.get("nodes", [])
        if timestamp and nodes:
            nodes.pop(0)
        for node in nodes:
            threads.append(format_thread_graphql_response({"message_thread": node}))
    return threads
