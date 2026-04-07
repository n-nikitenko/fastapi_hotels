from sqlalchemy import delete, select, insert

from models import RoomFacilityOrm
from repositories.base import BaseRepository
from repositories.mappers import FacilityDataMapper, RoomsFacilitiesDataMapper


class FacilityRepository(BaseRepository):
    _mapper = FacilityDataMapper


class RoomsFacilitiesRepository(BaseRepository):
    _mapper = RoomsFacilitiesDataMapper

    async def sync_room_facilities(self, room_id: int, facility_ids: list[int]) -> None:
        if not facility_ids:
            await self.delete(room_id=room_id)
            return

        assert self._mapper.db_model is not None

        stmt_select = select(self._mapper.db_model.id)
        result = await self._session.execute(stmt_select)
        current_facilities_ids = set(result.scalars().all())
        new_facilities_ids = set(facility_ids)

        ids_for_delete = current_facilities_ids - new_facilities_ids
        ids_for_add = new_facilities_ids - current_facilities_ids

        # удалить все лишние
        stmt_del = (
            delete(self._mapper.db_model)
            .where(self._mapper.db_model.room_id == room_id)
            .where(self._mapper.db_model.facility_id.in_(list(ids_for_delete)))
        )
        await self._session.execute(stmt_del)

        rows = [{"room_id": room_id, "facility_id": fid} for fid in ids_for_add]

        stmt_ins = insert(RoomFacilityOrm).values(rows)
        await self._session.execute(stmt_ins)
