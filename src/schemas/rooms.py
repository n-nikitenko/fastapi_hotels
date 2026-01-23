from pydantic import BaseModel


class Room(BaseModel):
    __tablename__ = "rooms"

    id: int
    hotel_id: int
    title: str
    description: str | None
    price: int
    quantity: int