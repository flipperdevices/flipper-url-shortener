import pytest
from fastapi import status

from app.core import settings


@pytest.mark.asyncio
async def test_redirect_root_success(client, monkeypatch):
    redirect_url = "http://redirect.url/path"
    monkeypatch.setattr(
        settings.application_settings, "ROOT_REDIRECT_URL", redirect_url
    )

    response = await client.get("/")
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == redirect_url


@pytest.mark.asyncio
async def test_redirect_root_not_found(client, monkeypatch):
    monkeypatch.setattr(settings.application_settings, "ROOT_REDIRECT_URL", None)

    response = await client.get("/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "The URL not found"


@pytest.mark.asyncio
async def test_redirect_by_short_url_success(client):
    resp = await client.post(
        "/api/v0/url/",
        json={"slug": "redir-slug", "original_url": "https://redirect.com"},
    )

    response = await client.get("/redir-slug")
    assert resp.status_code == status.HTTP_201_CREATED
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "https://redirect.com/"


@pytest.mark.asyncio
async def test_redirect_by_short_url_not_found(client):
    response = await client.get("/redirect/nonexistent-slug")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "The URL not found"
