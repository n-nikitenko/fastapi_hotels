from starlette.status import HTTP_200_OK


async def test_get_facilities(async_client):
    response = await async_client.get(
        url="/facilities/",
    )

    assert response.status_code == HTTP_200_OK


async def test_create_facility(auth_async_client):
    response = await auth_async_client.post(
        url="/facilities/",
        json={"title": "Душ в номере"},
    )

    assert response.status_code == HTTP_200_OK