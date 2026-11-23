# Wise-Teck Website: How It Works

23 November 2026. The same guide as a shared document: <https://claude.ai/artifact/Mz1PL27sdtbBFTf2UWuAAu>.
Step-by-step server commands: [SERVER-ACCESS.md](SERVER-ACCESS.md).

## How dynamic is the site?

Very dynamic: almost every word, photo, link, menu item, page and colour visitors see comes from the database and is
changed at <https://wiseteck.dev/admin/> with no developer and no code. All 16 public pages are built from sections
stored in the database. A scan of every site template (23 November 2026) found only five fixed words, listed in
[What still needs a developer](#what-still-needs-a-developer).

What stays in code is the *design*: how each type of section looks, spacing, fonts, animations and the server. You
pick from 22 ready-made section designs, fill them in and put them in any order. A brand-new kind of design needs a
developer.

There is no "edit on the page" mode yet, where you click text on the live site and type over it. Instead you edit in
the admin, save as a draft, press **Preview** to see the page exactly as visitors will, then publish. **View on site**
opens the live page from any form. The colour scheme also has a Preview button that shows unsaved colours across the
site.

## What you can change in the admin

Everything below is edited at <https://wiseteck.dev/admin/> and shows on the site as soon as you save (or publish,
for a draft).

| Area | What you can change |
| --- | --- |
| Pages | Add, hide or remove pages; page title and web address; the order of sections; search and sharing text and image. Save as draft, schedule a publish time, or restore an older version |
| Sections | Choose one of 22 designs (hero, cards, steps, photo + text, call-to-action band, contact form and more); headings, text, buttons, photos, icons, cards, extra details (label + value rows), words shown in colour, show or hide |
| Menu | Header menu items and their drop-down links; the header button's text and link |
| Footer | Footer columns, their links and the tagline |
| Lists | Programs, success stories, blog posts, team members, services, courses. Each appears by itself wherever its section is placed |
| Site settings | Top bar text, announcement bar, "page not found" texts, colour scheme, 3D coin colours, default search description, keywords, Google Analytics ID, sharing image |
| Contact messages | Read what visitors send through the contact form |
| Redirects | Send an old web address to a new one. Changing a page's address adds this automatically |
| Dashboard | Visitor numbers (no cookies), a search-engine health check with fixes in plain words, and the daily Lighthouse scores |

## What still needs a developer

These are kept in code on purpose, so the design stays consistent however the content changes.

| Kept in code | Why |
| --- | --- |
| A new kind of section design | Each of the 22 designs is a tested template; a new one needs a template, admin help text and checks on every screen size |
| Spacing, fonts, sizes, corner shapes | One shared design system keeps every page even; changing it in one place changes it everywhere |
| Animations (waves, 3D coin, reveal on scroll) | Code tuned for speed on phones |
| Five fixed words | "Home" in the blog breadcrumb, "No posts yet" on an empty blog, "Loading 3D…" while the coin loads, a hidden spam-trap field, and the server error page (it must work even when the database is down) |
| Server, security, backups | Done on the server over SSH (see the server sections below) |

## Colour scheme: three colours drive every shade

You choose three colours and every other colour on the site is worked out from them, including all the lighter and
darker shades. Where: **Admin → Site Settings → Colour scheme**. Pick one of six ready-made schemes or **Custom
colours**, press **Preview** to see the whole site in the new colours before saving, then **Save**.

| Scheme colour | Default | Where it shows | Shades that follow it |
| --- | --- | --- | --- |
| Primary | Violet #6d28d9 | Buttons, links, highlighted words, icons, light lavender backgrounds | 57 |
| Accent | Gold #d4af37 | Call-to-action buttons, gold rims and details | 26 |
| Dark | Navy #0d2158 | Top bar, footer, headings, dark text | 34 |
| Never changed | | White, greys, red error and green success colours, the logo | 15 |

**How the shades follow.** Each shade keeps its own lightness and takes the new colour's hue and strength. A very
light lavender background becomes a very light version of the new colour; dark text stays dark. The colour you pick
becomes the exact main shade, so contrast stays as readable as in the default scheme.

