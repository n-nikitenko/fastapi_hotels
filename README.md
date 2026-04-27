# fastapi_hotels

export PYTHONPATH=/src

## Миграции
```shell
     PYTHONPATH=src alembic revision --autogenerate -m "add_users" # Автоматически сгенерировать миграции

     alembic upgrade head # Применить миграции
```

### Миграции на хостинге (Docker)
```shell
docker compose up -d postgres redis
docker compose run --rm backend poetry run alembic upgrade head
docker compose up -d backend celery celery_beat nginx_service
```


## Тестовое окружение

```shell
     docker compose  -f docker-compose.test.yaml --env-file .env.test up -d
```


## nginx 
Если занят 80 порт
```commandline
sudo service apache2 stop
```