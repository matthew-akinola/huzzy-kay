from fastapi.testclient import TestClient
from ...core.app import get_app

client = TestClient(get_app())

def test_create_user():
    response = client.post(
        "/user/signup",
        json={"first_name": "imatt", "last_name": "Asokere", "email": "asokere101@gmail.com", "password":"string"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "foobar",
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }