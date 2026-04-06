from services import AuthService


def test_decode_encode_access_token():
    data = {"user_id": 1}
    access_token = AuthService.create_access_token(data=data)

    payload = AuthService.decode_token(token=access_token)

    assert payload.get("user_id") == data["user_id"]
