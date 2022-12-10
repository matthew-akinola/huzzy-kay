from fastapi import status, FastAPI
import factory
import json
import pytest
from httpx import AsyncClient
from ..db.models.user import User

class UserFactory(factory.Factory):
    first_name = "First Name"
    last_name = "Last Name"
    email = factory.Sequence(lambda n: "test%d@test.com" % n)
    password = factory.Sequence(lambda n: "testpassword%d" % n)

    class Meta:
        model = User
        

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, app: FastAPI):
    data  = {
        "first_name":"test first name",
        "last_name": "test last name",
        "email": "test email",
        "password": "testpassword"
    }
    url = app.url_path_for("create_user")

    response = await client.post(url, data=json.dumps(data))
    response_data = response.json()
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response_data["id"]
    assert response_data["first_name"] == data["first_name"]
    assert response_data["last_name"] == data["last_name"]
    assert response_data["email"] == data["email"]
    assert response_data["password"] == None


@pytest.mark.asyncio
async def test_user_login(client: AsyncClient, app: FastAPI):
    user: User = UserFactory()

    user_cred = {
        "email": user.email,
        "password": user.password
    }
    url = app.url_path_for("login")

    response = await client.post(url, data=json.dumps(user_cred))
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["user"]["id"]
    assert response_data["user"]["first_name"] == user.first_name
    assert response_data["user"]["last_name"] == user.last_name
    assert response_data["user"]["email"] == user.email
    assert response_data["access_token"]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, app: FastAPI):
    user: User = UserFactory()

    user_cred = {
        "email": user.email,
        "password": user.password
    }
    url = app.url_path_for("login")

    response = await client.post(url, data=json.dumps(user_cred))
    access_token = response.json()["access_token"]

    url = app.url_path_for("get_current_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get(url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
