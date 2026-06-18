# QRmenu — harbi-kebap.com production kurulumu

Sunucu yolu: `/home/ubuntu/harbiqrmenu`  
Domain: `harbi-kebap.com`

## Mimari

```
Nginx (443/80)
  ├── /              → Frontend/dist (React)
  ├── /api/v1/       → Gunicorn → Django WSGI
  ├── /admin/        → Gunicorn
  ├── /ckeditor5/    → Gunicorn
  ├── /static/       → Backend/staticfiles/
  └── /media/        → Backend/media/
```

---

## 1) DNS

Domain panelinde A kaydı:

| Host | Tip | Değer |
|------|-----|-------|
| `@`  | A   | SUNUCU_IP |
| `www`| A   | SUNUCU_IP |

---

## 2) MySQL

```bash
sudo mysql
```

```sql
CREATE DATABASE harbiqrmenu CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'harbiqrmenu'@'localhost' IDENTIFIED BY 'GUVENLI_SIFRE';
GRANT ALL PRIVILEGES ON harbiqrmenu.* TO 'harbiqrmenu'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 3) Kod (clone sonrası)

```bash
cd /home/ubuntu/harbiqrmenu
git pull
```

---

## 4) Ortam dosyaları

```bash
cp deploy/env/backend.env.example Backend/.env
cp deploy/env/frontend.env.example Frontend/.env
nano Backend/.env
```

Mutlaka düzenleyin:
- `DJANGO_SECRET_KEY` — uzun rastgele string
- `PROD_DB_PASSWORD` — MySQL şifresi
- `GROQ_API_KEY` vb.

---

## 5) İlk kurulum (tek sefer)

Scriptler Windows'tan kopyalandıysa önce satır sonlarını düzeltin:

```bash
sed -i 's/\r$//' deploy/scripts/*.sh
chmod +x deploy/scripts/*.sh
./deploy/scripts/initial-setup.sh
```

Superuser:

```bash
cd Backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py createsuperuser
```

---

## 6) Let's Encrypt (HTTPS)

Ubuntu 24.04'te `apt` certbot Python 3.13 ile bozulabiliyor (`_cffi_backend`).
**Snap sürümünü kullanın:**

DNS yayıldıktan sonra:

```bash
sudo apt remove -y certbot python3-certbot-nginx 2>/dev/null || true
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

sudo certbot --nginx -d harbi-kebap.com -d www.harbi-kebap.com
```

Snap kurulamazsa alternatif:

```bash
sudo apt install -y python3-cffi python3-cffi-backend libffi-dev python3-dev
sudo apt install --reinstall certbot python3-certbot-nginx python3-cryptography
sudo certbot --nginx -d harbi-kebap.com -d www.harbi-kebap.com
```

Otomatik yenileme testi:

```bash
sudo certbot renew --dry-run
```

---

## 7) Sonraki güncellemeler

Detayli rehber: [GUNCELLEME.md](../GUNCELLEME.md) (backend / frontend ayri ayri reload).

Windows'ta push ettikten sonra sunucuda (tam deploy):

```bash
cd /home/ubuntu/harbiqrmenu
./deploy/scripts/deploy.sh
```

---

## Kontrol

Gunicorn portu `Backend/.env` icindeki `PROD_RUNSERVER_PORT` degerinden okunur (ornegin `8526`).
Nginx upstream de ayni portu kullanir; port degisince:

```bash
bash deploy/scripts/render-nginx-config.sh
sudo cp deploy/systemd/qrmenu.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart qrmenu
sudo nginx -t && sudo systemctl reload nginx
```

| Adres | Açıklama |
|-------|----------|
| https://harbi-kebap.com | Menü sitesi |
| https://harbi-kebap.com/admin/ | Django admin |
| https://harbi-kebap.com/api/v1/access/status/ | API test |

Loglar:

```bash
sudo journalctl -u qrmenu -f
sudo tail -f /var/log/qrmenu/error.log
sudo tail -f /var/log/nginx/error.log
```

Servis:

```bash
sudo systemctl status qrmenu
sudo systemctl restart qrmenu
```

---

## Sorun giderme

**Certbot: sertifika alindi ama nginx'e kurulamadi**

Nginx'te `server_name harbi-kebap.com` blogu yoktu. Sertifika zaten `/etc/letsencrypt/live/harbi-kebap.com/` altinda:

```bash
cd /home/ubuntu/harbiqrmenu
sed -i 's/\r$//' deploy/scripts/*.sh
chmod +x deploy/scripts/*.sh
./deploy/scripts/finish-nginx-ssl.sh
```

Manuel:

```bash
sudo cp deploy/nginx/harbi-kebap.com.conf /etc/nginx/sites-available/harbi-kebap.com
sudo ln -sf /etc/nginx/sites-available/harbi-kebap.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**curl Cloudflare 404 donuyor**

Domain Cloudflare uzerinden gidiyor (`Server: cloudflare`). Cloudflare panelinde:

1. DNS → `A` kaydi `@` ve `www` → **sunucu IP**
2. SSL/TLS → **Full (strict)**
3. Kurulum sirasinda sorun olursa proxy'yi gecici **DNS only** (gri bulut) yapin

Sunucunun kendisini test edin (Cloudflare'i bypass):

```bash
curl -I http://SUNUCU_IP -H "Host: harbi-kebap.com"
curl -skI https://127.0.0.1 -H "Host: harbi-kebap.com"
```

**qrmenu.service bulunamadi**

`initial-setup.sh` tam bitmemis. `./deploy/scripts/finish-nginx-ssl.sh` calistirin.

**mysqlclient / pkg-config hatasi**

```bash
sudo apt update
sudo apt install -y pkg-config default-libmysqlclient-dev build-essential python3-dev
cd Backend
source venv/bin/activate
pip install -r requirements.txt
```

**Ana sayfa 500 / dist yok**

Nginx `Frontend/dist/index.html` bekler. Build basarisizsa klasor olusmaz.

**pnpm ERR_PNPM_IGNORED_BUILDS (esbuild / @tailwindcss/oxide)**

pnpm v10+ native build scriptlerini `allowBuilds` ile onaylar. `Frontend/pnpm-workspace.yaml` icinde
`esbuild: true` ve `'@tailwindcss/oxide': true` olmali (placeholder metin degil).

```bash
cd /home/ubuntu/harbiqrmenu
git pull
cd Frontend
pnpm install
pnpm run build
test -f dist/index.html && echo "dist OK"
sudo chmod -R a+rX dist
sudo nginx -t && sudo systemctl reload nginx
```

**Frontend CORS / loopback (127.0.0.1:48256) hatasi**

Production build yanlis API URL ile derlenmis. Tarayici `https://harbi-kebap.com` uzerinden
`http://127.0.0.1:48256` cagirmamali; `/api/v1` olmali.

```bash
cd /home/ubuntu/harbiqrmenu
git pull
echo 'VITE_API_BASE_URL=/api/v1' > Frontend/.env.production
cd Frontend
pnpm install
pnpm run build
sudo nginx -t && sudo systemctl reload nginx
```

Hard refresh: Ctrl+Shift+R

**502 / gunicorn 8000 portuna baglanmaya calisiyor**

`EnvironmentFile` kaldirildiktan sonra systemd `PROD_RUNSERVER_PORT` gormez; varsayilan 8000 kullanilir.
Servis artik `deploy/scripts/start-gunicorn.sh` ile `.env` portunu okur:

```bash
sudo systemctl stop qrmenu
sudo pkill -9 -f 'gunicorn.*config.wsgi' || true
sudo ss -tlnp | grep -E '8000|8526'

sed -i 's/\r$//' deploy/scripts/*.sh
bash deploy/scripts/render-nginx-config.sh
sudo cp deploy/systemd/qrmenu.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start qrmenu
sudo systemctl status qrmenu
curl -s http://127.0.0.1:8526/api/v1/access/status/ -H "Host: harbi-kebap.com" -H "X-Forwarded-Proto: https"
```

**API 500 / admin calisiyor ama API HTML 500**

systemd `EnvironmentFile` `.env` icindeki `$` karakterlerini bozar (ornegin `DJANGO_SECRET_KEY`).
Servis artik yalnizca Django `load_dotenv` kullanir. Sunucuda:

```bash
sudo cp deploy/systemd/qrmenu.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart qrmenu
```

Log:

```bash
sudo journalctl -u qrmenu -n 40 --no-pager
```

Shell test:

```bash
cd Backend && source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py shell -c "from api.services.frontend_access import is_frontend_public_access_enabled; print(is_frontend_public_access_enabled())"
```

`.env` icinde `PROD_DB_*` satirlari dolu olmali.

**Gunicorn crash loop / port 8000 meşgul**

```bash
sudo systemctl stop qrmenu
sudo pkill -9 -f 'gunicorn.*config.wsgi' || true
sudo ss -tlnp | grep 8000

cd /home/ubuntu/harbiqrmenu/Backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
gunicorn --bind 127.0.0.1:8000 config.wsgi:application
```

Hata yoksa Ctrl+C, servisi yeniden baslatin:

```bash
sudo cp deploy/systemd/qrmenu.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start qrmenu
```

Django test (Host header gerekli):

```bash
curl -sI http://127.0.0.1:8000/admin/ -H "Host: harbi-kebap.com"
curl -s http://127.0.0.1:8000/api/v1/access/status/ -H "Host: harbi-kebap.com"
```

**502 Bad Gateway** — Gunicorn calismiyor:
```bash
sudo systemctl status qrmenu
cd Backend && source venv/bin/activate && gunicorn config.wsgi:application
```

**504 Gateway Timeout (admin Groq çevir)** — İşlem uzun sürer; nginx ve gunicorn timeout artırılmış olmalı. Deploy sonrası:
```bash
sudo -u ubuntu -H bash /home/ubuntu/harbiqrmenu/deploy/scripts/deploy.sh
```
`Backend/.env` içinde isteğe bağlı: `GUNICORN_TIMEOUT=600`

**Admin CSS yok** — static toplanmamış:
```bash
cd Backend && source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py collectstatic --noinput
```

**Görsel yüklenirken 500 / görseller açılmıyor** — Gunicorn `ubuntu` ile çalışır; `media/` yazılabilir olmalı:

```bash
bash /home/ubuntu/harbiqrmenu/deploy/scripts/fix-upload-permissions.sh
sudo systemctl restart qrmenu
```

Eski (hatalı) komut `chown www-data:www-data Backend/media` admin yüklemelerini kırar; kullanmayın.

**413 Request Entity Too Large** — Nginx gövde limiti (varsayılan deploy: 25M). Daha büyük dosyalar için `deploy/nginx/harbi-kebap.com.conf` içinde `client_max_body_size` artırın, ardından `sudo nginx -t && sudo systemctl reload nginx`.
