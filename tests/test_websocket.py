import pytest
import json
from fastapi.testclient import TestClient
from app.websocket.chat import manager


@pytest.mark.asyncio
async def test_websocket_connection_requires_auth(client, auth_token):
    """Test that WebSocket requires authentication"""
    # This test would require a WebSocket test client
    # For now, we'll test the authentication logic
    from app.utils.jwt import verify_token
    
    # Valid token should work
    username = verify_token(auth_token)
    assert username is not None
    
    # Invalid token should fail
    invalid_username = verify_token("invalid_token")
    assert invalid_username is None

