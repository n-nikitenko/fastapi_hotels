from datetime import timedelta, timezone, datetime

import jwt

from config import settings
from pwdlib import PasswordHash


class AuthService:
    def __init__(self):
        self.password_hash = PasswordHash.recommended()

    def get_password_hash(self, password):
        return self.password_hash.hash(password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)