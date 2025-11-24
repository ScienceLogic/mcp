
import pytest
from unittest.mock import patch
from mcp_sl.http_client import HTTPClient, HTTPMethod
import httpx

@pytest.mark.asyncio
async def test_http_client_get_success():
    """Test successful GET request"""
    client = HTTPClient(
        base_url="https://example.com",
        headers={"Authorization": "Custom my-test-key"},
    )
    
    with patch.object(client, '_request', return_value={"test": "data"}) as mock_request:
        result = await client.get("some/endpoint", params={"limit": 10})
        
        mock_request.assert_called_once_with(
            HTTPMethod.GET,
            "some/endpoint", 
            params={"limit": 10}
        )
        assert result == {"test": "data"}

        # Verify the auth header is constructed correctly
        expected_header = "Custom my-test-key"
        assert client.headers["Authorization"] == expected_header
    

@pytest.mark.asyncio
async def test_http_client_error_handling():
    """Test HTTP error responses are handled properly"""
    client = HTTPClient(
        base_url="https://example.com",
        headers={"Authorization": "Custom my-test-key"},
    )

    with patch.object(client, '_request', side_effect=httpx.HTTPStatusError("404", request=None, response=None)):
        with pytest.raises(httpx.HTTPStatusError):
            await client.get("v2/nonexistent")
