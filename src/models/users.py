from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from .base import Base

class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
