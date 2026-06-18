#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/ubuntu/harbiqrmenu}"
BACKEND_DIR="${APP_ROOT}/Backend"
ENV_FILE="${BACKEND_DIR}/.env"

read_env_var() {
  local key="$1"
  local default="${2:-}"
  local value=""
  if [[ -f "${ENV_FILE}" ]]; then
    value="$(
      grep -E "^${key}=" "${ENV_FILE}" | tail -1 | cut -d= -f2- \
        | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"' | tr -d '\r'
    )"
  fi
  echo "${value:-$default}"
}

PROD_RUNSERVER_PORT="$(read_env_var PROD_RUNSERVER_PORT 8000)"
GUNICORN_TIMEOUT="$(read_env_var GUNICORN_TIMEOUT 600)"
export DJANGO_SETTINGS_MODULE=config.settings.prod

cd "${BACKEND_DIR}"
# shellcheck disable=SC1091
source "${BACKEND_DIR}/venv/bin/activate"

exec gunicorn \
  --workers 3 \
  --timeout "${GUNICORN_TIMEOUT}" \
  --bind "127.0.0.1:${PROD_RUNSERVER_PORT}" \
  --access-logfile - \
  --error-logfile - \
  config.wsgi:application
