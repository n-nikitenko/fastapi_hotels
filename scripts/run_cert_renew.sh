docker compose down nginx_service
syctemctl start nginx
sudo certbot renew --force_renewal
syctemctl stop nginx
docker compose start nginx_service -d