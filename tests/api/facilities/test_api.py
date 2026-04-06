from starlette.status import HTTP_200_OK


async def test_get_facilities(async_client):
    response = await async_client.get(
        url="/facilities/",
    )

    assert response.status_code == HTTP_200_OK
    assert isinstance(response.json(), list)


async def test_create_facility(auth_async_client):
    title = "Душ в номере"
    response = await auth_async_client.post(
        url="/facilities/",
        json={"title": title},
    )

    assert response.status_code == HTTP_200_OK

    response_data = response.json()
    assert response_data["data"]["title"] == title
