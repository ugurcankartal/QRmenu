#!/usr/bin/env bash
# Gunicorn ubuntu kullanicisiyla calisir; media/static yazilabilir olmali.
# Nginx (www-data) dosyalari grup uzerinden okur.
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/ubuntu/harbiqrmenu}"
BACKEND_DIR="${APP_ROOT}/Backend"
REPO_OWNER="${REPO_OWNER:-ubuntu}"

sudo mkdir -p \
  "${BACKEND_DIR}/media/images/products" \
  "${BACKEND_DIR}/media/images/categories" \
  "${BACKEND_DIR}/media/images/campaigns" \
  "${BACKEND_DIR}/media/images/chef-recommendations" \
  "${BACKEND_DIR}/media/images/gallery" \
  "${BACKEND_DIR}/media/languages/flags" \
  "${BACKEND_DIR}/media/settings" \
  "${BACKEND_DIR}/staticfiles" \
  "${BACKEND_DIR}/cache/django"

sudo chown -R "${REPO_OWNER}:www-data" \
  "${BACKEND_DIR}/media" \
  "${BACKEND_DIR}/staticfiles" \
  "${BACKEND_DIR}/cache"
sudo chmod -R u=rwX,g=rX,o= "${BACKEND_DIR}/media"
sudo chmod -R u=rwX,g=rX,o=rX "${BACKEND_DIR}/staticfiles"
sudo chmod -R u=rwX,g=rX,o= "${BACKEND_DIR}/cache"
