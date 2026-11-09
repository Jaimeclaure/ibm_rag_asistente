"""MCP server exposing the local restaurant sample data."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context, FastMCP

from restaurant_project.data import RESTAURANTS

mcp = FastMCP(
    "Restaurant Data Server",
    instructions="Search fictional restaurant records for the local capstone demo.",
)


@mcp.tool()
def search_restaurants(query: str, limit: int = 3) -> str:
    """Search restaurants by name, cuisine, city, or description."""
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    terms = query.casefold().split()
    scored: list[tuple[int, dict[str, Any]]] = []
    for restaurant in RESTAURANTS:
        searchable = " ".join(str(value) for value in restaurant.values()).casefold()
        score = sum(term in searchable for term in terms)
        if score:
            scored.append((score, restaurant))
    scored.sort(key=lambda result: result[0], reverse=True)
    return json.dumps(
        [restaurant for _, restaurant in scored[:limit]],
        ensure_ascii=False,
    )


@mcp.tool()
async def verify_client_roots(ctx: Context) -> str:
    """Return the filesystem roots announced by the connected MCP client."""
    roots_result = await ctx.session.list_roots()
    roots = [
        {"name": root.name, "uri": str(root.uri)}
        for root in roots_result.roots
    ]
    return json.dumps(roots, ensure_ascii=False)


@mcp.resource("culinary://maps")
def culinary_maps() -> str:
    """A sample culinary map resource."""
    return json.dumps(
        {
            "Boston": ["Peruvian", "Indian"],
            "Cambridge": ["Mexican"],
        },
        ensure_ascii=False,
    )


@mcp.resource("data://restaurants")
def restaurant_data() -> str:
    """The fictional restaurant records available to this server."""
    return json.dumps(RESTAURANTS, ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
