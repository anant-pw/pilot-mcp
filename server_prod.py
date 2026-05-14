"""
Pilot MCP Server — Production (Railway)
========================================
Transport : SSE (Server-Sent Events) via Starlette
Deployment: Railway.app (free tier)
Tools     : get_weather, get_joke, get_fact
APIs      : All free, no API key needed.

How it differs from server.py (local):
- stdio  = pipe between Claude Desktop and your script (local only)
- SSE    = HTTP endpoint anyone on the internet can connect to
"""

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

# ── Server instance ────────────────────────────────────────────────────────────
mcp_server = Server("pilot-mcp")


# ── Tool definitions (identical to local version) ──────────────────────────────
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description=(
                "Get current weather for any city in the world. "
                "Use this when the user asks about weather, temperature, or climate of a place."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. Delhi, London, Tokyo"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_joke",
            description=(
                "Fetch a random programming joke. "
                "Use this when the user wants a joke, wants to laugh, or asks for something funny."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_fact",
            description=(
                "Fetch a random interesting fact about the world. "
                "Use this when the user wants to learn something new, asks for a fun fact, or is curious."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


# ── Tool execution (identical to local version) ────────────────────────────────
@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    async with httpx.AsyncClient(timeout=10) as client:

        if name == "get_weather":
            city = arguments.get("city", "London")
            response = await client.get(f"https://wttr.in/{city}?format=3")
            if response.status_code == 200:
                return [TextContent(
                    type="text",
                    text=f"🌤️ Weather Report\n\n{response.text.strip()}\n\n"
                         f"(Source: wttr.in — free, no API key)"
                )]
            return [TextContent(type="text", text=f"Could not fetch weather for '{city}'.")]

        elif name == "get_joke":
            response = await client.get(
                "https://icanhazdadjoke.com/",
                headers={"Accept": "application/json"}
            )
            if response.status_code == 200:
                joke = response.json().get("joke", "No joke found.")
                return [TextContent(
                    type="text",
                    text=f"😄 Random Joke\n\n{joke}\n\n"
                         f"(Source: icanhazdadjoke.com — free, no API key)"
                )]
            return [TextContent(type="text", text="Could not fetch a joke right now.")]

        elif name == "get_fact":
            response = await client.get(
                "https://uselessfacts.jsph.pl/api/v2/facts/random",
                headers={"Accept": "application/json"}
            )
            if response.status_code == 200:
                fact = response.json().get("text", "No fact found.")
                return [TextContent(
                    type="text",
                    text=f"🧠 Random Fact\n\n{fact}\n\n"
                         f"(Source: uselessfacts.jsph.pl — free, no API key)"
                )]
            return [TextContent(type="text", text="Could not fetch a fact right now.")]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ── SSE Transport setup ────────────────────────────────────────────────────────
# This is what makes it a web server instead of a local stdio pipe
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request) -> Response:
    """SSE endpoint — MCP clients connect here to discover and call tools."""
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options()
        )
    return Response()


# ── Health check ───────────────────────────────────────────────────────────────
async def health(request: Request) -> Response:
    """Railway uses this to confirm the server is alive."""
    return Response("pilot-mcp is running ✅", media_type="text/plain")


# ── Starlette app ──────────────────────────────────────────────────────────────
app = Starlette(
    routes=[
        Route("/", health),                        # health check
        Route("/health", health),                  # Railway health check
        Route("/sse", handle_sse),                 # MCP clients connect here
        Mount("/messages/", app=sse.handle_post_message),  # tool call responses
    ]
)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))  # Railway injects PORT automatically
    uvicorn.run(app, host="0.0.0.0", port=port)
