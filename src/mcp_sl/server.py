"""
ScienceLogic MCP Server

This module sets up the main FastMCP server for the ScienceLogic.
The server provides paths for all sub MCP servers, currently:
* Skylar One MCP
* Skylar Compliance MCP

The server is configured to run with uvicorn and provides HTTP endpoints
for MCP client interactions.
"""

import logging
from contextlib import asynccontextmanager, AsyncExitStack
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp_sl.config import get_config
from mcp_sl.middleware import LoggingMiddleware, StripUnknownArgumentsMiddleware
from mcp_sl.skylar_compliance.apis import sky_comp_mcp
from mcp_sl.skylar_one.apis import sky_one_mcp

# Configure logging
logging.basicConfig(
    level=get_config().LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
cfg = get_config()

# Build routes and lifespan entries based on config
routes = []
apps_for_lifespan = []

if cfg.SKY_COMP_ENABLE:
    logger.info("Starting Skylar Compliance MCP server on /sky_comp/mcp")
    sky_comp_mcp.add_middleware(StripUnknownArgumentsMiddleware())
    sky_comp_mcp.add_middleware(LoggingMiddleware())
    rp_app = sky_comp_mcp.http_app()
    routes.append(Mount("/sky_comp", rp_app))
    apps_for_lifespan.append(rp_app)

if cfg.SKY_ONE_ENABLE:
    logger.info("Starting Skylar One MCP server on /sky_one/mcp")
    sky_one_mcp.add_middleware(StripUnknownArgumentsMiddleware())
    sky_one_mcp.add_middleware(LoggingMiddleware())
    sky_one_app = sky_one_mcp.http_app()
    routes.append(Mount("/sky_one", sky_one_app))
    apps_for_lifespan.append(sky_one_app)


@asynccontextmanager
async def lifespan(parent_app):
    async with AsyncExitStack() as stack:
        for sub_app in apps_for_lifespan:
            await stack.enter_async_context(sub_app.lifespan(parent_app))
        yield

app = Starlette(
    routes=routes,
    lifespan=lifespan,
)
