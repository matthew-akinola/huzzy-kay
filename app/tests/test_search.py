from fastapi import status, FastAPI
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_search_without_required_name_parameter(client: AsyncClient, app: FastAPI):
    url = app.url_path_for("search_vips")
    url = url + "?age=57&&email=email@test.com"
    
    response = await client.get(url)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_search(client: AsyncClient, app: FastAPI):
    url = app.url_path_for("search_vips")
    url = url + "?name=Obama"
    
    response = await client.get(url)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert response_data["name"]
    assert response_data["vip_score"]