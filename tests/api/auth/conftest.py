import pytest


@pytest.fixture()
def new_user_credentials() -> dict[str, str]:
    return {
        "email": "new_user@test.ru",
        "password": "Test123456",
    }