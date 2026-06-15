#!/usr/bin/env bash
# Sunucuda certbot sertifikasi alindi ama nginx/qrmenu kurulmadiysa calistirin.
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/ubuntu/harbiqrmenu}"
BACKEND_DIR="${APP_ROOT}/Backend"
FRONTEND_DIR="${APP_ROOT}/Frontend"
VENV_ACTIVATE="${BACKEND_DIR}/venv/bin/activate"

echo "==> Finish harbi-kebap.com nginx + qrmenu setup"

if [[ ! -f "${BACKEND_DIR}/.env" ]]; then
  echo "Backend/.env bulunamadi. Once env dosyasini olusturun."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 bulunamadi."
  exit 1
fi

if [[ ! -f "${VENV_ACTIVATE}" ]]; then
  echo "==> Python virtualenv olusturuluyor..."
  if ! python3 -m venv "${BACKEND_DIR}/venv" 2>/dev/null; then
    sudo apt update
    sudo apt install -y python3-venv python3-pip
    rm -rf "${BACKEND_DIR}/venv"
    python3 -m venv "${BACKEND_DIR}/venv"
  fi
fi

echo "==> Sistem bagimliliklari kontrol ediliyor..."
if ! command -v pkg-config >/dev/null 2>&1; then
  sudo apt update
  sudo apt install -y pkg-config default-libmysqlclient-dev build-essential python3-dev
fi

# shellcheck disable=SC1090
source "${VENV_ACTIVATE}"
pip install --upgrade pip
pip install -r "${BACKEND_DIR}/requirements.txt"

export DJANGO_SETTINGS_MODULE=config.settings.prod
cd "${BACKEND_DIR}"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [[ ! -f "${FRONTEND_DIR}/.env" ]]; then
  cp "${APP_ROOT}/deploy/env/frontend.env.example" "${FRONTEND_DIR}/.env"
fi

if ! command -v pnpm >/dev/null 2>&1; then
  sudo npm install -g pnpm
fi

cd "${FRONTEND_DIR}"
if [[ ! -f "${FRONTEND_DIR}/.env.production" ]]; then
  cp "${APP_ROOT}/deploy/env/frontend.env.example" "${FRONTEND_DIR}/.env.production"
fi
export CI=true
pnpm install --frozen-lockfile || pnpm install
pnpm rebuild esbuild @tailwindcss/oxide
pnpm run build

if [[ ! -d "${FRONTEND_DIR}/dist" ]]; then
  echo "Frontend build basarisiz: dist/ klasoru yok."
  exit 1
fi

sudo mkdir -p /var/log/qrmenu /var/www/html
sudo chown www-data:www-data /var/log/qrmenu

sudo cp "${APP_ROOT}/deploy/systemd/qrmenu.service" /etc/systemd/system/qrmenu.service
bash "${APP_ROOT}/deploy/scripts/render-nginx-config.sh"
sudo ln -sf /etc/nginx/sites-available/harbi-kebap.com /etc/nginx/sites-enabled/harbi-kebap.com

sudo chown -R ubuntu:www-data "${APP_ROOT}"
sudo chmod o+x /home/ubuntu /home/ubuntu/harbiqrmenu 2>/dev/null || true
bash "${APP_ROOT}/deploy/scripts/fix-upload-permissions.sh"
sudo chmod 640 "${BACKEND_DIR}/.env"

sudo systemctl daemon-reload
sudo systemctl enable qrmenu
sudo systemctl restart qrmenu
sudo nginx -t
sudo systemctl reload nginx

echo "==> Local test:"
curl -sI -H "Host: harbi-kebap.com" http://127.0.0.1 | head -5 || true
curl -skI -H "Host: harbi-kebap.com" https://127.0.0.1 | head -5 || true

echo "==> Done. Cloudflare SSL mode: Full (strict)"
