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

## GitLab Runner (отдельный compose)

Runner вынесен в отдельный файл `docker-compose.runner.yaml`, чтобы не смешивать CI/CD-инфраструктуру с приложением.

### 1) Поднять runner-контейнер
```shell
docker compose -f docker-compose.runner.yaml up -d
```

### 2) Зарегистрировать runner в GitLab
Получите registration token в GitLab (Project/Group/Instance -> Settings -> CI/CD -> Runners), затем выполните:

```shell
docker compose -f docker-compose.runner.yaml exec gitlab_runner gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.com/" \
  --registration-token "<YOUR_REGISTRATION_TOKEN>" \
  --executor "docker" \
  --docker-image "alpine:latest" \
  --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
  --docker-volumes "/cache" \
  --description "fastapi-hotels-runner" \
  --tag-list "fastapi,hotels" \
  --run-untagged="true" \
  --locked="false"
```

Если у вас self-hosted GitLab, замените `--url` на URL вашего GitLab.

### 3) Проверить статус runner
```shell
docker compose -f docker-compose.runner.yaml logs -f gitlab_runner
```

### 4) Остановить runner
```shell
docker compose -f docker-compose.runner.yaml down
```

Конфигурация runner сохраняется на хосте в директории `/srv/gitlab-runner/config`.

### 5) Если в pipeline используются Docker-команды (`docker build`, `docker compose`)

Если вы зарегистрировали runner командой выше, `docker.sock` уже будет добавлен автоматически.
Если runner зарегистрирован ранее или другим способом, проверьте файл `/srv/gitlab-runner/config/config.toml` и секцию `[runners.docker]`.
Для доступа job-контейнеров к Docker daemon на хосте должен быть проброшен сокет:

```toml
volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]
```

Если сейчас там только `volumes = ["/cache"]`, добавьте `docker.sock` и перезапустите runner:

```shell
docker compose -f docker-compose.runner.yaml restart gitlab_runner
```

> Примечание: это даёт job'ам расширенный доступ к Docker хоста. Используйте только для доверенных проектов/раннеров.


## nginx 
Если занят 80 порт
```commandline
sudo service apache2 stop
```