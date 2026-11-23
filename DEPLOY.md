# Deploying Wise-Teck on the VPS

Day-to-day work (logging in, finding files, changing the code, putting it live, undoing an update):
[SERVER-ACCESS.md](SERVER-ACCESS.md).

Server: Ubuntu 24.04, `159.198.43.141`, logged in as `root` (PuTTY). Nginx is already running and serves
`dehleze.store`. **Do not edit or remove anything belonging to dehleze** (`/etc/nginx/sites-available/dehleze`,
its folders or its database). Everything below only adds new files.

The site is already live at https://wiseteck.dev. To bring a new version online, follow
**Update the live site** right below, and do **Server security** once. Sections 1–9 are the first-time setup, kept
for reference.

## Update the live site

Run these in PuTTY as `root`. They change only Wise-Teck; dehleze is not touched.

**Never overwrite** `/srv/wiseteck/.env` (passwords), `/srv/wiseteck/app/media/` (uploaded photos) or the database:
they exist only on the server. Updating the code and running `migrate` keeps all content edited in the admin.

### Step 1: back up

```
sudo -u postgres pg_dump wiseteck > /root/wiseteck-$(date +%F).sql
tar czf /root/wiseteck-media-$(date +%F).tgz -C /srv/wiseteck/app media
```

### Step 2: get the new code (choose A or B)

**A. From GitHub (recommended)**

```
cd /srv/wiseteck/app
git status            # must say "nothing to commit"; if not, stop and ask
git pull origin main
```

**B. From the zip file**: copy the zip to `/root/` with WinSCP, then:

```
apt install -y unzip rsync
cd /root && rm -rf wiseteck-new && unzip -q wise-teck-site.zip -d wiseteck-new
rsync -a --exclude media/ --exclude staticfiles/ --exclude .env --exclude db.sqlite3 wiseteck-new/ /srv/wiseteck/app/
cp -r wiseteck-new/media/seed /srv/wiseteck/app/media/     # seed photos only (sharper versions); uploads are not touched
```

The server folder is also a GitHub copy, so after a zip update `git status` lists changed files; that is expected.
To go back to A later: `git fetch origin && git reset --hard origin/main` in `/srv/wiseteck/app` (`.env`, uploads
and the database are not in GitHub and are kept).

### Step 3: install, update the database, restart

```
cd /srv/wiseteck/app
set -a; . /srv/wiseteck/.env; set +a
../venv/bin/pip install -r requirements.txt
../venv/bin/python manage.py migrate
../venv/bin/python manage.py check --deploy
../venv/bin/python manage.py collectstatic --noinput
../venv/bin/python manage.py make_image_variants
chown -R www-data:www-data /srv/wiseteck/app/media
systemctl restart wiseteck
systemctl status wiseteck --no-pager
```

`check --deploy` must end with "no issues (1 silenced)".

What this release (23 November 2026) changes on the server:

- `migrate` adds one table (`0019_lighthouse_run`) for the daily Lighthouse results. No content is changed.
- No new Python packages. `collectstatic` picks up the new CSS and JavaScript (menu button, smooth hovers, top bar
  alignment, Lighthouse panel). New address: `/llms.txt`.
- Optional, once: switch on the Lighthouse panel (*Daily Lighthouse check* below).

### Daily Lighthouse check (once)

The check itself runs on GitHub every day; this lets its results appear on the admin dashboard.

```
openssl rand -hex 32                                   # copy the value it prints
nano /srv/wiseteck/.env                                # add a line: LIGHTHOUSE_TOKEN=<that value>
systemctl restart wiseteck
```

Then on GitHub: repository **Settings → Secrets and variables → Actions → New repository secret**, name
`LIGHTHOUSE_TOKEN`, the same value. Start the first check at once: **Actions → Lighthouse → Run workflow**; the
dashboard's *Speed & quality* panel fills in when it finishes (about 15 minutes). The workflow checks
`https://wiseteck.dev`; to check another address, set a repository *variable* `SITE_URL`.

### Step 4: Nginx improvements (once)

Open the Wise-Teck site file only: `nano /etc/nginx/sites-available/wiseteck` (never the dehleze file).

