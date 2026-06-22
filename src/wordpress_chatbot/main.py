"""FastAPI server hosting Chainlit chat UI and FastMCP (SSE)."""

from __future__ import annotations

import uvicorn
from chainlit.utils import mount_chainlit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from wordpress_chatbot.mcp.server import mcp

app = FastAPI(title="WordPress Insights Chat", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/mcp")
async def mcp_root():
    """Redirect bare /mcp to the SSE endpoint."""
    return RedirectResponse(url="/mcp/sse")


# Mount MCP SSE
app.mount("/mcp", mcp.sse_app())

# Mount Chainlit at root
mount_chainlit(app=app, target="src/wordpress_chatbot/chat.py", path="/")

if __name__ == "__main__":
    uvicorn.run("wordpress_chatbot.main:app", host="0.0.0.0", port=8000, reload=True)
