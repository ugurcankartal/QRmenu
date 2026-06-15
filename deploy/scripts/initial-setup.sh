#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/ubuntu/harbiqrmenu}"
BACKEND_DIR="${APP_ROOT}/Backend"
FRONTEND_DIR="${APP_ROOT}/Frontend"

echo "==> Initial server setup for QRmenu"

sudo apt update
sudo apt install -y git python3 python3-venv python3-pip python3-dev \
  default-libmysqlclient-dev build-essential pkg-config \
  nginx mysql-server curl

if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt install -y nodejs
fi

if ! command -v pnpm >/dev/null 2>&1; then
  sudo npm install -g pnpm
fi

cd "${BACKEND_DIR}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f "${BACKEND_DIR}/.env" ]]; then
  cp "${APP_ROOT}/deploy/env/backend.env.example" "${BACKEND_DIR}/.env"
  echo "Created Backend/.env — edit it before continuing."
  exit 1
fi

if [[ ! -f "${FRONTEND_DIR}/.env" ]]; then
  cp "${APP_ROOT}/deploy/env/frontend.env.example" "${FRONTEND_DIR}/.env"
fi

export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py collectstatic --noinput

cd "${FRONTEND_DIR}"
pnpm install
pnpm run build

sudo mkdir -p /var/log/qrmenu
sudo chown www-data:www-data /var/log/qrmenu

sudo cp "${APP_ROOT}/deploy/systemd/qrmenu.service" /etc/systemd/system/qrmenu.service
bash "${APP_ROOT}/deploy/scripts/render-nginx-config.sh"
sudo ln -sf /etc/nginx/sites-available/harbi-kebap.com /etc/nginx/sites-enabled/harbi-kebap.com
sudo rm -f /etc/nginx/sites-enabled/default

sudo chown -R ubuntu:www-data "${APP_ROOT}"
bash "${APP_ROOT}/deploy/scripts/fix-upload-permissions.sh"
sudo chmod 750 "${BACKEND_DIR}"
sudo chmod 640 "${BACKEND_DIR}/.env"

sudo systemctl daemon-reload
sudo systemctl enable qrmenu
sudo systemctl start qrmenu
sudo nginx -t
sudo systemctl reload nginx

echo "==> Initial setup done."
echo "Next: point DNS to this server, then run:"
echo "  sudo certbot --nginx -d harbi-kebap.com -d www.harbi-kebap.com"
