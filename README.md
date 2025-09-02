# MCP Agents

MCP-enabled agent service using [OpenAI’s Agents SDK](https://pypi.org/project/openai-agents/).

## Features
- OpenAI Agent + MCP server integration
- Filesystem MCP (sandboxed)
- FastAPI HTTP endpoint for other apps/projects
- `.env` for secrets (API keys, OAuth creds)

## Quickstart

```bash
git clone https://github.com/hanpinglim/mcp-agents.git
cd mcp-agents
py -3.12 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # add your keys
uvicorn app.serve:app --reload
