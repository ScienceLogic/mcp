import logging
from fastmcp.server.middleware import Middleware, MiddlewareContext
from mcp.types import CallToolRequestParams

logger = logging.getLogger(__name__)


class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP operations."""

    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""
        logger.debug(context)
        if isinstance(context.message, CallToolRequestParams):
            logger.info("Call is for tool %s with args: %s", context.message.name, context.message.arguments)
        else:
            logger.debug("Processing %s", context.method)

        result = await call_next(context)

        logger.debug("Completed %s", context.method)
        return result
