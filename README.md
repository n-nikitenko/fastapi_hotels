# fastapi_hotels

export PYTHONPATH=/src

## Миграции
```shell
     PYTHONPATH=src alembic revision --autogenerate -m "add_users" # Автоматически сгенерировать миграции

     alembic upgrade head # Применить миграции
```