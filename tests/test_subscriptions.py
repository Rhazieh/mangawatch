MANGADEX_URL = "https://mangadex.org/title/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
MANWHACLAN_URL = "https://manwhaclan.com/manga/the-beginning-after-the-end/"
KUNMANGA_URL = "https://kunmanga.com/manga/solo-leveling/"


def _auth_headers(client):
    client.post("/auth/register", json={"email": "u@example.com", "password": "pass"})
    token = client.post(
        "/auth/login", json={"email": "u@example.com", "password": "pass"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_subscribe_to_mangadex_url(client):
    r = client.post(
        "/subscriptions",
        json={"url": MANGADEX_URL},
        headers=_auth_headers(client),
    )
    assert r.status_code == 201


def test_subscribe_requires_auth(client):
    r = client.post("/subscriptions", json={"url": MANGADEX_URL})
    assert r.status_code == 403


def test_subscribe_unsupported_url(client):
    r = client.post(
        "/subscriptions",
        json={"url": "https://notsupported.com/series/something"},
        headers=_auth_headers(client),
    )
    assert r.status_code == 400


def test_subscribe_duplicate_returns_409(client):
    headers = _auth_headers(client)
    client.post("/subscriptions", json={"url": MANGADEX_URL}, headers=headers)
    r = client.post("/subscriptions", json={"url": MANGADEX_URL}, headers=headers)
    assert r.status_code == 409


def test_subscribe_to_manwhaclan_url(client):
    r = client.post(
        "/subscriptions",
        json={"url": MANWHACLAN_URL},
        headers=_auth_headers(client),
    )
    assert r.status_code == 201


def test_subscribe_to_kunmanga_url(client):
    r = client.post(
        "/subscriptions",
        json={"url": KUNMANGA_URL},
        headers=_auth_headers(client),
    )
    assert r.status_code == 201


def test_list_subscriptions(client):
    headers = _auth_headers(client)
    client.post("/subscriptions", json={"url": MANGADEX_URL}, headers=headers)
    client.post("/subscriptions", json={"url": KUNMANGA_URL}, headers=headers)

    r = client.get("/subscriptions", headers=headers)
    assert r.status_code == 200
    urls = [s["source_url"] for s in r.json()]
    assert MANGADEX_URL in urls
    assert KUNMANGA_URL in urls
