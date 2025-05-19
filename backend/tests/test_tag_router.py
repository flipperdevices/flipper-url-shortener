from fastapi import status as http_status


async def test_create_tag_success(client):
    response = await client.post(
        "/api/v0/tag/",
        json={"name": "test-tag"},
    )

    assert response.status_code == http_status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "test-tag"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_create_tag_duplicate(client):
    await client.post("/api/v0/tag/", json={"name": "dup-tag"})

    response = await client.post("/api/v0/tag/", json={"name": "dup-tag"})
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "The Tag with this name already exists"


async def test_get_tags(client):
    await client.post("/api/v0/tag/", json={"name": "list-tag"})
    response = await client.get("/api/v0/tag/")

    assert response.status_code == http_status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert any(tag["name"] == "list-tag" for tag in data["items"])


async def test_get_tags_query(client):
    await client.post("/api/v0/tag/", json={"name": "querytag"})
    response = await client.get("/api/v0/tag/?query=querytag")

    assert response.status_code == http_status.HTTP_200_OK
    data = response.json()
    assert any(tag["name"] == "querytag" for tag in data["items"])


async def test_patch_tag_success(client):
    resp = await client.post("/api/v0/tag/", json={"name": "patch-tag"})
    tag_id = resp.json()["id"]
    response = await client.patch(f"/api/v0/tag/{tag_id}", json={"name": "patched-tag"})
    assert response.status_code == http_status.HTTP_204_NO_CONTENT

    tags = await client.get("/api/v0/tag/")
    assert any(tag["name"] == "patched-tag" for tag in tags.json()["items"])


async def test_patch_tag_not_found(client):
    response = await client.patch("/api/v0/tag/99999", json={"name": "notfound"})
    assert response.status_code == http_status.HTTP_404_NOT_FOUND


async def test_patch_tag_duplicate_name(client):
    await client.post("/api/v0/tag/", json={"name": "dup1"})
    resp = await client.post("/api/v0/tag/", json={"name": "dup2"})
    tag_id = resp.json()["id"]

    response = await client.patch(f"/api/v0/tag/{tag_id}", json={"name": "dup1"})
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "The Tag with this name already exists"


async def test_delete_tag_success(client):
    resp = await client.post("/api/v0/tag/", json={"name": "del-tag"})
    tag_id = resp.json()["id"]

    response = await client.delete(f"/api/v0/tag/{tag_id}")
    assert response.status_code == http_status.HTTP_204_NO_CONTENT

    tags = await client.get("/api/v0/tag/")
    assert not any(tag["id"] == tag_id for tag in tags.json()["items"])


async def test_delete_tag_not_found(client):
    response = await client.delete("/api/v0/tag/99999")
    assert response.status_code == http_status.HTTP_404_NOT_FOUND
