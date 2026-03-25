# fastapi_hotels

export PYTHONPATH=/src

## Миграции
```shell
     PYTHONPATH=src alembic revision --autogenerate -m "add_users" # Автоматически сгенерировать миграции

     alembic upgrade head # Применить миграции
```


## Тестовое окружение

```shell
     docker compose  -f docker-compose.test.yaml --env-file .env.test up -d
```