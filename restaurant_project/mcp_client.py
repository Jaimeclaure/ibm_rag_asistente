"""MCP client that verifies tools, resources, search, and configured roots."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_TOOLS = {"search_restaurants", "verify_client_roots"}


async def configured_roots(_: Any) -> types.ListRootsResult:
    return types.ListRootsResult(
        roots=[
            types.Root(
                uri=PROJECT_ROOT.as_uri(),
                name="Restaurant RAG project",
            )
        ]
    )


def first_text(result: Any) -> str:
    for item in result.content:
        if isinstance(item, types.TextContent):
            return item.text
    raise RuntimeError("The MCP tool response did not contain text content.")


async def main() -> None:
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "restaurant_project.mcp_server"],
    )
    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream,
            list_roots_callback=configured_roots,
        ) as session:
            await session.initialize()
            discovered_tools = await session.list_tools()
            tool_names = {tool.name for tool in discovered_tools.tools}
            missing_tools = REQUIRED_TOOLS - tool_names
            if missing_tools:
                raise RuntimeError(f"Required MCP tools missing: {sorted(missing_tools)}")
            print(f"Operational tools verified: {', '.join(sorted(REQUIRED_TOOLS))}")

            resources = await session.list_resources()
            resource_uris = {str(resource.uri) for resource in resources.resources}
            print(f"Available resources: {', '.join(sorted(resource_uris))}")
            if not resource_uris:
                raise RuntimeError("The MCP server did not expose any resources.")

            search_result = await session.call_tool(
                "search_restaurants",
                {"query": "Peruvian Boston", "limit": 2},
            )
            restaurants = json.loads(first_text(search_result))
            if not restaurants:
                raise RuntimeError("The MCP search query returned no restaurant results.")
            print("Successful search query result:")
            print(json.dumps(restaurants, ensure_ascii=False, indent=2))

            roots_result = await session.call_tool("verify_client_roots")
            roots = json.loads(first_text(roots_result))
            root_uris = {root["uri"] for root in roots}
            expected_root = PROJECT_ROOT.as_uri()
            if expected_root not in root_uris:
                raise RuntimeError(
                    f"Configured project root {expected_root!r} was not received "
                    f"by the server; received {sorted(root_uris)}."
                )
            print(f"Configured project root verified: {expected_root}")


if __name__ == "__main__":
    asyncio.run(main())
