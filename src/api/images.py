import os
import shutil

from fastapi import APIRouter, UploadFile

from config import settings

router = APIRouter(prefix="/images", tags=["Изображения отелей"])

@router.post("/", summary="Загрузка изображения")
def upload_image(image: UploadFile):
    from tasks import resize_image

    image_path=os.path.join(settings.UPLOAD_DIR, image.filename)
    with open(image_path, "wb+") as f:
        shutil.copyfileobj(image.file, f)
    resize_image.delay(
        image_path=image_path,
        output_dir=settings.UPLOAD_DIR,
    )
    return {"ok": True}

