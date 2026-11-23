# Server access and code changes

How to get into the Wise-Teck server, find your way around it, and change the website's code safely. Every command
you need is here, in the order you use it. Server setup, security hardening and backups: [DEPLOY.md](DEPLOY.md).

> This repository is public. Never write a password, the contents of `.env` or any secret into this file, a commit
> or an issue.

## Quick start: the five things you will do most

Type these in **PowerShell** on your PC (lines starting with `#` are notes, not commands).

### 1. Log in to the server

```powershell
ssh root@159.198.43.141
# type the root password (nothing shows while typing), press Enter
```

### 2. Go to the website's folder and look around

```bash
cd /srv/wiseteck/app        # the website's code
ls                          # list what is there
git log --oneline -3        # which version is live (top line)
```

### 3. Read a file

```bash
less templates/sections/home_hero.html     # arrows to scroll, q to quit
grep -rn "Apply Now" templates core        # find where some text or code is
```

Or open WinSCP (section 1), go to `/srv/wiseteck/app` and double-click a file.

### 4. Update the website with the zip

On your PC, in PowerShell, from the project folder `D:\Inner Pages\wise-teck-v3-django`:

```powershell
git archive --format=zip -o "D:\Inner Pages\wise-teck-site.zip" main     # make the zip from the main version
scp "D:\Inner Pages\wise-teck-site.zip" root@159.198.43.141:/root/      # send it to the server
ssh root@159.198.43.141                                                  # log in
```

Then on the server, one block at a time:

```bash
# a. back up first
sudo -u postgres pg_dump wiseteck > /root/wiseteck-$(date +%F).sql
tar czf /root/wiseteck-media-$(date +%F).tgz -C /srv/wiseteck/app media

# b. unpack the zip and copy the new code in (keeps .env, uploaded photos and the database)
apt install -y unzip rsync          # needed once; quick if already installed
cd /root && rm -rf wiseteck-new && unzip -q wise-teck-site.zip -d wiseteck-new
rsync -a --exclude media/ --exclude staticfiles/ --exclude .env --exclude db.sqlite3 wiseteck-new/ /srv/wiseteck/app/
cp -r wiseteck-new/media/seed /srv/wiseteck/app/media/

# c. install, update the database, restart
cd /srv/wiseteck/app
set -a; . /srv/wiseteck/.env; set +a
../venv/bin/pip install -r requirements.txt
../venv/bin/python manage.py migrate
../venv/bin/python manage.py check --deploy
../venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data /srv/wiseteck/app/media
systemctl restart wiseteck
systemctl status wiseteck --no-pager       # must say "active (running)"
```

### 5. Check the site and leave

```bash
curl -I https://wiseteck.dev               # "200" means the site answers
exit                                       # log out of the server
```

The rest of this file explains each of these in more detail, and covers changing the code, undoing an update and
emergencies.

## What each tool is and why we use it

| Tool | What it is | Why we use it |
| --- | --- | --- |
| `ssh` (PowerShell) / PuTTY | A secure remote login to the server | To type commands on the server from your PC; everything sent is encrypted |
| WinSCP | A file browser for the server | To see, read and copy the server's files like in Windows Explorer |
| `scp` | Secure file copy | To send the update zip to the server (or bring files back) |
| Git | Version tracking for code | Every change is recorded and can be undone; the server can update with `git pull` |
| GitHub | Online home of the code | The master copy; it runs all the tests on every change and the daily Lighthouse check |
| `git archive` / zip / `unzip` / `rsync` | Packing and copying code | The zip method: pack `main`, unpack on the server, copy only the code over the old code (rsync), leaving passwords, photos and the database alone |
| Nginx | The web server in front | HTTPS padlock, sends photos and CSS fast, passes pages to the website program, keeps the two websites on this server apart |
| Gunicorn + Django | The website program | Django is the site's code; Gunicorn runs several copies so many visitors are served at once |
| `systemctl` | Starts and stops background services | To restart the site (`wiseteck`) or Nginx, and to see if they are running |
| `journalctl` | Reads the system's logs | To see errors and who tried to log in |
| PostgreSQL / `pg_dump` | The database / its backup tool | Holds all content edited in the admin; `pg_dump` saves a copy of it |
| `cron` | Runs jobs on a timetable | Makes the daily backup at 02:30 UTC without anyone doing anything |
| fail2ban | Watches failed logins and blocks the sender | Bots try about 10,000 passwords a day; after 5 wrong tries an address is blocked for an hour, longer if it returns |
| `ufw` | The firewall | Only SSH (22) and the websites (80, 443) can be reached from the internet; everything else is closed |
| `.env` | The settings file with passwords | Keeps secrets out of the code, so the code can be public on GitHub |

