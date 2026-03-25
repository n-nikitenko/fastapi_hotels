from services import AuthService


def test_create_access_token():
    data = {"user_id": 1}
    access_token = AuthService.create_access_token(data=data)

    assert  access_token
    assert isinstance(access_token, str)