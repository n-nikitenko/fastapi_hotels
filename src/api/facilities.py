import json

from fastapi import APIRouter, Body
from fastapi.openapi.models import Example

from api.dependencies import DbDep, UserIdDep, PaginationDep
from connectors import redis_manager
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
                    value={
                        "title": "Душ в номере"
                    },
                ),
                "2": Example(
                    summary="Wi-fi",
                    value={
                        "title": "Wi-fi"
                    },
                )
            }
        )
):

    facility =  await db.facilities.create(facility_data)
    await db.commit()

    return {"ok": True, "data": facility}

@router.get("/", summary="Список всех удобств")
async def get_facilities(
        db: DbDep,
):
    facilities = await redis_manager.get_json("facilities")
    if not facilities:
        facilities = await db.facilities.get_all()
        await redis_manager.set_json("facilities", [facility.model_dump() for facility in facilities], ex=30)

    return facilities