## What is in the zip (the important files)

| File or folder | What it is |
| --- | --- |
| `SERVER-ACCESS.md` | This guide |
| `DEPLOY.md` | Server setup, security, backups, switching on Lighthouse |
| `README.md` | What the site does, the admin, SEO, Lighthouse, running it locally, tests |
| `CHANGELOG.md` | Every change, the decisions, and which version is live |
| `CLAUDE.md` | Project rules and commands (for developers and AI coding sessions) |
| `manage.py` | The command used to run Django tasks: `migrate`, `collectstatic`, `check --deploy`… |
| `requirements.txt` | The exact Python packages the site needs (installed with `pip install -r`) |
| `config/settings.py` | Site settings; reads passwords from `.env` on the server |
| `config/urls.py` | Which web address goes to which page or feature |
| `core/models.py` | The database tables: pages, sections, blog, stories, courses, settings… |
| `core/views.py` | What each address shows (pages, contact form, sitemap, `llms.txt`, Lighthouse results) |
| `core/migrations/` | Database updates, applied by `manage.py migrate` |
| `core/adminpanel/` | The admin panel at `/admin/` |
| `core/lighthouse.py`, `core/seo.py`, `core/seo_audit.py` | Lighthouse panel; search-engine tags; the SEO health check |
| `core/tests/` | The automatic tests (108) |
| `templates/` | The HTML of every page; `templates/sections/` has one file per section type |
| `static/css/wise-teck.css` | The website's one stylesheet |
| `static/css/adminpanel.css` | The admin panel's stylesheet |
| `static/js/` | Scripts: menu, waves, 3D coin |
| `media/seed/` | The starting photos (photos uploaded in the admin live only on the server) |
| `.github/workflows/` | GitHub jobs: tests on every change (`ci.yml`), daily Lighthouse (`lighthouse.yml`) |
| `tools/lighthouse/run.mjs` | The Lighthouse runner used by that daily job |

Not in the zip, and never overwritten by an update: `/srv/wiseteck/.env` (passwords), `/srv/wiseteck/app/media/`
(uploaded photos) and the database. They exist only on the server.

## Quick facts

| What | Value |
| --- | --- |
| Server address | `159.198.43.141` (Namecheap VPS, Ubuntu 24.04) |
| Login | `root`, password auth (ask the site owner for the password) |
| Website | <https://wiseteck.dev> (also <https://www.wiseteck.dev>) |
| Website admin | <https://wiseteck.dev/admin/> (its own login, separate from the server) |
| Code on the server | `/srv/wiseteck/app` |
| Settings and passwords | `/srv/wiseteck/.env` (never overwrite, never commit) |
| Uploaded photos | `/srv/wiseteck/app/media/` (only on the server) |
| Python environment | `/srv/wiseteck/venv` |
| Site service | `wiseteck` (Gunicorn running Django) |
| Database | PostgreSQL, database and user `wiseteck` |
| Nginx file for this site | `/etc/nginx/sites-available/wiseteck` |
| Master copy of the code | <https://github.com/Engineer00/wise_teck_v3> (branch `main` = what goes live) |
| Working copy on the dev PC | `D:\Inner Pages\wise-teck-v3-django` |

**Logins we have:** the server's root password and the website admin. **Logins we don't have:** the Namecheap
account (reboot from outside, emergency console, root password reset, renewal) and the Porkbun account (DNS, domain
renewal). Those belong to the client; contact them if the server stops answering or you are locked out.

