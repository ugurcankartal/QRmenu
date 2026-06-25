# QRmenu — Production güncelleme rehberi

Sunucu yolu: `/home/ubuntu/harbiqrmenu`  
Domain: https://harbi-kebap.com

İlk kurulum için: [deploy/DEPLOY.md](deploy/DEPLOY.md)

---

## Genel akış

1. **Windows’ta** değişikliği yap → `git commit` → `git push origin main`
2. **Sunucuda** deploy script veya `git pull` + ilgili adımlar

> **Cursor / AI agent kuralı:** Kod, migration, frontend veya deploy script değişikliği tamamlandığında **her zaman** yerel repoda commit + `git push origin main` yap. Kullanıcı ayrıca istemedikçe push atlama; push sonrası kısa commit hash’ini bildir. Sunucuda commit yapma — sunucu yalnızca `git pull` / `deploy.sh` ile güncellenir.

---

## Backend (Django / REST API) değişince

Python kodu, model, migration, API view vb. değiştiğinde **Gunicorn yeniden başlatılmalı**. Kod otomatik yüklenmez.

### Sadece backend (hızlı)

```bash
cd /home/ubuntu/harbiqrmenu
git pull

cd Backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod

# requirements.txt degistiysa:
pip install -r requirements.txt

# model / migration degistiysa:
python manage.py migrate --noinput

# admin CSS/JS veya collectstatic gerektiren degisiklik varsa:
python manage.py collectstatic --noinput

sudo systemctl restart qrmenu
```

### Kontrol

```bash
sudo systemctl status qrmenu
curl -s https://harbi-kebap.com/api/v1/access/status/
```

### Log

```bash
sudo journalctl -u qrmenu -n 30 --no-pager
sudo tail -f /var/log/qrmenu/error.log
```

### Ne zaman ne yapılır?

| Değişiklik türü | Ekstra adım |
|-----------------|-------------|
| Sadece `.py` (view, serializer, service) | `sudo systemctl restart qrmenu` yeter |
| Model + migration | `migrate` + `restart qrmenu` |
| `requirements.txt` | `pip install -r requirements.txt` + `restart qrmenu` |
| Admin static / `STATIC_ROOT` | `collectstatic` + `restart qrmenu` |
| `.env` (port, DB, secret) | `restart qrmenu`; port değiştiyse aşağıdaki port bölümüne bakın |

### Port değiştiğinde (`PROD_RUNSERVER_PORT`)

Gunicorn portu `Backend/.env` içindeki `PROD_RUNSERVER_PORT` değerinden okunur (ör. `8526`).

```bash
cd /home/ubuntu/harbiqrmenu
bash deploy/scripts/render-nginx-config.sh
sudo cp deploy/systemd/qrmenu.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart qrmenu
sudo nginx -t && sudo systemctl reload nginx
```

---

## Frontend (React) değişince

React **build edilir**; Nginx `Frontend/dist/` klasörünü sunar. Kaynak kod değişince **yeniden build** gerekir. Gunicorn restart gerekmez.

### Sadece frontend (hızlı)

```bash
cd /home/ubuntu/harbiqrmenu
git pull

cd Frontend
pnpm install          # package.json / lockfile degistiyse
pnpm run build

sudo chmod -R a+rX dist
```

Nginx genelde **reload gerekmez** — `dist/` güncellenince yeni dosyalar hemen servis edilir.

### Tarayıcıda eski sürüm görünürse

- **Ctrl+Shift+R** (hard refresh)
- Cloudflare kullanıyorsanız: **Caching → Purge Everything**

### Kontrol

```bash
test -f dist/index.html && echo "dist OK"
grep -r "127.0.0.1:48256" dist/ || echo "API URL OK"
```

Production’da tarayıcı API’yi **`/api/v1`** üzerinden çağırmalı; `127.0.0.1:48256` yalnızca yerel geliştirme içindir.

---

## Her ikisi birden (tam deploy)

Backend + frontend + migrate + collectstatic + servis restart:

```bash
cd /home/ubuntu/harbiqrmenu
sudo bash deploy/scripts/deploy.sh
```

> **Not:** Script'i `sudo -u ubuntu` ile değil, **root olarak** (`sudo bash ...`) çalıştırın; böylece `dist/` gibi root'un yazdığı dosyaların sahipliği otomatik düzeltilir.

---

## Yerel geliştirme (Windows)

| Taraf | Komut | Reload |
|-------|--------|--------|
| Backend | `python manage.py runserver` (dev port) | Otomatik |
| Frontend | `pnpm dev` (Vite) | Otomatik (HMR) |

Production’a almak için: push → sunucuda yukarıdaki adımlar.

---

## Özet tablo

| Ne değişti? | Sunucuda ne yap? |
|-------------|------------------|
| Django API / model | `migrate` (gerekirse) + `sudo systemctl restart qrmenu` |
| React UI | `pnpm run build` |
| Her ikisi | `./deploy/scripts/deploy.sh` |

---

## Faydalı adresler

| Adres | Açıklama |
|-------|----------|
| https://harbi-kebap.com | Menü sitesi |
| https://harbi-kebap.com/admin/ | Django admin |
| https://harbi-kebap.com/api/v1/access/status/ | API test |
