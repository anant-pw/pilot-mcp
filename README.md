# 🧪 Pilot MCP — Learn MCP in 10 Minutes

> A minimal MCP server built to teach **what MCP is, how it works, and why it exists.**
> No paid tool APIs. No prior knowledge needed. Works locally and in production.

---

## What is MCP?

**MCP = Model Context Protocol**

A standard way for any LLM — accessed via Claude, Cline, Cursor, or your own app — to call real tools in the outside world.

```
Without MCP:
You → LLM → Answer (from training data or its own search)

With MCP:
You → LLM → [decides which tool to call] → MCP Server → Real data → LLM → Answer
```

The difference — with MCP, **you** define the tools, **you** own the server, **you** control the data source.

---

## What this server does

3 tools. That's it.

| Tool | What it does | API used |
|---|---|---|
| `get_weather` | Live weather for any city | wttr.in (free, no key) |
| `get_joke` | Random programming joke | icanhazdadjoke.com (free) |
| `get_fact` | Random fun fact | uselessfacts.jsph.pl (free) |

---

## MCP vs RAG (quick clarification)

| | RAG | MCP |
|---|---|---|
| What it gives LLM | Your documents (knowledge) | Real tools (actions) |
| Data type | Stored, static | Live, real-time |
| Can it act? | No — read only | Yes — read + write |
| Example | "Find our refund policy" | "Create a Jira ticket" |

> RAG = give LLM a library. MCP = give LLM a phone to call people with.
> Together = knowledge + action. That's the production pattern.

---

## Try it live — no local setup needed

The server is deployed on Railway. Add this to your **Cline MCP config**:

```json
{
  "mcpServers": {
    "pilot-mcp-live": {
      "type": "sse",
      "url": "https://pilot-mcp-production.up.railway.app/sse"
    }
  }
}
```

Then ask: `"What's the weather in Delhi?"`

If it doesn't trigger automatically, ask: `"What's the weather in Delhi using pilot-mcp-live tool?"`

---

## Local setup (5 minutes)

### Step 1 — Clone the repo
```bash
git clone https://github.com/anant-pw/pilot-mcp.git
cd pilot-mcp
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Configure Claude Desktop

Find the config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

> ⚠️ Windows users: if AppData is hidden → File Explorer → View → Show → Hidden items

Paste this (replace the path):
```json
{
  "mcpServers": {
    "pilot-mcp": {
      "command": "python",
      "args": ["C:\\Users\\yourname\\pilot-mcp\\server.py"]
    }
  }
}
```

> ⚠️ Windows: use double backslashes `\\` in the path

### Step 4 — Restart Claude Desktop
Fully quit (system tray → Quit), then reopen.
Look for the 🔨 hammer icon near the chat input — confirms MCP is connected.

### Step 5 — Test it
```
What's the weather in Delhi?
Tell me a joke
Give me a random fun fact
```

---

## Cline setup (VS Code)

Better for testing — shows tool calls transparently, no competing built-in tools.

1. Install **Cline** extension in VS Code (by saoudrizwan)
2. Get a free API key from [OpenRouter](https://openrouter.ai)
3. Cline settings → Provider: `OpenRouter` → Model: `google/gemini-2.0-flash-exp:free`
4. Open MCP settings → paste:

```json
{
  "mcpServers": {
    "pilot-mcp": {
      "command": "python",
      "args": ["D:\\your\\path\\to\\pilot-mcp\\server.py"]
    }
  }
}
```

---

## How it works (full flow)

```
You type: "What's the weather in Tokyo?"
                    │
                    ▼
         LLM reads your message
                    │
                    ▼
     LLM checks: do I have a tool for this?
     → YES: get_weather exists in this MCP server
                    │
                    ▼
     LLM calls: get_weather(city="Tokyo")
                    │
                    ▼
     MCP server hits: https://wttr.in/Tokyo?format=3
                    │
                    ▼
     Returns: "Tokyo: ⛅️ +22°C"
                    │
                    ▼
     LLM wraps it in a response to you
```

---

## File structure

```
pilot-mcp/
├── server.py          ← Local MCP server (stdio transport)
├── server_prod.py     ← Production MCP server (SSE transport)
├── Dockerfile         ← Docker container for Railway
├── railway.toml       ← Railway deployment config
├── requirements.txt   ← Python dependencies
└── README.md          ← This file
```

---

## Local vs Production

| | Local (`server.py`) | Production (`server_prod.py`) |
|---|---|---|
| Transport | stdio | SSE (HTTP) |
| Runs on | Your machine | Railway (cloud) |
| Who can use it | Only you | Anyone with the URL |
| Config | `command + args` | `type: sse + url` |

> **stdio** = walkie talkie — works only between two people near each other
> **SSE** = phone call — works from anywhere with the number (URL)

---

## Deploy your own to Railway (free)

1. Fork this repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your forked repo — Railway auto-detects the Dockerfile
4. Settings → Networking → Generate Domain
5. Update the URL in your MCP config to your new Railway domain

---

## Extend this — add a new tool in 3 steps

1. Add a `Tool(...)` entry in `list_tools()` in `server.py`
2. Add an `elif name == "your_tool":` block in `call_tool()`
3. Restart Claude Desktop / Cline

That's all MCP is. A list of tools + a handler. Everything else is the LLM's intelligence.

---

## Real QA use case (what this scales to)

The same MCP pattern — with real QA tools — closes the full testing loop:

```
→ Playwright  scrapes live app UI
→ Claude      generates pytest test cases
→ pytest      executes the suite
→ Allure      parses failures + stack traces
→ Jira        logs each failure as a bug ticket
```

One prompt. End to end. That's why MCP matters — not weather, not jokes. This.

---

## Stack

```
Python 3.11+    mcp SDK (Anthropic official)    httpx
Starlette       uvicorn (prod)                  Docker
```

---

## Honest note

Tool APIs (wttr.in, icanhazdadjoke, uselessfacts) — **free, no keys needed.**
LLM client (Claude Desktop, Cline) — needs an account. **Free tiers work fine.**

---

*Built as a learning pilot. Deployed in production. Pure MCP.*