1. Inside the `server { ... }` block that has `listen 443 ssl`, add near the top:

   ```
   server_tokens off;
   gzip on;
   gzip_types text/css application/javascript application/json image/svg+xml application/xml text/plain font/woff2;
   gzip_min_length 1024;
   if ($host = www.wiseteck.dev) { return 301 https://wiseteck.dev$request_uri; }
   ```

   In the same block, replace the two `location /static/` and `location /media/` lines with:

   ```
   location /static/ { alias /srv/wiseteck/app/staticfiles/; expires 1y; add_header Cache-Control "public, immutable"; add_header X-Content-Type-Options nosniff; }
   location /media/  { alias /srv/wiseteck/app/media/; expires 30d; add_header Cache-Control "public"; add_header X-Content-Type-Options nosniff; add_header Content-Security-Policy "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; sandbox"; }
   ```

   (Static files carry a version in their address, so browsers may keep them for a year. The `/media/` policy
   stops an uploaded file from ever running code when opened on its own.)

   Keep the existing `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` line in `location /`: the rate
   limits and visitor statistics read the visitor's address from it.

2. Save, then check and reload:

   ```
   nginx -t && systemctl reload nginx
   ```

`nginx -t` must say "syntax is ok"; if not, undo the edit before reloading.

### Step 5: check

- https://wiseteck.dev opens; the menu, logo and pages look right on a phone.
- https://www.wiseteck.dev goes to https://wiseteck.dev.
- https://wiseteck.dev/admin/ signs in.
- https://dehleze.store still works.

If something goes wrong: `journalctl -u wiseteck -n 50 --no-pager` shows the error. To go back to the previous version,
use `git checkout <previous commit>` and restart (or restore the backups from step 1).

## Server security (do this first)

A read-only check on 21 Nov 2026 found **9,227 failed root password guesses over SSH in 24 hours**, root login with a
password allowed, no firewall and no fail2ban. Nothing showed a break-in (only the owner's and the developer's
addresses had logged in), but a simple root password will not hold against that. These steps do not touch the
websites; run them in PuTTY as `root`, one block at a time.

**1. Block password guessers (fail2ban).** Bans an address for an hour after 5 wrong SSH passwords.

```
apt install -y fail2ban
printf '[sshd]\nenabled = true\nmaxretry = 5\nbantime = 1h\n' > /etc/fail2ban/jail.d/sshd.local
systemctl enable --now fail2ban
fail2ban-client status sshd
```

**2. Firewall.** Only SSH and the websites (both sites use 80 and 443).

```
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
ufw status
```

**3. SSH login.** Best: sign in with SSH keys only. Root already has two keys in `/root/.ssh/authorized_keys`; once
everyone who needs the server can sign in with a key, turn passwords off:

```
printf 'PasswordAuthentication no\nPermitRootLogin prohibit-password\n' > /etc/ssh/sshd_config.d/10-keys-only.conf
sshd -t && systemctl reload ssh
```

Keep the current PuTTY window open and test a new key login before closing it. Until keys are set up, at least
change the root password to a long random one: `passwd`.

**4. Security updates.** Automatic updates are on, and some need a restart (`/var/run/reboot-required` exists).
Reboot at a quiet hour (both sites are down for about a minute): `reboot`.

**5. Backups.** There were none. Daily database + photos, kept 14 days:

```
cat > /root/backup-wiseteck.sh <<'EOF'
#!/bin/sh
# Daily backup of the Wise-Teck database and uploaded photos; keeps 14 days.
set -e
D=/root/backups; mkdir -p "$D"
sudo -u postgres pg_dump wiseteck | gzip > "$D/wiseteck-$(date +%F).sql.gz"
tar czf "$D/wiseteck-media-$(date +%F).tgz" --exclude=media/_v -C /srv/wiseteck/app media
find "$D" -name 'wiseteck-*' -mtime +14 -delete
EOF
chmod 700 /root/backup-wiseteck.sh && /root/backup-wiseteck.sh && ls -lh /root/backups
echo '30 2 * * * root /root/backup-wiseteck.sh' > /etc/cron.d/wiseteck-backup
```

Copy `/root/backups` to another place now and then (WinSCP to a PC or Google Drive): a backup on the same server
does not survive the server.

**Also found:** the HTTPS certificate of **dehleze.store** expired on 12 Nov 2026 (wiseteck.dev's is valid until
Feb 2027 and renews itself). That site belongs to someone else; tell its owner rather than changing its settings.

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
`../venv/bin/python manage.py createsuperuser`. Change the password to a strong one before the site is announced:
`../venv/bin/python manage.py changepassword admin`.

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

See **Update the live site** at the top. Never run `seed_content --reset` on the live server: it replaces the
client's edits.

## Backups

Daily automatic backups: see **Server security → 5. Backups**. A one-off backup before a risky change:

```
sudo -u postgres pg_dump wiseteck > /root/wiseteck-$(date +%F).sql
tar czf /root/wiseteck-media-$(date +%F).tgz -C /srv/wiseteck/app media
```

Restore: `sudo -u postgres psql wiseteck < /root/wiseteck-<date>.sql` and unpack the media archive into
`/srv/wiseteck/app/`.
