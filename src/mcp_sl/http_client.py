
"""
HTTP Client Module for ScienceLogic APIs

This module provides a comprehensive HTTP client for interacting with the downstream APIs.
It handles authentication, request/response processing, and provides a clean async interface
for all HTTP operations required by the MCP server.

The client supports all standard HTTP methods and automatically handles:
- API authentication via custom headers
- JSON request/response serialization
- Error handling and status code validation

Example:
    >>> client = HTTPClient()
    >>> devices = await client.get("v2/devices", params={"limit": 10})
    >>> backup_result = await client.post("v2/devices/123/backup", json_data={"name": "manual_backup"})
"""
from enum import Enum
from typing import Dict, Any, Optional
from httpx import AsyncClient, Response
from mcp_sl.config import get_config


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class HTTPClient:
    def __init__(self, base_url: str, headers: dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request(HTTPMethod.GET, endpoint, params=params)

    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request(HTTPMethod.DELETE, endpoint, params=params)

    async def post(self, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request(HTTPMethod.POST, endpoint, params=params, json_data=json_data)

    async def put(self, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request(HTTPMethod.PUT, endpoint, params=params, json_data=json_data)

    async def patch(self, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request(HTTPMethod.PATCH, endpoint, params=params, json_data=json_data)

    async def _request(
        self,
        method: HTTPMethod,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        async with AsyncClient(verify=False, timeout=get_config().TOOL_TIMEOUT_MS) as client:
            if method == HTTPMethod.GET:
                response: Response = await client.get(url, headers=self.headers, params=params)
            elif method == HTTPMethod.DELETE:
                response: Response = await client.delete(url, headers=self.headers, params=params)
            elif method == HTTPMethod.POST:
                response: Response = await client.post(url, headers=self.headers, params=params, json=json_data)
            elif method == HTTPMethod.PUT:
                response: Response = await client.put(url, headers=self.headers, params=params, json=json_data)
            elif method == HTTPMethod.PATCH:
                response: Response = await client.patch(url, headers=self.headers, params=params, json=json_data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method.value}")

            response.raise_for_status()
            return response.json()
