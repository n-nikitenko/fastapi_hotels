docker compose down nginx_service
systemctl start nginx
sudo certbot renew --force_renewal
systemctl stop nginx
docker compose up -d nginx_service