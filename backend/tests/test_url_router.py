from fastapi import status as http_status


async def test_create_url_success(client):
    response = await client.post(
        "/api/v0/url/",
        json={"slug": "test-slug", "original_url": "https://example.com"},
    )

    assert response.status_code == http_status.HTTP_201_CREATED
    data = response.json()
    assert data["slug"] == "test-slug"
    assert data["original_url"] == "https://example.com/"
    assert "id" in data
    assert data["visits"] == 0
    assert "created_at" in data
    assert "updated_at" in data
    assert "last_visit_at" in data


async def test_create_url_duplicate_slug(client):
    response = await client.post(
        "/api/v0/url/",
        json={"slug": "duplicate-slug", "original_url": "https://example.com"},
    )
    assert response.status_code == http_status.HTTP_201_CREATED

    response = await client.post(
        "/api/v0/url/",
        json={"slug": "duplicate-slug", "original_url": "https://another-example.com"},
    )

    assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "The URL with this slug already exists"


async def test_get_short_urls(client):
    await client.post(
        "/api/v0/url/",
        json={"slug": "list-slug", "original_url": "https://list.com"},
    )
    response = await client.get("/api/v0/url/")

    assert response.status_code == http_status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert any(url["slug"] == "list-slug" for url in data["items"])


async def test_patch_short_url_success(client):
    resp = await client.post(
        "/api/v0/url/",
        json={"slug": "patch-slug", "original_url": "https://patch.com"},
    )
    url_id = resp.json()["id"]

    response = await client.patch(
        f"/api/v0/url/{url_id}",
        json={"original_url": "https://patched.com"},
    )
    assert response.status_code == http_status.HTTP_204_NO_CONTENT


async def test_patch_short_url_not_found(client):
    response = await client.patch(
        "/api/v0/url/99999",
        json={"original_url": "https://notfound.com"},
    )
    assert response.status_code == http_status.HTTP_404_NOT_FOUND


async def test_delete_short_url_success(client):
    resp = await client.post(
        "/api/v0/url/",
        json={"slug": "delete-slug", "original_url": "https://delete.com"},
    )
    url_id = resp.json()["id"]
    response = await client.delete(f"/api/v0/url/{url_id}")
    assert response.status_code == http_status.HTTP_204_NO_CONTENT


async def test_delete_short_url_not_found(client):
    response = await client.delete("/api/v0/url/99999")
    assert response.status_code == http_status.HTTP_404_NOT_FOUND


async def test_add_and_delete_tag_url(client):
    url_resp = await client.post(
        "/api/v0/url/",
        json={"slug": "tag-slug", "original_url": "https://tag.com"},
    )
    url_id = url_resp.json()["id"]

    tag_resp = await client.post(
        "/api/v0/tag/",
        json={"name": "test-tag"},
    )
    tag_id = tag_resp.json()["id"]

    response = await client.post(
        f"/api/v0/url/{url_id}/tag",
        json={"tag_ids": [tag_id]},
    )
    assert response.status_code == http_status.HTTP_201_CREATED

    del_response = await client.request(
        "DELETE",
        f"/api/v0/url/{url_id}/tag",
        json={"tag_ids": [tag_id]},
        headers={"Content-Type": "application/json"},
    )
    assert del_response.status_code == http_status.HTTP_204_NO_CONTENT