**Never touch:** the other website on this server, `dehleze.store` (`/home/dehleze/`,
`/etc/nginx/sites-available/dehleze`, its database). Never press *Reinstall OS* in Namecheap: it wipes both sites.

---

## 1. Connect to the server

### PowerShell (built into Windows 10 and 11)

```powershell
ssh root@159.198.43.141
```

- The first time it asks *Are you sure you want to continue connecting?*: type `yes`.
- Type the password when asked. Nothing appears while you type; press Enter.
- You are in when the prompt shows `root@...:~#`.
- Leave with `exit`.

### PuTTY

Host Name `159.198.43.141`, Port `22`, Connection type SSH → **Open** → log in as `root` → password.

### WinSCP (folders on screen, drag and drop)

New Site → File protocol **SFTP**, Host name `159.198.43.141`, Port `22`, User name `root`, Password → **Login**.
Your PC is on the left, the server on the right. Double-click a file to view it; drag files to copy them.

### Copy files between the PC and the server (PowerShell)

```powershell
# PC -> server (for example the update zip)
scp "D:\Inner Pages\wise-teck-site.zip" root@159.198.43.141:/root/

# server -> PC (one file)
scp root@159.198.43.141:/srv/wiseteck/app/core/views.py "D:\server-files\"

# server -> PC (the whole site folder, including uploaded photos)
scp -r root@159.198.43.141:/srv/wiseteck/app "D:\server-copy"
```

---

## 2. Find your way around

```bash
cd /srv/wiseteck/app          # go to the site's code
pwd                           # where am I?
ls                            # list files and folders
ls -la                        # the same, with hidden files, sizes and dates
cd core                       # into a folder;  cd ..  goes back up one level
less core/views.py            # read a file (arrows to scroll, / to search, q to quit)
grep -rn "Apply Now" templates core     # find text in the code
du -sh media                  # size of the uploaded photos
```

What is where in the code:

| Folder / file | What it holds |
| --- | --- |
| `config/settings.py` | Settings (read from `/srv/wiseteck/.env` on the server) |
| `core/models.py` | Database tables: pages, sections, blog, stories, settings… |
| `core/views.py` | What each web address shows |
| `core/adminpanel/` | The admin panel |
| `templates/` | The HTML of every page and section type |
| `static/css/wise-teck.css` | The site's one stylesheet |
| `static/js/` | The site's scripts (menu, waves, 3D coin) |
| `core/tests/` | The automatic tests |

Which version is live, and is anything changed on the server?

```bash
cd /srv/wiseteck/app
git log --oneline -5          # the live version is the top line
git status                    # must say "nothing to commit, working tree clean"
git diff                      # if not clean: shows exactly what was changed on the server
```

---

## 3. Check the site is healthy

```bash
systemctl status wiseteck --no-pager          # must say "active (running)"
journalctl -u wiseteck -n 50 --no-pager       # the site's last 50 log lines (errors appear here)
journalctl -u wiseteck -f                     # follow the log live (Ctrl+C to stop)
systemctl restart wiseteck                    # restart the site
nginx -t                                      # check Nginx settings ("syntax is ok")
systemctl reload nginx                        # apply Nginx changes (only after nginx -t passes)
tail -n 50 /var/log/nginx/error.log           # Nginx errors
curl -I https://wiseteck.dev                  # the site answers? (look for "200 OK")
df -h                                         # free disk space
free -h                                       # free memory
uptime                                        # how long the server has run, and its load
```

Security on the server (set up on 23 November 2026):

```bash
fail2ban-client status sshd                   # how many addresses are blocked right now
fail2ban-client set sshd unbanip <address>    # unblock someone who typed the password wrong 5 times
ufw status                                    # the firewall: only 22, 80 and 443 open
ls -lh /root/backups                          # the daily backups (database + photos, last 14 days)
/root/backup-wiseteck.sh                      # make a backup now
```

