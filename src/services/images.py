import os
import shutil

from fastapi import UploadFile

from config import settings
from exceptions import ObjectNotFoundException
from .base import BaseService
from tasks import resize_image

class ImagesService(BaseService):
    def __init__(self):
        super().__init__()

    @staticmethod
    def upload_image(
            image: UploadFile,
    ):

        if not image.filename:
            raise ObjectNotFoundException()

        image_path = os.path.join(settings.UPLOAD_DIR, image.filename)
        with open(image_path, "wb+") as f:
            shutil.copyfileobj(image.file, f)
        resize_image.delay(  # type: ignore
            image_path=image_path,
            output_dir=settings.UPLOAD_DIR,
        )