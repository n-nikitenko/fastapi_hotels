from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.dialects import postgresql

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

        # удалить все лишние
        stmt_del = (
            delete(self._model)
            .where(self._model.room_id==room_id)
            .where(self._model.facility_id.not_in(facility_ids))
        )
        await self._session.execute(stmt_del)

        # добавить недостающие (insert … on conflict do nothing)
        rows = [
            {"room_id": room_id, "facility_id": fid}
            for fid in facility_ids
        ]

        stmt_ins = postgresql.insert(RoomFacilityOrm).values(rows)
        stmt_ins = stmt_ins.on_conflict_do_nothing(
            constraint="uq_room_facility"
        )
        await self._session.execute(stmt_ins)