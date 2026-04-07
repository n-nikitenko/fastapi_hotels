from fastapi import APIRouter, Body
from fastapi.openapi.models import Example
from fastapi_cache.decorator import cache
import tasks

from api.dependencies import DbDep, UserIdDep
from schemas import FacilityAdd

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.post("/", summary="Создание")
async def create_facility(
    db: DbDep,
    user_id: UserIdDep,
    facility_data: FacilityAdd = Body(
        openapi_examples={
            "1": Example(
                summary="Душ в номере",
                value={"title": "Душ в номере"},
            ),
            "2": Example(
                summary="Wi-fi",
                value={"title": "Wi-fi"},
            ),
        }
    ),
):

    facility = await db.facilities.create(facility_data)
    await db.commit()
    tasks.test_task.delay()  # type: ignore

    return {"ok": True, "data": facility}


@router.get("/", summary="Список всех удобств")
@cache(expire=5)
async def get_facilities(
    db: DbDep,
):
    return await db.facilities.get_all()
