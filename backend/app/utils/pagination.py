"""
Shared pagination parsing for list endpoints.
"""

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def parse_pagination(args):
    try:
        page = max(1, int(args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1

    try:
        limit = int(args.get("limit", DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        limit = DEFAULT_PAGE_SIZE

    limit = max(1, min(limit, MAX_PAGE_SIZE))
    skip = (page - 1) * limit
    return page, limit, skip