from starlette.status import HTTP_200_OK


async def test_create_booking(auth_async_client, test_booking_data, register_user):
    response = await auth_async_client.post(
        url="/bookings/",
        json={
            "room_id": test_booking_data.room_id,
            "from_date": str(test_booking_data.from_date),
            "to_date": str(test_booking_data.to_date),
        }
    )
    assert response.status_code == HTTP_200_OK
    response_data = response.json()
    assert response_data["ok"] is True
    assert response_data["data"]["room_id"]==test_booking_data.room_id
    assert response_data["data"]["from_date"]==str(test_booking_data.from_date)
    assert response_data["data"]["to_date"]==str(test_booking_data.to_date)