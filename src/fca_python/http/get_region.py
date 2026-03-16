from typing import Any


def get_region(ctx: Any):
    return getattr(ctx, "region", None)
