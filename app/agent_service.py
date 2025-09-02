# app/agent_service.py
import os
import asyncio
from agents import Agent, Runner, set_default_openai_key
from agents.mcp import MCPServerStdio

# --- Load env ---------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_STUB = os.getenv("USE_STUB", "0") == "1"            # if 1, bypass OpenAI calls
USE_FS_MCP = os.getenv("USE_FS_MCP", "0") == "1"        # if 1, mount filesystem MCP
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")     # cheap default

if not USE_STUB:
    if not OPENAI_API_KEY:
        # Not fatal at import-time, but real runs will fail; warn explicitly:
        print("WARNING: OPENAI_API_KEY is not set and USE_STUB=0. Calls will fail.")
    else:
        set_default_openai_key(OPENAI_API_KEY)

# --- Configure MCP servers (optional) ---------------------------------------
mcp_servers = []
if USE_FS_MCP:
    SAMPLE_ROOT = os.path.abspath("./sandbox")
    os.makedirs(SAMPLE_ROOT, exist_ok=True)
    filesystem_server = MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", SAMPLE_ROOT],
        }
    )
    mcp_servers.append(filesystem_server)

# --- Build the Agent --------------------------------------------------------
agent = Agent(
    name="WorkspaceAgent",
    instructions=(
        "You are a helpful, careful assistant. "
        "Use tools when useful. Ask before destructive actions."
    ),
    model=MODEL_NAME,              # <- force a cheaper model by default
    mcp_servers=mcp_servers,
)

# --- Ensure MCP connects once ----------------------------------------------
_mcp_connected = False
_mcp_lock = asyncio.Lock()

async def ensure_mcp_connected():
    """Connect MCP servers once; skip if none configured."""
    global _mcp_connected
    if _mcp_connected or not agent.mcp_servers:
        return
    async with _mcp_lock:
        if _mcp_connected:
            return
        for srv in agent.mcp_servers:
            try:
                await srv.connect()
            except Exception as e:
                # Surface connection issues in logs
                print(f"[MCP] connect failed: {e}")
                raise
        _mcp_connected = True
        print("MCP servers connected.")

# --- Single-run entrypoint used by FastAPI ----------------------------------
async def run_once(user_input: str) -> str:
    # Stub mode: return immediately (good for local testing with no credits)
    if USE_STUB:
        return f"[STUB:{MODEL_NAME}] You said: {user_input}"

    # Connect MCP if any enabled
    if agent.mcp_servers:
        await ensure_mcp_connected()

    # Call the agent loop
    result = await Runner.run(agent, user_input)
    return result.final_output or "[No output]"
