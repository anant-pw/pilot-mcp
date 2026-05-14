"""
Pilot MCP Server — Weather + Joke + Fact
=========================================
Purpose : Teach what MCP is through 3 simple, real tools.
Transport: stdio (Claude Desktop compatible)
APIs     : All free, no API key needed.
"""

import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ── Server instance ────────────────────────────────────────────────────────────
app = Server("pilot-mcp")


# ── Tool definitions ───────────────────────────────────────────────────────────
@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    MCP calls this first — like a menu.
    Claude reads this list to know WHAT tools exist and WHEN to use them.
    """
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


# ── Tool execution ─────────────────────────────────────────────────────────────
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    MCP calls this when Claude decides to USE a tool.
    name      = which tool Claude picked
    arguments = what Claude extracted from the user's message
    """

    async with httpx.AsyncClient(timeout=10) as client:

        # ── Tool 1: Weather ────────────────────────────────────────────────────
        if name == "get_weather":
            city = arguments.get("city", "London")
            # wttr.in — free, no API key, returns plain text
            response = await client.get(
                f"https://wttr.in/{city}?format=3"
            )
            if response.status_code == 200:
                weather_text = response.text.strip()
                return [TextContent(
                    type="text",
                    text=f"🌤️ Weather Report\n\n{weather_text}\n\n"
                         f"(Source: wttr.in — free, no API key)"
                )]
            else:
                return [TextContent(type="text", text=f"Could not fetch weather for '{city}'.")]

        # ── Tool 2: Joke ───────────────────────────────────────────────────────
        elif name == "get_joke":
            # icanhazdadjoke — free, no API key
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
            else:
                return [TextContent(type="text", text="Could not fetch a joke right now.")]

        # ── Tool 3: Fact ───────────────────────────────────────────────────────
        elif name == "get_fact":
            # uselessfacts.net — free, no API key
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
            else:
                return [TextContent(type="text", text="Could not fetch a fact right now.")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Entry point ────────────────────────────────────────────────────────────────
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
