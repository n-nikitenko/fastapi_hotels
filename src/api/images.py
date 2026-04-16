import os
import shutil

from fastapi import APIRouter, UploadFile, HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT

from config import settings

router = APIRouter(prefix="/images", tags=["Изображения отелей"])


@router.post("/", summary="Загрузка изображения")
def upload_image(image: UploadFile):
    from tasks import resize_image

    if not image.filename:
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_CONTENT, detail="Имя файла не указано")

    image_path = os.path.join(settings.UPLOAD_DIR, image.filename)
    with open(image_path, "wb+") as f:
        shutil.copyfileobj(image.file, f)
    resize_image.delay(  # type: ignore
        image_path=image_path,
        output_dir=settings.UPLOAD_DIR,
    )
    return {"ok": True}
