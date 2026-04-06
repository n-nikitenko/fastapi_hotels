from starlette.status import HTTP_200_OK


async def test_get_hotels(async_client):
    response = await async_client.get(
        url="/hotels/", params={"from_date": "2026-03-01", "to_date": "2026-04-10"}
    )

    assert response.status_code == HTTP_200_OK
