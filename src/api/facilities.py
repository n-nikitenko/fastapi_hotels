from fastapi import APIRouter, Body
from fastapi.openapi.models import Example

from api.dependencies import DbDep, UserIdDep, PaginationDep
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
async def get_bookings(
        db: DbDep,
):
    return await db.facilities.get_all()