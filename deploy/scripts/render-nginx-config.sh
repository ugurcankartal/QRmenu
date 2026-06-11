#!/usr/bin/env bash
# Backend/.env icindeki PROD_RUNSERVER_PORT ile nginx upstream portunu eslestirir.
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/ubuntu/harbiqrmenu}"
BACKEND_ENV="${APP_ROOT}/Backend/.env"
NGINX_TEMPLATE="${APP_ROOT}/deploy/nginx/harbi-kebap.com.conf"
NGINX_TARGET="${1:-/etc/nginx/sites-available/harbi-kebap.com}"

if [[ ! -f "${BACKEND_ENV}" ]]; then
  echo "Backend/.env bulunamadi: ${BACKEND_ENV}"
  exit 1
fi

PROD_RUNSERVER_PORT="$(
  grep -E '^PROD_RUNSERVER_PORT=' "${BACKEND_ENV}" | tail -1 | cut -d= -f2- \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"'
)"
PROD_RUNSERVER_PORT="${PROD_RUNSERVER_PORT:-8000}"
export PROD_RUNSERVER_PORT

echo "==> Nginx upstream port: ${PROD_RUNSERVER_PORT}"

envsubst '${PROD_RUNSERVER_PORT}' < "${NGINX_TEMPLATE}" | sudo tee "${NGINX_TARGET}" >/dev/null
