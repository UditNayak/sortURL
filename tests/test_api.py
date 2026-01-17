def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_url_shortening_endpoint(client):
    payload = {"original_url": "https://example.com"}

    response = client.post("/api/shorten", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com"
