from schemas import RoomFacility, FacilityAdd
from .base import BaseService
import tasks


class FacilitiesService(BaseService):
    async def get_all(self) -> list[RoomFacility]:
        assert self.db is not None
        return await self.db.facilities.get_all()

    async def create(
        self,
        facility_data: FacilityAdd,
    ) -> RoomFacility:
        assert self.db is not None
        facility = await self.db.facilities.create(facility_data)
        await self.db.commit()
        tasks.test_task.delay()  # type: ignore
        return facility
