from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from app.apis import deps
from app.models.user import Status, UserStatus


def make_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 12345),
            "scheme": "http",
        }
    )


class FakeTokenQuery:
    def __init__(self, token_obj):
        self.token_obj = token_obj

    def select_related(self, *fields):
        assert fields == ("user",)
        return self

    async def first(self):
        return self.token_obj


class FakeUser:
    def __init__(self, status=UserStatus.NORMAL):
        self.id = "12345678-1234-1234-1234-123456789012"
        self.email = "api@example.com"
        self.nickname = "api-user"
        self.status = status
        self.roles = []

    async def fetch_related(self, relation):
        assert relation == "roles"
        self.roles = [SimpleNamespace(code="GM")]


@pytest.mark.asyncio
async def test_api_token_authentication_returns_user_and_roles(monkeypatch):
    user = FakeUser()
    token_obj = SimpleNamespace(user=user)

    def fake_filter(**kwargs):
        assert kwargs == {"token": "api-token", "status": Status.OK}
        return FakeTokenQuery(token_obj)

    monkeypatch.setattr(deps.UserToken, "filter", fake_filter)
    request = make_request()

    result = await deps.get_current_user_or_token(
        request=request,
        credentials=None,
        authorization=None,
        api_token="api-token",
    )

    assert result["user_id"] == user.id
    assert result["roles"] == ["GM"]
    assert request.state.user_id == user.id
    assert request.state.auth_type == "api_token"


@pytest.mark.asyncio
async def test_revoked_api_token_is_rejected(monkeypatch):
    monkeypatch.setattr(
        deps.UserToken,
        "filter",
        lambda **kwargs: FakeTokenQuery(None),
    )

    with pytest.raises(HTTPException) as exc_info:
        await deps.get_current_user_or_token(
            request=make_request(),
            credentials=None,
            authorization=None,
            api_token="revoked-token",
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid API Token"


@pytest.mark.asyncio
async def test_inactive_api_token_user_is_rejected(monkeypatch):
    token_obj = SimpleNamespace(user=FakeUser(status=UserStatus.DISABLED))
    monkeypatch.setattr(
        deps.UserToken,
        "filter",
        lambda **kwargs: FakeTokenQuery(token_obj),
    )

    with pytest.raises(HTTPException) as exc_info:
        await deps.get_current_user_or_token(
            request=make_request(),
            credentials=None,
            authorization=None,
            api_token="api-token",
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found or inactive"


@pytest.mark.asyncio
async def test_jwt_authentication_still_works(monkeypatch):
    payload = {
        "id": "12345678-1234-1234-1234-123456789012",
        "email": "jwt@example.com",
        "roles": ["ADMIN"],
    }
    monkeypatch.setattr(deps.JwtToken, "verify_token", lambda token: payload)
    request = make_request()

    result = await deps.get_current_user_or_token(
        request=request,
        credentials=HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="jwt-token"
        ),
        authorization="Bearer jwt-token",
        api_token=None,
    )

    assert result["user_id"] == payload["id"]
    assert result["roles"] == ["ADMIN"]
    assert request.state.auth_type == "jwt"


@pytest.mark.asyncio
async def test_api_token_in_bearer_authorization_falls_back_to_database(monkeypatch):
    user = FakeUser()
    token_obj = SimpleNamespace(user=user)

    monkeypatch.setattr(
        deps.JwtToken,
        "verify_token",
        lambda token: (_ for _ in ()).throw(ValueError("not a JWT")),
    )
    monkeypatch.setattr(
        deps.UserToken,
        "filter",
        lambda **kwargs: FakeTokenQuery(token_obj),
    )
    request = make_request()

    result = await deps.get_current_user_or_token(
        request=request,
        credentials=HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="stored-api-token"
        ),
        authorization="Bearer stored-api-token",
        api_token=None,
    )

    assert result["user_id"] == user.id
    assert request.state.auth_type == "api_token"


@pytest.mark.asyncio
async def test_api_token_can_be_direct_authorization_value(monkeypatch):
    user = FakeUser()
    token_obj = SimpleNamespace(user=user)
    captured = {}

    def fake_filter(**kwargs):
        captured.update(kwargs)
        return FakeTokenQuery(token_obj)

    monkeypatch.setattr(deps.UserToken, "filter", fake_filter)

    result = await deps.get_current_user_or_token(
        request=make_request(),
        credentials=None,
        authorization="stored-api-token",
        api_token=None,
    )

    assert captured == {"token": "stored-api-token", "status": Status.OK}
    assert result["user_id"] == user.id
