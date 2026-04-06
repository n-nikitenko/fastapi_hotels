import pytest
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_CONTENT,
)


@pytest.mark.parametrize(
    argnames=("email", "pwd", "status"),
    argvalues=[
        ("reg_user1@test.ru", "123456", HTTP_200_OK),
        ("reg_user1@test.ru", "123456", HTTP_409_CONFLICT),
        ("reg_user2@test.ru", "123456", HTTP_200_OK),
        ("reg_user2", "123456", HTTP_422_UNPROCESSABLE_CONTENT),
        ("reg_user2@mail.ru", "", HTTP_422_UNPROCESSABLE_CONTENT),
        ("reg_user2@mail.ru", "123456", HTTP_200_OK),
        ("reg_user2@mail", "", HTTP_422_UNPROCESSABLE_CONTENT),
        ("reg_user2@gmail.com", "123456", HTTP_200_OK),
        ("@gmail.com", "123456", HTTP_422_UNPROCESSABLE_CONTENT),
    ],
)
async def test_auth_register(email, pwd, status, async_client):
    response = await async_client.post(
        url="/auth/register",
        json={"email": email, "password": pwd},
    )
    assert response.status_code == status
    if status == HTTP_200_OK:
        assert response.json()["ok"] is True


async def test_auth_success_flow(async_client, new_user_credentials):
    # register
    response = await async_client.post(
        url="/auth/register",
        json=new_user_credentials,
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["ok"] is True
    # me
    response = await async_client.get(
        url="/auth/me",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    # login
    response = await async_client.post(
        url="/auth/login",
        json=new_user_credentials,
    )
    assert response.status_code == HTTP_200_OK
    access_token_from_body = response.json().get("access_token")
    access_token_from_cookie = async_client.cookies.get("access_token")
    assert access_token_from_body, "В ответе логина отсутствует access_token"
    assert access_token_from_cookie, "После логина не установился access_token cookie"
    assert access_token_from_cookie == access_token_from_body, (
        "Токен в cookie не совпадает с токеном в response body"
    )
    # me
    response = await async_client.get(
        url="/auth/me",
    )
    assert response.status_code == HTTP_200_OK
    user_data = response.json()
    assert user_data["email"] == new_user_credentials["email"]
    # logout
    response = await async_client.post(
        url="/auth/logout",
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["ok"] is True
    assert not response.json().get("access_token")
    # me
    response = await async_client.get(
        url="/auth/me",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
