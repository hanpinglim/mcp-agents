# app/serve.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent_service import run_once, ensure_mcp_connected

app = FastAPI(title="MCP Agents Service")

class RunRequest(BaseModel):
    input: str

class RunResponse(BaseModel):
    output: str

@app.on_event("startup")
async def _startup():
    # If there are MCP servers configured, connect them on startup (no-op otherwise)
    try:
        await ensure_mcp_connected()
    except Exception as e:
        # Don't crash the API if tools failed to connect; requests can still run
        print(f"[Startup] MCP connect warning: {e}")

@app.post("/run", response_model=RunResponse)
async def run_endpoint(req: RunRequest):
    try:
        out = await run_once(req.input)
        return RunResponse(output=out)
    except Exception as e:
        # Return a readable error instead of a raw 500 trace
        raise HTTPException(status_code=502, detail=f"Agent error: {e}")
