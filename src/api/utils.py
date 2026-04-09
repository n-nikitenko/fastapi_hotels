from datetime import date

from fastapi import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT


def raise_if_dates_inconsistency(from_date: date, to_date: date) -> None:
    if to_date < from_date:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Дата выезда не может быть раньше даты заезда"
        )