# Deploying Wise-Teck v3 (Django) on the VPS

Server: Ubuntu 24.04, `159.198.43.141`, logged in as `root` (PuTTY). Nginx is already running and serves
`dehleze.store`. **Do not edit or remove anything belonging to dehleze** (`/etc/nginx/sites-available/dehleze`,
its folders or its database). Everything below only adds new files.

Replace `wiseteck.dev` with the real domain everywhere.

## 1. Packages

```
apt update
apt install -y python3-venv python3-dev git postgresql libpq-dev
```

## 2. PostgreSQL database

```
sudo -u postgres psql -c "CREATE USER wiseteck WITH PASSWORD 'CHOOSE-A-STRONG-PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE wiseteck OWNER wiseteck;"
```

## 3. Code and Python environment

```
mkdir -p /srv/wiseteck && cd /srv/wiseteck
git clone <REPO-URL> app
python3 -m venv venv
venv/bin/pip install -r app/requirements.txt
```

## 4. Settings file

```
cat > /srv/wiseteck/.env <<'EOF'
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=PASTE-A-LONG-RANDOM-STRING
DJANGO_ALLOWED_HOSTS=wiseteck.dev,www.wiseteck.dev
DJANGO_CSRF_TRUSTED_ORIGINS=https://wiseteck.dev,https://www.wiseteck.dev
POSTGRES_DB=wiseteck
POSTGRES_USER=wiseteck
POSTGRES_PASSWORD=CHOOSE-A-STRONG-PASSWORD
EOF
chmod 600 /srv/wiseteck/.env
```

To make a secret key: `venv/bin/python -c "import secrets; print(secrets.token_urlsafe(50))"`.

For contact-form email alerts, add `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`,
then set the alert address in Admin → Site Settings.

## 5. Database tables, content, admin user, static files

```
cd /srv/wiseteck/app
set -a; . /srv/wiseteck/.env; set +a
../venv/bin/python manage.py migrate
../venv/bin/python manage.py seed_content
../venv/bin/python manage.py copy_original_admins --db /srv/wiseteck/original-db.sqlite3   # same login as the original site
../venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data /srv/wiseteck/app/media
```

For the admin login: copy the original site's `db.sqlite3` (from `D:\wise teck site\wise_teck ORIGINAL\`) to
`/srv/wiseteck/original-db.sqlite3` first (e.g. with WinSCP), and delete it after the command. Or create a new login with
`../venv/bin/python manage.py createsuperuser`. Change the password to a strong one before going live
(Django admin at `/django-admin/` → Users, or `manage.py changepassword admin`).

To bring content edited locally instead of the fresh seed: on the PC run
`py manage.py dumpdata --exclude contenttypes --exclude auth.permission --exclude sessions --indent 1 > content.json`,
copy `content.json` and the `media/` folder to the server, then `../venv/bin/python manage.py loaddata content.json`.

## 6. Gunicorn service

```
cat > /etc/systemd/system/wiseteck.service <<'EOF'
[Unit]
Description=Wise-Teck website (Django)
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/wiseteck/app
EnvironmentFile=/srv/wiseteck/.env
ExecStart=/srv/wiseteck/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8100 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now wiseteck
systemctl status wiseteck --no-pager
```

### Scheduled publishing timer

Drafts with a "Go live at" time are published on the next visit after that time. To make it exact even when
nobody visits, run the check every minute:

```
cat > /etc/systemd/system/wiseteck-publish.service <<'EOF'
[Unit]
Description=Wise-Teck: publish scheduled drafts

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/srv/wiseteck/app
EnvironmentFile=/srv/wiseteck/.env
ExecStart=/srv/wiseteck/venv/bin/python manage.py publish_scheduled
EOF
cat > /etc/systemd/system/wiseteck-publish.timer <<'EOF'
[Unit]
Description=Wise-Teck: check scheduled drafts every minute

[Timer]
OnCalendar=*-*-* *:*:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now wiseteck-publish.timer
```

## 7. Nginx site (next to dehleze)

```
cat > /etc/nginx/sites-available/wiseteck <<'EOF'
server {
    listen 80;
    server_name wiseteck.dev www.wiseteck.dev;
    client_max_body_size 20M;

    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml application/xml text/plain;
    gzip_min_length 1024;

    location /static/ { alias /srv/wiseteck/app/staticfiles/; expires 30d; add_header Cache-Control "public"; }
    location /media/  { alias /srv/wiseteck/app/media/; expires 30d; add_header Cache-Control "public"; }

    location / {
        proxy_pass http://127.0.0.1:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
ln -s /etc/nginx/sites-available/wiseteck /etc/nginx/sites-enabled/wiseteck
nginx -t && systemctl reload nginx
```

`nginx -t` must say "syntax is ok". If not, stop and fix before reloading.

## 8. Domain and HTTPS

DNS (at the domain's registrar): A record `@` → `159.198.43.141`, A record `www` → `159.198.43.141`.
When `getent hosts wiseteck.dev` shows the IP:

```
apt install -y certbot python3-certbot-nginx
certbot --nginx -d wiseteck.dev -d www.wiseteck.dev
```

Then check https://wiseteck.dev, https://wiseteck.dev/admin/ and that https://dehleze.store still works.

## 9. Search engines (after HTTPS works)

1. Admin → Site Settings → **Main web address**: `https://wiseteck.dev` (canonical links, sitemap and link previews use it).
2. Check https://wiseteck.dev/robots.txt and https://wiseteck.dev/sitemap.xml open.
3. Google Search Console → add the property `https://wiseteck.dev` → verify (paste the code into Site Settings →
   Google Search Console code) → Sitemaps → submit `sitemap.xml`.
4. Optional checks: https://search.google.com/test/rich-results (structured data) and https://pagespeed.web.dev (speed).

## Updating later

```
cd /srv/wiseteck/app && git pull
set -a; . /srv/wiseteck/.env; set +a
../venv/bin/pip install -r requirements.txt
../venv/bin/python manage.py migrate
../venv/bin/python manage.py collectstatic --noinput
systemctl restart wiseteck
```

Never run `seed_content --reset` on the live server: it replaces the client's edits.

## Backups

```
sudo -u postgres pg_dump wiseteck > /root/wiseteck-$(date +%F).sql
tar czf /root/wiseteck-media-$(date +%F).tgz -C /srv/wiseteck/app media
```
