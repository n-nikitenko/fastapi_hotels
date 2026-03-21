import asyncio
from pathlib import Path
from time import sleep

from PIL import Image

from .celery_app import celery_app
from .helpers import get_bookings_with_today_checkin_helper


@celery_app.task
def test_task():
    sleep(5)
    print("Я молодец")

@celery_app.task
def resize_image(image_path: Path | str, output_dir: Path | str, widths: tuple[int] = (300, 500, 700)):
    """
    Сжимает изображение до заданных ширин, сохраняя пропорции.
    """
    img_path = Path(image_path)
    out_dir = Path(output_dir)

    # Создаем папку, если её нет
    out_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(img_path) as img:
        orig_width, orig_height = img.size

        for width in widths:
            # Рассчитываем высоту для сохранения пропорций
            ratio = width / float(orig_width)
            height = int(float(orig_height) * float(ratio))

            # Ресайз (LANCZOS — лучший фильтр для уменьшения)
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)

            # Формируем имя файла: "имя_300px.jpg"
            file_name = f"{img_path.stem}_{width}px{img_path.suffix}"
            save_path = out_dir / file_name

            # Сохраняем (для JPEG можно добавить quality=85)
            resized_img.save(save_path, optimize=True)


@celery_app.task(name="booking_today_checkin")
def send_emails_to_users_with_today_checkin():
    asyncio.run(get_bookings_with_today_checkin_helper())