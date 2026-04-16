from fastapi import APIRouter, UploadFile, HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT

from exceptions import ObjectNotFoundException
from services import ImagesService

router = APIRouter(prefix="/images", tags=["Изображения отелей"])


@router.post("/", summary="Загрузка изображения")
def upload_image(image: UploadFile):
    try:
        ImagesService.upload_image(image)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_CONTENT, detail="Имя файла не указано"
        )
    else:
        return {"ok": True}