If **you** get "Connection refused" or "timed out" after several wrong passwords, fail2ban has blocked your address
for an hour. Wait, or ask someone else who can log in to unblock you (find your address at <https://api.ipify.org>).

Run Django's own commands on the server (always load the settings first):

```bash
cd /srv/wiseteck/app
set -a; . /srv/wiseteck/.env; set +a
../venv/bin/python manage.py check --deploy          # production checklist: "no issues (1 silenced)"
../venv/bin/python manage.py showmigrations core     # database updates applied ([X]) or not ([ ])
../venv/bin/python manage.py changepassword admin    # new password for the website admin user "admin"
```

---

## 4. Change the code (the right way)

Changes are made on a PC, tested, sent to GitHub, and then the server is updated from GitHub (or a zip). Never edit
code on the server: the next update overwrites it.

### 4.1 Get the code on your PC (once)

Needs [Git](https://git-scm.com/download/win) and [Python 3.13](https://www.python.org/downloads/).

```powershell
git clone https://github.com/Engineer00/wise_teck_v3.git
cd wise_teck_v3
py -3.13 -m pip install -r requirements-dev.txt
py -3.13 manage.py migrate
py -3.13 manage.py seed_content           # test content and photos (not the live content)
py -3.13 manage.py createsuperuser        # your local admin login
```

On the dev PC the code is already in `D:\Inner Pages\wise-teck-v3-django`. Set the project's Git identity once per
copy, as listed in [CLAUDE.md](CLAUDE.md) → Commits.

### 4.2 Start from the latest version, on a new branch

```powershell
git checkout main
git pull origin main
git checkout -b fix/short-description     # e.g. fix/footer-phone-number
```

### 4.3 Run the site locally and make the change

```powershell
py -3.13 manage.py runserver 127.0.0.1:8010
```

Open <http://127.0.0.1:8010/> (site) and <http://127.0.0.1:8010/admin/> (admin). Edit the files in any editor (VS Code);
the local site reloads by itself. Stop it with Ctrl+C.

- Wording, photos, menus and colours are content: change them in the live admin, not in code.
- Styles go only in `static/css/wise-teck.css`, using its tokens. Conventions: [CLAUDE.md](CLAUDE.md).
- Changed `core/models.py`? Create the database update: `py -3.13 manage.py makemigrations core`, then `migrate`.

### 4.4 Test before sending

```powershell
py -3.13 manage.py test core              # all tests must pass ("OK")
py -3.13 -m ruff check .                  # code checks
py -3.13 -m ruff format .                 # tidy formatting
```

### 4.5 Send it to GitHub

```powershell
git status                                # what changed
git diff                                  # the changes line by line
git add <file> <file>                     # the files to include (never .env or db.sqlite3)
git commit -m "Footer: new phone number"  # plain description, no AI attribution
git push -u origin fix/short-description
```

GitHub runs all the tests automatically (repository → **Actions** → green tick). Then merge into `main`:

- on GitHub: open the branch → **Compare & pull request** → **Create pull request** → **Merge**, or
- on the PC:

  ```powershell
  git checkout main
  git pull origin main
  git merge --ff-only fix/short-description
  git push origin main
  ```

### 4.6 Put it live

Log in to the server (section 1) and back up first:

```bash
sudo -u postgres pg_dump wiseteck > /root/wiseteck-$(date +%F).sql
tar czf /root/wiseteck-media-$(date +%F).tgz -C /srv/wiseteck/app media
```

#### Option A: from GitHub (recommended)

```bash
cd /srv/wiseteck/app
git status                      # must be clean; if not, stop and look at "git diff" first
git pull --ff-only origin main
```

#### Option B: from a zip

On the PC, build the zip from `main` (in the project folder), then copy it up:

```powershell
git archive --format=zip -o "D:\Inner Pages\wise-teck-site.zip" main
scp "D:\Inner Pages\wise-teck-site.zip" root@159.198.43.141:/root/
```

On the server:

```bash
apt install -y unzip rsync
cd /root && rm -rf wiseteck-new && unzip -q wise-teck-site.zip -d wiseteck-new
rsync -a --exclude media/ --exclude staticfiles/ --exclude .env --exclude db.sqlite3 wiseteck-new/ /srv/wiseteck/app/
cp -r wiseteck-new/media/seed /srv/wiseteck/app/media/
```

(After a zip update `git status` on the server lists changed files; that is expected. To return to option A:
`git fetch origin && git reset --hard origin/main`.)

#### Then, for both options

```bash
cd /srv/wiseteck/app
set -a; . /srv/wiseteck/.env; set +a
../venv/bin/pip install -r requirements.txt
../venv/bin/python manage.py migrate
../venv/bin/python manage.py check --deploy
../venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data /srv/wiseteck/app/media
systemctl restart wiseteck
systemctl status wiseteck --no-pager
```

### 4.7 Check it worked

- `systemctl status wiseteck --no-pager` says **active (running)**.
- <https://wiseteck.dev> and <https://wiseteck.dev/admin/> open; look at the page you changed on a phone too.
- <https://dehleze.store> still opens.
- If something is wrong: `journalctl -u wiseteck -n 50 --no-pager` shows the error.

---

## 5. Undo a bad update

Go back to the previous code version:

```bash
cd /srv/wiseteck/app
git log --oneline -5                     # find the previous version's code (second line)
git checkout <previous-code>             # e.g. git checkout 7b9f1ca
systemctl restart wiseteck
```

When the fix is ready on GitHub, return to the normal state with `git checkout main && git pull --ff-only origin main`
and run the "Then, for both options" block again.

Restore the database from a backup (this throws away every admin edit made after the backup; do it only if the
update damaged the content):

```bash
systemctl stop wiseteck
sudo -u postgres dropdb wiseteck
sudo -u postgres createdb -O wiseteck wiseteck
sudo -u postgres psql wiseteck < /root/wiseteck-<date>.sql
systemctl start wiseteck
```

Restore uploaded photos: `tar xzf /root/wiseteck-media-<date>.tgz -C /srv/wiseteck/app`.

---

## 6. Emergency fix on the server (only when the site is down)

If the site is broken and there is no time for the normal route:

```bash
cd /srv/wiseteck/app
nano <file>                              # edit (Ctrl+O, Enter to save; Ctrl+X to exit)
systemctl restart wiseteck
git diff                                 # copy this change
```

Then make the same change on the PC and send it through section 4 the same day, and reset the server copy with
`git checkout -- <file>` before the next update. Otherwise `git pull` refuses to run, or the fix is lost.

---

## 7. Never

- Overwrite or delete `/srv/wiseteck/.env`, `/srv/wiseteck/app/media/` or the database.
- Run `manage.py seed_content --reset` on the server (it wipes everything edited in the admin).
- Edit the dehleze files, or reload Nginx without `nginx -t` passing first.
- Commit passwords, `.env` or `db.sqlite3` (the repository is public).
- Press *Reinstall OS* in the Namecheap dashboard.

---

## 8. Log: what has been run on the server

Newest first. Add an entry each time someone changes the server.

### 23 November 2026, 09:07 UTC: website update from `7b9f1ca` to `af57acb` (`main`)

Backup first (taken 08:10 UTC, in `/root/deploy-backup-2026-11-23-0810/`):

```bash
B=/root/deploy-backup-2026-11-23-0810; mkdir -p $B
cd /srv/wiseteck/app && git rev-parse HEAD > $B/previous-commit.txt
cd /tmp && sudo -u postgres pg_dump wiseteck > $B/wiseteck.sql
tar czf $B/media.tgz -C /srv/wiseteck/app media
cp /srv/wiseteck/.env $B/env.backup && chmod 600 $B/env.backup
```

Then the update, saved as `/root/deploy-2026-11-23.sh` and run in the background so a dropped connection could not
stop it halfway (`nohup /root/deploy-2026-11-23.sh > /root/deploy-2026-11-23.log 2>&1 &`):

```bash
set -e
cd /srv/wiseteck/app
[ -z "$(git status --porcelain)" ] || { echo "STOP: files changed on the server"; exit 1; }
git pull --ff-only origin main
set -a; . /srv/wiseteck/.env; set +a
../venv/bin/pip install -q -r requirements.txt
../venv/bin/python manage.py check --deploy          # "no issues (1 silenced)"
../venv/bin/python manage.py migrate --noinput       # applied core.0019_lighthouse_run
../venv/bin/python manage.py collectstatic --noinput # 3 files updated
chown -R www-data:www-data /srv/wiseteck/app/media
systemctl restart wiseteck                           # "active"
```

To undo: `git checkout 7b9f1ca && systemctl restart wiseteck` (the new table from 0019 is harmless to the old code).

### 23 November 2026: security (no website code changed)

The live code stayed at `7b9f1ca` (the 22 November version). Run as root over SSH:

```bash
# evidence of the attacks (read-only): every failed SSH login still in the logs, 25 Oct - 23 Nov
mkdir -p /root/security-evidence-2026-11-23 && cd /root/security-evidence-2026-11-23
( for f in $(ls -1tr /var/log/auth.log*); do case $f in *.gz) zcat $f;; *) cat $f;; esac; done ) \
  | grep -E "sshd.*(Failed password|Invalid user)" > failed-ssh-logins.log
gzip -kf failed-ssh-logins.log            # + per-day.txt, top-addresses.txt, top-usernames.txt

# daily backups (database + uploaded photos, 02:30 UTC, kept 14 days)
#   script /root/backup-wiseteck.sh as in DEPLOY.md -> Server security -> 5, then:
/root/backup-wiseteck.sh
echo '30 2 * * * root /root/backup-wiseteck.sh' > /etc/cron.d/wiseteck-backup

# fail2ban (Ubuntu 24.04: the SSH service is ssh.service)
apt-get update -qq && apt-get install -y fail2ban
printf '[sshd]\nenabled = true\nmaxretry = 5\nfindtime = 10m\nbantime = 1h\nbantime.increment = true\nbantime.maxtime = 1w\nbackend = systemd\njournalmatch = _SYSTEMD_UNIT=ssh.service + _COMM=sshd\n' > /etc/fail2ban/jail.d/sshd.local
systemctl enable --now fail2ban && systemctl restart fail2ban
fail2ban-client status sshd

# firewall: SSH and the websites only
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp
ufw --force enable && ufw status verbose
```

Checked after each step: a new SSH login works; https://wiseteck.dev, https://www.wiseteck.dev, the admin and
https://dehleze.store answer.

### 22 November 2026: website update from `c119ede` to `7b9f1ca`

Run as root over SSH (exact command lines were not kept; these are the steps, in order):

```bash
# 1. backup into /root/deploy-backup-2026-11-22-0633/
sudo -u postgres pg_dump wiseteck > /root/deploy-backup-2026-11-22-0633/wiseteck.sql
tar czf /root/deploy-backup-2026-11-22-0633/media.tgz -C /srv/wiseteck/app media
cd /srv/wiseteck/app && git rev-parse HEAD > /root/deploy-backup-2026-11-22-0633/previous-commit.txt
# 2. three files edited directly on the server on 20 Nov (and an extra migration made there) were copied into
#    that backup folder, then put back to GitHub's version; GitHub already had the same edits
# 3. update the code and restart
git pull --ff-only origin main
set -a; . /srv/wiseteck/.env; set +a
../venv/bin/pip install -r requirements.txt
../venv/bin/python manage.py check --deploy
../venv/bin/python manage.py migrate
../venv/bin/python manage.py collectstatic --noinput
systemctl restart wiseteck
../venv/bin/python manage.py make_image_variants
chown -R www-data:www-data /srv/wiseteck/app/media
```

### Still to do

- Reboot for pending updates (`reboot`, at a quiet hour; both sites are down about a minute and come back by
  themselves).
- Switch on the Lighthouse panel: `LIGHTHOUSE_TOKEN` in `/srv/wiseteck/.env` and the same value as a GitHub secret
  (DEPLOY.md → *Daily Lighthouse check*).
