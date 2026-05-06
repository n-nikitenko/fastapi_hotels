#!/usr/bin/env bash
set -euo pipefail

docker compose stop nginx_service
sudo systemctl start nginx
sudo certbot renew --force_renewal
sudo systemctl stop nginx
docker compose up -d --no-deps nginx_service