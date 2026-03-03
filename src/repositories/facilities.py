from sqlalchemy import delete, select, insert

from models import FacilityOrm, RoomFacilityOrm
from repositories.base import BaseRepository
from schemas import Facility, RoomFacility


class FacilityRepository(BaseRepository):
    _model = FacilityOrm
    _schema = Facility


class RoomsFacilitiesRepository(BaseRepository):
    _model = RoomFacilityOrm
    _schema = RoomFacility


    async def sync_room_facilities(self, room_id: int, facility_ids: list[int]) -> None:
        if not facility_ids:
            await self.delete(room_id=room_id)
            return

        stmt_select = (
            select(self._model.id)
        )
        result = await self._session.execute(stmt_select)
        current_facilities_ids = set(result.scalars().all())
        new_facilities_ids = set(facility_ids)

        ids_for_delete = current_facilities_ids - new_facilities_ids
        ids_for_add = new_facilities_ids - current_facilities_ids

        # удалить все лишние
        stmt_del = (
            delete(self._model)
            .where(self._model.room_id==room_id)
            .where(self._model.facility_id.in_(list(ids_for_delete)))
        )
        await self._session.execute(stmt_del)

        rows = [
            {"room_id": room_id, "facility_id": fid}
            for fid in ids_for_add
        ]

        stmt_ins = insert(RoomFacilityOrm).values(rows)
        await self._session.execute(stmt_ins)