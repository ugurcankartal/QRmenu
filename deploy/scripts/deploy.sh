#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/ubuntu/harbiqrmenu}"
BACKEND_DIR="${APP_ROOT}/Backend"
FRONTEND_DIR="${APP_ROOT}/Frontend"
REPO_OWNER="${REPO_OWNER:-ubuntu}"

echo "==> Deploy QRmenu at ${APP_ROOT}"

if [[ ! -d "${BACKEND_DIR}/venv" ]]; then
  echo "Virtualenv not found. Run initial setup first (see deploy/DEPLOY.md)."
  exit 1
fi

run_as_owner() {
  if [[ "$(id -un)" == "${REPO_OWNER}" ]]; then
    "$@"
  else
    sudo -u "${REPO_OWNER}" -H "$@"
  fi
}

if [[ "$(id -un)" == "root" ]]; then
  echo "==> Fix repo ownership for ${REPO_OWNER}"
  chown -R "${REPO_OWNER}:${REPO_OWNER}" "${APP_ROOT}"
fi

echo "==> Sync from GitHub (origin/main)"
run_as_owner bash -lc "
  set -euo pipefail
  cd '${APP_ROOT}'
  git fetch origin
  git reset --hard origin/main
  git clean -fd --exclude=Backend/.env --exclude=Frontend/.env --exclude=Frontend/.env.production
"

echo "==> Backend dependencies, migrate, collectstatic"
run_as_owner bash -lc "
  set -euo pipefail
  source '${BACKEND_DIR}/venv/bin/activate'
  pip install -r '${BACKEND_DIR}/requirements.txt'
  export DJANGO_SETTINGS_MODULE=config.settings.prod
  cd '${BACKEND_DIR}'
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
"

echo "==> Frontend build"
run_as_owner bash -lc "
  set -euo pipefail
  cd '${FRONTEND_DIR}'
  pnpm install --frozen-lockfile || pnpm install
  pnpm run build
  test -f dist/index.html
"

chmod -R a+rX "${FRONTEND_DIR}/dist"

sudo mkdir -p /var/log/qrmenu
sudo chown www-data:www-data /var/log/qrmenu
sudo chmod 640 "${BACKEND_DIR}/.env" 2>/dev/null || true

bash "${APP_ROOT}/deploy/scripts/fix-upload-permissions.sh"

bash "${APP_ROOT}/deploy/scripts/render-nginx-config.sh"
sudo cp "${APP_ROOT}/deploy/systemd/qrmenu.service" /etc/systemd/system/qrmenu.service
sudo systemctl daemon-reload
sudo systemctl restart qrmenu
sudo nginx -t
sudo systemctl reload nginx

echo "==> Deploy finished."
