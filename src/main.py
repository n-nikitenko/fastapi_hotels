from asyncpg.exceptions import UniqueViolationError
from fastapi import FastAPI, HTTPException, status
import asyncpg
from sqlalchemy.exc import IntegrityError
from api import hotels_router, auth_router, rooms_router, booking_router, facility_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(hotels_router)
app.include_router(rooms_router)
app.include_router(booking_router)
app.include_router(facility_router)


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request, exc: IntegrityError):
    # Парсим ошибку PostgreSQL
    orig_cause = getattr(exc.orig, '__cause__', None)
    if isinstance(orig_cause, asyncpg.exceptions.UniqueViolationError):
        if "users_email_key" in str(exc.orig):
            raise HTTPException(
                status_code=409,
                detail="Email уже существует"
            )
    raise HTTPException(status_code=400, detail="Ошибка базы данных")

if __name__=="__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        reload=True
    )
