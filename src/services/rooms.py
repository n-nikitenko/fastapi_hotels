from datetime import date

from schemas import RoomAdd, RoomAddEx, RoomFacilityAdd, Room, RoomPatchRequest, RoomWithRels
from .base import BaseService


class RoomsService(BaseService):
    async  def get_filtered_by_date(
            self,
            hotel_id: int,
            from_date: date,
            to_date: date,
    ):
        return await self.db.rooms.get_filtered_by_date(
            hotel_id=hotel_id, from_date=from_date, to_date=to_date,
        )

    async  def remove(
            self,
            hotel_id: int,
            room_id: int,
    ):
        await self.db.rooms.delete(id=room_id, hotel_id=hotel_id)
        await self.db.commit()

    async def create(
            self,
            hotel_id: int,
            room_data: RoomAdd,
    ) -> Room:
        new_room = room_data.model_dump()
        new_room["hotel_id"] = hotel_id
        room = await self.db.rooms.create(RoomAddEx.model_validate(new_room))
        if room_data.facilities_ids:
            await self.db.rooms_facilities.bulk_create(
                [
                    RoomFacilityAdd(room_id=room.id, facility_id=facility_id)
                    for facility_id in room_data.facilities_ids
                ]
            )
        await self.db.commit()
        return room

    async def update(
            self,
            hotel_id: int,
            room_id: int,
            room_data: RoomAdd | RoomPatchRequest,
            exclude_unset: bool = True,
    ) -> Room:
        room = await self.db.rooms.update(
            RoomAddEx.model_validate(
                room_data.model_dump(exclude={"facilities_ids"}, exclude_unset=exclude_unset,) | {"hotel_id": hotel_id},
            ),
            id=room_id,
            hotel_id=hotel_id,
            exclude_unset=exclude_unset,
        )
        await self.db.rooms_facilities.sync_room_facilities(
            room_id=room.id,
            facility_ids=room_data.facilities_ids,
        )
        await self.db.commit()
        return room


    async def get(
            self,
            hotel_id: int,
            room_id: int,
    ) -> RoomWithRels:
        return await self.db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)