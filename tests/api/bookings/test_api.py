import pytest
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    argnames=("from_date", "to_date", "status_code"),
    argvalues=[
        ("2026-03-01", "2026-03-04", HTTP_200_OK),
        ("2026-03-01", "2026-03-04", HTTP_200_OK),
        ("2026-03-01", "2026-03-04", HTTP_200_OK),
        ("2026-03-01", "2026-03-04", HTTP_200_OK),
        ("2026-03-01", "2026-03-04", HTTP_200_OK),
        ("2026-03-01", "2026-03-04", HTTP_404_NOT_FOUND),
        ("2026-03-05", "2026-03-07", HTTP_200_OK),
    ]
)
async def test_create_booking(auth_async_client, from_date, to_date, status_code):
    response = await auth_async_client.post(
        url="/bookings/",
        json={
            "room_id": 1,
            "from_date": from_date,
            "to_date": to_date,
        }
    )
    assert response.status_code == status_code
    if status_code == HTTP_200_OK:
        response_data = response.json()
        assert response_data["ok"] is True
        assert response_data["data"]["room_id"]==1
        assert response_data["data"]["from_date"]==from_date
        assert response_data["data"]["to_date"]==to_date

@pytest.mark.parametrize(
    argnames=("from_date", "to_date", "bookings_count"),
    argvalues=[
        ("2026-03-01", "2026-03-04", 1),
        ("2026-03-01", "2026-03-04", 2),
        ("2026-03-01", "2026-03-04", 3),
        ("2026-03-01", "2026-03-04", 4),
        ("2026-03-01", "2026-03-04", 5),
        ("2026-03-01", "2026-03-04", 5),
        ("2026-03-05", "2026-03-07", 6),
    ]
)
async def test_add_and_get_my_bookings(remove_all_bookings, auth_async_client, from_date, to_date, bookings_count):
    await auth_async_client.post(
        url="/bookings/",
        json={
            "room_id": 1,
            "from_date": from_date,
            "to_date": to_date,
        }
    )

    response = await auth_async_client.get(
        url="/bookings/me"
    )

    assert response.status_code==HTTP_200_OK
    assert len(response.json()) == bookings_count