Example with the Emerald scheme (primary #047857):

| Shade | Default | Becomes |
| --- | --- | --- |
| Button violet | #7c3aed | #1c8765 |
| Soft lavender ring | #b9a3ff | #92c1ad |
| Palest background | #f5f3ff | #f1f6f4 |

The same change reaches the moving waves, the 3D coin and the background patterns (39 drawing colours). If a custom
colour would make text hard to read, for example white text on a too-light primary, Site Settings shows a warning in
plain words before you save.

**The other colours: the 3D coin.** Site Settings has a second, optional group, **3D coin colours**, with three
boxes: base (the coin face, white by default), lower ring (violet) and upper ring (light violet). Left empty, the
coin follows the colour scheme like everything else. Filled in, they change only the coin and override the scheme
there. So the site has 3 scheme colours that drive everything, plus up to 3 coin colours that touch only the coin.

## Section heights: natural, with three exceptions

No section has a maximum height, and ordinary sections have no minimum either: each is as tall as its content. Every
section gets the same space above and below (80px on desktop, shrinking smoothly to 48px on phones), so the gap
between any two sections is always equal. Content added in the admin never gets cut off.

Three kinds of section have a *minimum* height, so pages line up with each other. They grow taller if their content
needs it.

| Section | Minimum height | Why |
| --- | --- | --- |
| Home hero (top of the home page) | Fills the screen: at least 640px, at most 860px; desktop only | The first view is a full-screen welcome |
| Inner page hero (top of every other page) | 720px desktop and tablet, 700px phones | Every page opens with the same height |
| Call-to-action band (end of inner pages) | 360px desktop, 408px small laptops, 448px tablets, 560px phones | Every page ends the same way, whatever the band's wording |

## Animations and transitions

Every hover and fade on the site is now smooth, checked by a script that tests all 42 hover styles on all 16 pages
(23 November 2026). Fixed that day:

- Links in the top bar, menu, drop-downs, footer and breadcrumbs changed colour instantly. They now fade over 0.2
  seconds.
- Program, service and other cards never lifted on hover, and their shadow jumped. The scroll-in animation was holding
  them in place for good. Now, once a card has faded in, its own 0.3-second lift and shadow take over.
- The menu button's three lines stayed equal after closing on phones. It now always returns to its uneven lines.
- Tapping on a phone flashed the browser's sky blue. Taps now show a light brand violet.
- The header coin turned non-stop, so it rarely lined up with the top bar. It now rests facing forward (lined up)
  and makes one smooth turn every 8.5 seconds.

**GSAP is not needed.** GSAP is an animation library for complex timelines (scenes that scrub with the scroll bar,
morphing shapes). This site's motion is fades, lifts, the moving waves and the 3D coin. CSS and the site's own small
scripts already do all of that. GSAP would add about 70 KB of code for phones to download and slow the first view,
with nothing to show for it. Visitors who ask their device for reduced motion get a still site.

## Quality checks and Lighthouse

The site meets professional standards on every check that could be measured on 23 November 2026. Accessibility, best
practices and SEO all score 100 in Google Lighthouse. Phone speed figures will come from the first daily Lighthouse
run (see below).

| Area | How it is checked | Result |
| --- | --- | --- |
| Automated tests | 108 tests run on every change (pages, admin, drafts, SEO, colours, security, design rules) | All pass |
| Code quality | Ruff style and lint checks; GitHub runs everything on Python 3.12 + PostgreSQL for every push | Pass |
| Accessibility | Lighthouse on home, about, blog, contact, Wise College | 100 (contact was 98: fixed a skipped heading level) |
| SEO | Lighthouse, same pages | 100 (home and blog were 92: "Read More" links now say which page they open) |
| Best practices | Lighthouse | 100 |
| Speed | Lighthouse | Home on desktop 89 (main content in 1.1 s, no layout jumping); about on desktop 98; blog on a phone 95 |
| Design consistency | One stylesheet with shared tokens; tests block stray colours, spacing and screen sizes; alignment measured at 8 widths | Pass |
| Security | Content Security Policy, HTTPS, login and contact-form rate limits, Django's production checklist | Pass; server secured on 23 Nov (firewall, fail2ban, daily backups); a reboot at a quiet hour is still due |

Lighthouse's remaining speed suggestions are about 98 KB of unused CSS, CSS and JavaScript that could be minified
(31 KB and 11 KB), and a 0.6 s server response on the home page. These are the next speed improvements.

### Lighthouse on the admin dashboard (automatic)

Yes, it is fully automatic. Every day at 05:30 Pakistan time, GitHub's servers run Google Lighthouse on every page of
the live site, on a phone and on a desktop. The results appear in a new **Speed & quality** panel on the admin
dashboard. Nothing extra runs on your own server, and it costs nothing because the code repository is public.

What the panel shows:

| Part | What to look at |
| --- | --- |
| Four scores, phone and desktop | Performance (speed), Accessibility (usable by everyone), Best practices (security, modern standards), SEO (search basics). Green 90–100, orange 50–89, red under 50; each shows the change since the previous day |
| Core Web Vitals (home page, phone) | Largest Contentful Paint: under 2.5 s is good. Total Blocking Time: under 200 ms. Cumulative Layout Shift: under 0.1. Google uses these in rankings |
| What Lighthouse suggests | The most common fixes in plain words, with how many pages each affects |
| Every page | Each page's four scores, phone / desktop |
| Links | Full reports for every page, and "Run a check now" (GitHub's *Run workflow* button) |

Switching it on is a one-time step, after this update is live:

1. Make a long random value (for example with `openssl rand -hex 32` on the server).
2. Add it to the server's `/srv/wiseteck/.env` as `LIGHTHOUSE_TOKEN=<value>`, then `systemctl restart wiseteck`.
3. Add the same value on GitHub: repository **Settings → Secrets and variables → Actions → New repository secret**,
   named `LIGHTHOUSE_TOKEN`.

Without step 3 the daily check still runs, and its results show on the GitHub run page instead of the dashboard.

## Complete SEO: what is automatic and what needs people

Technical SEO is built into the site and runs by itself. Being found also takes three free Google and Bing accounts
(set up once) and ongoing work no software can do honestly: useful content and links from other websites.

**Already automatic in the site:**

- Search title and description for every page, blog post and story, editable in the admin, with a health check on
  the dashboard (length, missing text, missing photos).
- `sitemap.xml` (every live page, updated by itself), `robots.txt`, and `llms.txt` (the same list, written for AI
  search such as ChatGPT, Gemini and Perplexity).
- Structured data Google reads: organisation, breadcrumbs, articles, courses. Sharing previews for WhatsApp,
  Facebook, LinkedIn and X.
- One official address per page (canonical). Drafts and previews hidden from Google. An automatic redirect when a
  page's address changes.
- Fast, mobile-friendly pages over HTTPS: compressed WebP photos in several sizes, self-hosted fonts. Accessibility
  100.
- A daily Lighthouse check of speed, SEO and accessibility on the dashboard.

**Set up once (free):**

1. **Google Search Console**: proves you own the site, then shows which searches show it, clicks, position, indexing
   problems, real-visitor speed and the websites that link to you. Paste its verification code into Site Settings
   and submit the sitemap (the dashboard's Google tools panel has the link and a Copy button).
2. **Bing Webmaster Tools**: one click to import from Search Console. Bing's index also feeds ChatGPT search and
   Copilot.
3. **Google Business Profile**: the Maps and local listing for 48-Main Gulberg, Lahore, with hours, photos and
   reviews. This drives "near me" searches.

**Ongoing work (people, not software):**

- **Content**: publish a useful blog post or success story regularly, answering what students actually search for.
  Set your target keywords in Site Settings; the dashboard links to Google Trends and live searches for them.
- **Backlinks** (other websites linking to yours): ask partners, the affiliated university, employers, local
  directories, education portals and news sites to link to Wise-Teck. Keep name, address and phone identical
  everywhere. Track new links for free in Search Console or Ahrefs Webmaster Tools.
- **Reviews**: ask students to review Wise-Teck on Google.

**What cannot be automated.** Backlinks can be monitored but not created by software. Bought or automated links break
Google's spam policies and can get a site removed from results. Content can be drafted with AI help, but Google
penalises mass-produced pages, so a person should review and add real facts.

| Tool | What it does | Cost | Runs by itself? |
| --- | --- | --- | --- |
| Admin SEO health | Checks titles, descriptions and photos on every page | Free (built in) | Yes, each time the dashboard opens |
| Lighthouse panel | Speed, technical SEO, accessibility, every page | Free (built in) | Yes, daily |
| Google Search Console | Searches, clicks, indexing, backlinks, real-visitor speed | Free | Yes, after setup; emails alerts |
| Bing Webmaster Tools | Same for Bing and ChatGPT search | Free | Yes, after setup |
| Google Business Profile | Maps, local search, reviews | Free | Updates by hand |
| Google Analytics 4 | Detailed visitor behaviour (optional; the site counts visitors itself) | Free | Yes |
| Ahrefs Webmaster Tools | Backlink list and site audit for your own site | Free | Yes, after setup |
| Semrush / Ahrefs (paid) | Competitors' keywords and links | Paid monthly | Yes; only worth it for an active SEO campaign |

Possible next step: show Search Console's searches, clicks and new backlinks on the admin dashboard as well, daily.
That needs read access to your Search Console, given once to a Google service account.

## Editing directly on the page

Not yet: today every change is made in the admin, and you see it on the page after saving. An on-page edit mode can
be added, because every word and photo already comes from the database.

**Today:**

- Edit a page or section in the admin, press **Save as draft**, then **Preview** to see the page exactly as visitors
  will. Publish when happy, or schedule a time.
- **View on site** on any form opens the live page in a new tab.
- Every save is a version you can restore.

**How an on-page edit mode would work** (two steps, the first one small):

1. **Edit buttons on the live page.** When you are signed in, an "Edit page" switch appears at the top of the site.
   Each section gets an outline and an **Edit this section** button that opens its form in a side panel; after
   saving, that section refreshes in place. Visitors never see any of this.
2. **Typing on the page itself.** Click a heading or paragraph and type over it. Click a photo to upload a
   replacement (resized and compressed automatically), or paste a new video link. Changes save as a draft first,
   with Publish and Undo, and each one is kept as a version.

Recommendation: build step 1 first. It gives "click what you see, change it" right away, and reuses the admin's
existing checks and version history.

## The server: what each part does and why

The domain is registered at Porkbun, the server is rented from Namecheap, and on that server Nginx, Gunicorn with
Django, and PostgreSQL work together. Each does one job.

```text
 Visitor (phone or computer) opens wiseteck.dev
        │
        ▼
 Porkbun (domain) ── finds the server for wiseteck.dev: 159.198.43.141
        │
        ▼
 ┌─ Namecheap VPS · 159.198.43.141 ───────────────────────────────┐
 │  Nginx · the front door                                        │
 │    HTTPS lock, compression, photos and CSS;                    │
 │    also serves dehleze.store, kept separate                    │
 │        │                                                       │
 │        ▼                                                       │
 │  Gunicorn + Django · the website                               │
 │    builds each page, runs the admin panel,                     │
 │    receives the daily Lighthouse scores                        │
 │        │                                                       │
 │        ▼                                                       │
 │  PostgreSQL · the database                                     │
 │    content, messages, versions, statistics                     │
 └────────────────────────────────────────────────────────────────┘
        ▲
        │ new versions (git pull or zip)
 GitHub · the code ── tests every change, daily Lighthouse check
```

| Part | What it is | Why we use it |
| --- | --- | --- |
| Porkbun | The company where the domain wiseteck.dev was bought (a registrar) | Its DNS settings point wiseteck.dev to the server's address, 159.198.43.141. The domain was bought there; moving it to Namecheap is optional (one account), not needed |
| Namecheap VPS | The rented computer (Ubuntu 24.04) that runs the site, next to dehleze.store | Full control and a fixed monthly price |
| Nginx | The web server in front | Handles the HTTPS certificate (the padlock); sends photos, CSS and fonts straight from disk, compressed and cached, without waking the Python program; passes page requests to Gunicorn; lets wiseteck.dev and dehleze.store share one server without touching each other; cuts off slow or oversized requests, so one bad visitor cannot tie up the site |
| Gunicorn + Django | The program that builds the pages and the admin | Django is the website's code; Gunicorn runs several copies of it at once so many visitors are served together |
| PostgreSQL | The database | Keeps all content, messages, versions and statistics safely, even with many people editing |
| GitHub | Where the code lives | Every change is tested automatically; the daily Lighthouse check runs here; the server gets new versions from here |

## Server security: what protects the server, and why

Bots tried **298,509 wrong passwords** on the server's root login in 30 days (25 October to 23 November 2026), from
2,038 different internet addresses, about 10,000 a day. None got in: every successful login in the last 10 days is
accounted for. On 23 November the server was locked down so these attempts are now blocked, not just refused.

| Protection | What it does | Why we use it |
| --- | --- | --- |
| Strong root password (since 21 Nov) | 24 random characters | A guessing bot would need longer than the age of the universe; the old password could fall |
| fail2ban (since 23 Nov) | Blocks an address for 1 hour after 5 wrong passwords in 10 minutes, longer each time it returns (up to a week) | Stops each bot after a handful of tries instead of thousands. It blocked its first attacker within 75 seconds |
| Firewall, `ufw` (since 23 Nov) | Only SSH (22) and the websites (80, 443) can be reached | Anything else started on the server by mistake stays invisible from the internet |
| Daily backups (since 23 Nov) | Database and uploaded photos at 02:30 UTC, kept 14 days, in `/root/backups/` | There were none. A bad update, a mistake in the admin or a broken disk could otherwise lose everything |
| Automatic security updates | Ubuntu installs security fixes by itself | Known holes get closed without anyone remembering |
| Rate limits on the website | The admin login stops after 5 wrong passwords; the contact form after 5 messages in 10 minutes | Protects the website's own login and inbox |

**Have the attacks stopped?** No, and they never will: bots scan every server on the internet. The difference now is
that each one is blocked after 5 tries, and the password cannot be guessed. Two optional extras would cut them
further: key-only login (the server stops accepting passwords at all, but everyone would need a key file instead of
the password), and a reboot at a quiet hour to finish installing pending updates. Every service, including
dehleze.store's, restarts by itself, so the reboot is safe; it takes both sites down for about a minute.

**If you get locked out** after typing the password wrong 5 times, wait an hour, or ask someone who can log in to run
`fail2ban-client set sshd unbanip <your address>`.

**Proof:** the full log of every failed login is kept on the server in `/root/security-evidence-2026-11-23/`, and a
copy with a summary is on the developer's PC in `D:\Inner Pages\security-evidence-2026-11-23\`.

## Tools we use, and why

| Tool | Why we use it |
| --- | --- |
| PowerShell `ssh` / PuTTY | Log in to the server and type commands; everything is encrypted |
| WinSCP | See and copy the server's files like in Windows Explorer |
| `scp` | Send the update zip to the server |
| Git and GitHub | Every code change is recorded and can be undone; GitHub keeps the master copy, tests every change and runs the daily Lighthouse check |
| Zip, `unzip`, `rsync` | The zip update: pack the code, unpack it on the server, copy only the code over, leaving passwords, photos and the database alone |
| `systemctl` | Restart the site or Nginx, and check they are running |
| `journalctl` | Read logs: errors, and who tried to log in |
| `pg_dump` | Save a copy of the database before an update |
| `cron` | Run the daily backup by itself |
| `.env` file | Keeps passwords out of the code, so the code can be public on GitHub |

## How to open the server

Use PowerShell or PuTTY to type commands, and WinSCP to see the server's folders like Windows Explorer. All three use
the server's root password.

**Commands (PowerShell, built into Windows 10):**

```powershell
ssh root@159.198.43.141
```

Type the password when asked (nothing shows while you type), then `exit` to leave. With PuTTY instead: Host
`159.198.43.141`, Port `22`, **Open**, log in as `root`.

Useful once logged in:

| Command | What it does |
| --- | --- |
| `systemctl status wiseteck --no-pager` | Is the site running? |
| `journalctl -u wiseteck -n 50 --no-pager` | The last 50 lines of the site's log (errors show here) |
| `systemctl restart wiseteck` | Restart the site |
| `nginx -t` | Check Nginx's settings before reloading it |
| `df -h` and `free -h` | Free disk space and memory |

**Folders on screen (WinSCP, free):** New Site → File protocol **SFTP**, Host `159.198.43.141`, Port `22`, User
`root`, the password → **Login**. Your PC is on the left, the server on the right.

| Folder | What it holds |
| --- | --- |
| `/root/` | Put the update zip here |
| `/srv/wiseteck/app/` | The site's code |
| `/srv/wiseteck/.env` | Passwords and settings. Never delete or overwrite |
| `/srv/wiseteck/app/media/` | Photos uploaded in the admin. Exists only on the server |
| `/home/dehleze/`, `/etc/nginx/sites-available/dehleze` | The other website. Never touch |

**Control panel.** We have two logins: the server's root password and the website admin. That covers all day-to-day
work. We do not have the Namecheap or Porkbun account logins; those belong to whoever bought the server and the
domain. Namecheap's account dashboard manages the VPS itself: start, stop, reboot from outside, a console when SSH is
unreachable, root password reset and renewal. Porkbun's account is needed to change DNS records or renew the domain.
Before the server security steps that change how root logs in, make sure the account owner can be reached in case of
a lock-out. Never press **Reinstall OS**: it wipes both websites. cPanel is a paid add-on that
[only installs on a fresh AlmaLinux server](https://www.namecheap.com/hosting/vps/), so adding it would mean
rebuilding both sites from scratch; it is not recommended. If a browser panel is wanted, Cockpit (free, from Ubuntu)
shows services, logs, updates and a terminal without changing Nginx. It should be opened through SSH rather than to
the whole internet.

**Security note.** Since 23 November, fail2ban blocks anyone who types the root password wrong 5 times (for an hour,
longer if they return). The firewall, daily backups and the remaining optional steps are described above in "Server
security".

### Getting to the code

The code lives in three places. GitHub holds the master copy; the server and this PC hold copies of it.

| Where | Address | Notes |
| --- | --- | --- |
| GitHub (public) | <https://github.com/Engineer00/wise_teck_v3> | Branch `main` is what goes live. The 23 November changes wait on branch `fix/burger-icon-reset` until merged |
| The server | `/srv/wiseteck/app` | The live copy. Settings and passwords are next to it in `/srv/wiseteck/.env` |
| This PC | `D:\Inner Pages\wise-teck-v3-django` | The working copy where changes are made and tested |

**Look at the code on the server** (after `ssh root@159.198.43.141`):

```bash
cd /srv/wiseteck/app
ls                          # the files and folders
git log --oneline -5        # which version is live (newest first)
git status                  # files changed on the server itself (should be none)
less core/views.py          # read a file (q to quit)
```

Or open `/srv/wiseteck/app` in WinSCP and double-click any file to view it.

**Get a copy on any Windows PC** (needs Git and Python 3.13):

```powershell
git clone https://github.com/Engineer00/wise_teck_v3.git
cd wise_teck_v3
py -3.13 -m pip install -r requirements-dev.txt
py -3.13 manage.py migrate
py -3.13 manage.py seed_content
py -3.13 manage.py createsuperuser
py -3.13 manage.py runserver 127.0.0.1:8010
```

Then open <http://127.0.0.1:8010/> for the site and <http://127.0.0.1:8010/admin/> for the admin. This runs on test
content, not the live content.

**Copy the server's code to this PC** (PowerShell; it includes uploaded photos):

```powershell
scp -r root@159.198.43.141:/srv/wiseteck/app "D:\server-copy"
```

**Rule:** change code on the PC, send it to GitHub, then update the server from there (zip or `git pull`). Never edit
code directly on the server: the next update overwrites it, as happened to edits made there on 20 November.

## How to update the live site

On 23 November the live site still ran the 22 November version, which was put on the server with `git pull` from
GitHub, not with a zip. Either method below works. Both keep everything edited in the admin, the uploaded photos and
the passwords.

### Method A: the zip file

The up-to-date zip is `D:\Inner Pages\wise-teck-site.zip`. Copy it to the server's `/root/` folder with WinSCP, or
from PowerShell on the PC:

```powershell
scp "D:\Inner Pages\wise-teck-site.zip" root@159.198.43.141:/root/
```

Then log in (`ssh root@159.198.43.141`) and run these blocks in order:

```bash
# 1. back up the database and uploaded photos
sudo -u postgres pg_dump wiseteck > /root/wiseteck-$(date +%F).sql
tar czf /root/wiseteck-media-$(date +%F).tgz -C /srv/wiseteck/app media

# 2. unpack the zip and copy the new code over the old (keeps .env, uploads and the database)
apt install -y unzip rsync
cd /root && rm -rf wiseteck-new && unzip -q wise-teck-site.zip -d wiseteck-new
rsync -a --exclude media/ --exclude staticfiles/ --exclude .env --exclude db.sqlite3 wiseteck-new/ /srv/wiseteck/app/
cp -r wiseteck-new/media/seed /srv/wiseteck/app/media/

# 3. install, update the database, restart
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

`check --deploy` must end with "no issues (1 silenced)", and the status must say **active (running)**. The server
folder is also a GitHub copy, so after a zip update `git status` lists changed files; that is expected. To switch back
to Method B later, run `git fetch origin && git reset --hard origin/main` in `/srv/wiseteck/app` (passwords, uploads
and the database are not in GitHub and are kept).

### What is in the zip

| File or folder | What it is |
| --- | --- |
| `WEBSITE-GUIDE.md` | This guide |
| `SERVER-ACCESS.md` | Step-by-step guide: logging in, reading the folders and code, updating with the zip, undoing an update |
| `DEPLOY.md` | Server setup, security, backups, switching on Lighthouse |
| `README.md` | What the site does, the admin, SEO, Lighthouse, tests |
| `CHANGELOG.md` | Every change, the decisions, and which version is live |
| `manage.py` | The command for Django tasks: `migrate`, `collectstatic`, `check --deploy` |
| `requirements.txt` | The exact Python packages the site needs |
| `config/` | Settings and web addresses |
| `core/` | The website's code: database tables (`models.py`), pages (`views.py`), the admin panel, the tests |
| `core/migrations/` | Database updates, applied by `migrate` |
| `templates/` | The HTML of every page and section type |
| `static/` | The stylesheets, scripts, fonts and logo |
| `media/seed/` | The starting photos |
| `.github/workflows/` | GitHub's automatic jobs: tests on every change, the daily Lighthouse check |

Not in the zip, and never overwritten by an update: `/srv/wiseteck/.env` (passwords), uploaded photos and the
database. They exist only on the server.

### Method B: from GitHub (fewer steps)

First merge the changes into `main` on GitHub (branch `fix/burger-icon-reset`, one click). Then on the server, run
block 1 above, then:

```bash
cd /srv/wiseteck/app
git status          # must say "nothing to commit"
git pull --ff-only origin main
```

Then run block 3 above.

### After this update

- Open <https://wiseteck.dev> on a phone: the menu button returns to its uneven lines, and the top bar lines up with
  the logo and the Apply button.
- Open <https://wiseteck.dev/llms.txt>: it lists the pages.
- Switch on the Lighthouse panel (three steps in "Quality checks and Lighthouse" above).
- If anything fails, `journalctl -u wiseteck -n 50 --no-pager` shows why, and the backups from block 1 restore the
  previous state.

## Sources

- Namecheap VPS hosting, cPanel add-on on AlmaLinux: <https://www.namecheap.com/hosting/vps/>
- Namecheap control panels:
  <https://www.namecheap.com/support/knowledgebase/article.aspx/505/48/what-control-panels-do-you-provide/>
