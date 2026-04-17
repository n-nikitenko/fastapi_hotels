from fastapi import APIRouter, UploadFile

from exceptions import ObjectNotFoundException, NoImageFileHttpException
from services import ImagesService

router = APIRouter(prefix="/images", tags=["Изображения отелей"])


@router.post("/", summary="Загрузка изображения")
def upload_image(image: UploadFile):
    try:
        ImagesService.upload_image(image)
    except ObjectNotFoundException:
        raise NoImageFileHttpException()
    else:
        return {"ok": True}
