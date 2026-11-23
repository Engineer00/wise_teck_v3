# Wise-Teck Website

[![CI](https://github.com/Engineer00/wise_teck_v3/actions/workflows/ci.yml/badge.svg)](https://github.com/Engineer00/wise_teck_v3/actions/workflows/ci.yml)
[![Lighthouse](https://github.com/Engineer00/wise_teck_v3/actions/workflows/lighthouse.yml/badge.svg)](https://github.com/Engineer00/wise_teck_v3/actions/workflows/lighthouse.yml)

The website of Wise-Teck, a project of WISE Education Society. It is a content-managed Django site: every page,
section, word, photo, menu item, colour and setting lives in the database and is edited in the site's own admin
panel, so the site is run day to day without touching code.

| | |
| --- | --- |
| Live site | <https://wiseteck.dev> (admin: <https://wiseteck.dev/admin/>) |
| Repository | <https://github.com/Engineer00/wise_teck_v3> (`main` is the deployable version) |
| Owner's guide | [WEBSITE-GUIDE.md](WEBSITE-GUIDE.md): what can be edited, colours, SEO, Lighthouse, server and security in plain language |
| Server guide | [SERVER-ACCESS.md](SERVER-ACCESS.md): logging in, reading the code, updating the live site, undoing an update |
| Deployment | [DEPLOY.md](DEPLOY.md): server setup, security hardening, backups |
| History | [CHANGELOG.md](CHANGELOG.md): every change and decision; *Current status* says which version is live |

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Folder structure](#folder-structure)
- [Editing content](#editing-content)
- [Testing and code quality](#testing-and-code-quality)
- [Performance and Lighthouse](#performance-and-lighthouse)
- [SEO](#seo)
- [Security](#security)
- [Deployment](#deployment)
- [Design system](#design-system)
- [Management commands](#management-commands)
- [Contributing](#contributing)
- [Licence](#licence)

## Features

- **Pages built from sections.** Each page is an ordered list of sections chosen from 22 designs (hero, cards,
  steps, photo and text, call-to-action band, contact form, blog list and more), all edited in the admin.
- **Safe publishing.** Drafts, a preview identical to the live page, scheduled publishing and a full version history
  with one-click restore.
- **Colour schemes.** Three brand colours (primary, accent, dark) recolour the whole site, including the animated
  waves and the 3D coin, with a readability check before saving.
- **Custom fields without code.** Courses have their own admin screen; any section can carry extra label-and-value
  rows such as *Fee · Rs 15,000*.
- **Search-engine ready.** Titles, descriptions, canonical links, structured data, `sitemap.xml`, `robots.txt`,
  `llms.txt`, sharing previews and automatic redirects, with an SEO health check on the dashboard.
- **Daily Google Lighthouse check** of every page, phone and desktop, shown on the admin dashboard.
- **Privacy-friendly visitor statistics** with no cookies and no stored IP addresses.
- **Fast on phones.** Responsive WebP photos, self-hosted fonts, lazy loading and no render-blocking third parties.

## Tech stack

| Layer | Technology |
| --- | --- |
| Application | Python 3.12 (server and CI; 3.13 works locally), Django 6.1.3 |
| Database | PostgreSQL 16 in production, SQLite for local development |
| Web server | Nginx (HTTPS, static and media files) in front of Gunicorn 27 |
| Front end | Plain modern CSS (cascade layers and design tokens, no framework), vanilla JavaScript, three.js for the 3D coin |
| Assets | Inter and Font Awesome Free, self-hosted |
| Quality | Ruff (lint and format), Django test runner, GitHub Actions CI, Dependabot |
| Monitoring | Google Lighthouse 13 on GitHub Actions, daily |
| Hosting | Namecheap VPS, Ubuntu 24.04 (shared with another site, `dehleze.store`) |

Exact package versions are pinned in `requirements.txt`; CI tests exactly those versions.

## Getting started

### Prerequisites

- [Python 3.12 or 3.13](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### Install and run (Windows, PowerShell)

```powershell
git clone https://github.com/Engineer00/wise_teck_v3.git
cd wise_teck_v3
py -3.13 -m pip install -r requirements-dev.txt
py -3.13 manage.py migrate
py -3.13 manage.py seed_content             # loads the full site content and its photos
py -3.13 manage.py createsuperuser          # your local admin login
py -3.13 manage.py runserver 127.0.0.1:8010
```

Open <http://127.0.0.1:8010/> for the site and <http://127.0.0.1:8010/admin/> for the admin. Call Python as
`py -3.13` explicitly: a virtual environment left active from another folder can make plain `py` pick an interpreter
without Django.

On macOS or Linux, use `python3` in place of `py -3.13`.

## Configuration

Settings are read from environment variables (on the server, from `/srv/wiseteck/.env`). With none set, the site runs
in development mode on SQLite. Never commit real values: this repository is public.

| Variable | Purpose | Default |
| --- | --- | --- |
| `DJANGO_DEBUG` | `1` for development, `0` in production | `1` |
| `DJANGO_SECRET_KEY` | Long random secret; required when `DJANGO_DEBUG=0` | development-only key |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names, e.g. `wiseteck.dev,www.wiseteck.dev` | `127.0.0.1,localhost` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated origins, e.g. `https://wiseteck.dev,https://www.wiseteck.dev` | none |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | PostgreSQL connection; when `POSTGRES_DB` is unset, SQLite is used | `localhost`, `5432` |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` | SMTP for contact-form alerts; when `EMAIL_HOST` is unset, mail is printed to the console | port `587`, TLS on |
| `DEFAULT_FROM_EMAIL` | Sender of outgoing mail | `Wise-Teck Website <no-reply@wise-teck.org>` |
| `LIGHTHOUSE_TOKEN` | Shared secret that lets the daily Lighthouse workflow post results; unset disables the endpoint | none |
| `LIGHTHOUSE_WORKFLOW_URL` | Where the dashboard's "Run a check now" link points | this repository's Lighthouse workflow |

Production readiness check (must report no issues):

```powershell
$env:DJANGO_DEBUG="0"; $env:DJANGO_SECRET_KEY="<long random value>"; $env:DJANGO_ALLOWED_HOSTS="wiseteck.dev"
py -3.13 manage.py check --deploy
```

## Folder structure

```text
wise_teck_v3/
├── config/                         Project configuration
│   ├── settings.py                 Settings from environment variables, production security
│   ├── urls.py                     URL routes (pages, sitemap, robots, llms.txt, previews, Lighthouse endpoint)
│   └── wsgi.py                     Entry point for Gunicorn
├── core/                           The website application
│   ├── models.py                   Data model: Page → Section → Item / Detail, site settings, menu, footer,
│   │                               programs, stories, blog, team, services, courses, messages, redirects,
│   │                               versions, visitor statistics, Lighthouse runs
│   ├── views.py                    Public pages, blog and story pages, contact form, previews, sitemap.xml,
│   │                               robots.txt, llms.txt, the Lighthouse results endpoint
│   ├── adminpanel/                 The admin panel at /admin/ (views, forms, URLs)
│   ├── layouts.py                  Fields, photo sizes and help text for each of the 22 section types
│   ├── versioning.py               Drafts, scheduled publishing, version history
│   ├── theme.py                    Colour schemes: three brand colours → the full palette
│   ├── seo.py                      Meta tags, canonical links, Open Graph, structured data
│   ├── seo_audit.py                The dashboard's SEO health check
│   ├── lighthouse.py               Validates Lighthouse results and builds the dashboard panel
│   ├── images.py                   Upload processing, responsive WebP copies, recommended photo sizes
│   ├── stats.py                    Cookie-free visitor statistics
│   ├── throttle.py                 Rate limits for sign-in and the contact form
│   ├── middleware.py               Redirects, Permissions-Policy, Analytics CSP
│   ├── signals.py                  Automatic redirect when an address changes
│   ├── context_processors.py       Site settings, menu, footer and colour scheme for every template
│   ├── permissions.py              Staff-only access
│   ├── motifs.py                   Server-drawn background artwork
│   ├── templatetags/               Template filters and tags (highlights, srcset, colours, link context)
│   ├── management/commands/        seed_content, copy_original_admins, publish_scheduled, make_image_variants
│   ├── migrations/                 Database schema and data migrations
│   ├── seed/                       Seed data for seed_content
│   └── tests/                      Test suite (108 tests)
├── templates/                      HTML templates
│   ├── base.html                   Page shell: head, header, footer
│   ├── page.html, detail.html      A page made of sections; a blog post or success story
│   ├── 404.html, 500.html          Error pages (500 works without the database)
│   ├── sections/                   One template per section type (22) and shared section parts
│   ├── partials/                   Header, logo, buttons, 3D coin, story card, pagination, SEO tags
│   └── adminpanel/                 Admin screens: dashboard, lists, forms, colour-scheme picker
├── static/                         Front-end assets
│   ├── css/wise-teck.css           The site stylesheet (design tokens and cascade layers)
│   ├── css/adminpanel.css          The admin stylesheet (its own --ap-* tokens)
│   ├── js/                         Site behaviour, waves, 3D coin, analytics loader, admin helpers
│   ├── img/                        Logo, wordmark, favicon, default sharing image
│   └── vendor/                     Self-hosted Inter font and Font Awesome
├── media/seed/                     Photos loaded by seed_content (uploads live only on the server)
├── tools/lighthouse/run.mjs        Lighthouse runner used by the daily workflow
├── .github/
│   ├── workflows/ci.yml            Lint, format, migrations check, production check and tests on every push
│   ├── workflows/lighthouse.yml    Daily Lighthouse check of the live site
│   └── dependabot.yml              Weekly dependency and security updates
├── .claude/                        AI-assistant project settings: commit hook and skills
├── manage.py                       Django command-line entry point
├── requirements.txt                Pinned production dependencies
├── requirements-dev.txt            Development tools (Ruff) on top of requirements.txt
├── pyproject.toml                  Ruff configuration
├── README.md                       This file
├── WEBSITE-GUIDE.md                Owner's guide (plain language)
├── SERVER-ACCESS.md                Server access, code changes, going live, server log
├── DEPLOY.md                       Server setup, security, backups
├── CHANGELOG.md                    Change history and current status
└── CLAUDE.md                       Conventions and commands for AI-assisted development
```

## Editing content

All content is edited at `/admin/`.

| Admin section | What it controls |
| --- | --- |
| Dashboard | Visitors (30 days, top pages, sources, devices), SEO health with fix-it links, daily Lighthouse scores, Google tools, messages, drafts, recent changes |
| Website → Pages | Address, title, search description, sharing preview, visibility; drafts, scheduled publishing, version history |
| Website → Sections | The ordered blocks of a page; the form shows only the fields its type uses, with the recommended photo size beside every photo field; extra details (label + value rows) |
| Website → Menu, Footer, Programs | Header menu and drop-downs, footer link columns, the three-program strip |
| Website → Site Settings | Logo, colour scheme, announcement bar, contact details, header button, footer, social links, contact-form texts and alerts, 404 page, search-engine settings, Google Analytics ID, keywords |
| Website → Redirects | Old addresses to new ones; added automatically when an address changes |
| Content → Success Stories, Blogs, Team, Services, Courses | Lists shown by the matching sections; posts and stories get their own pages |
| Inbox → Messages | Contact-form messages |

**Text conventions.** Coloured words in a title: *Words in the title to colour*. Line break in a short label: `|`.
New paragraph: a blank line. Bold: `**like this**`. Icons: Font Awesome names such as `fa-users`.

**Deliberately fixed.** The logo keeps its colours in every scheme; one typeface (Inter) and one type scale; the
layout breakpoints; the shapes of the wave and background drawings (their colours follow the scheme); red and green
status colours.

### Photo sizes

The admin shows the recommended size beside every photo field. Uploads (JPG for photos, PNG for logos, up to 20 MB)
are rotated upright, stripped of camera data, resized to at most 2000px and compressed; the site serves WebP copies
at 480, 800, 1200 and 1600px. Sizes are defined once in `core/images.py` (`SLOTS`).

| Where it appears | Recommended size (px) | Shape |
| --- | --- | --- |
| Inner-page hero; top of a blog post or story | 1920 × 800 | 2.4 : 1 |
| Second hero photo | 1200 × 500 | wide |
| Home · About photo | 1200 × 800 | 3 : 2 |
| Photo beside text (split section) | 1400 × 1050 | 4 : 3 |
| Home · Weekend courses | 1400 × 960 | landscape |
| Home · Corporate collaborations | 1440 × 600 | wide |
| Card photos: programs, earning blocks, team | 800 × 500 | 16 : 10 |
| Home · photo tiles | 800 × 450 | 16 : 9 |
| Blog post photo | 1920 × 1080 | 16 : 9, subject centred |
| Success-story photo | 1000 × 1000 | square, face centred |
| Collaborator logo | 400 × 200 | transparent PNG |
| Service icon | SVG, or 112 × 112 PNG | square |
| Round logo | 512 × 512 | square transparent PNG |
| Browser tab icon | 512 × 512 | square PNG |
| Sharing preview (built-in card when empty) | 1200 × 630 | 1.9 : 1 |

Videos are not uploaded to the site; host them on YouTube and link them from a button.

## Testing and code quality

```powershell
py -3.13 manage.py test core        # 108 tests
py -3.13 -m ruff check .            # lint (rules in pyproject.toml)
py -3.13 -m ruff format .           # format
```

`.github/workflows/ci.yml` runs lint, format check, `makemigrations --check`, `check --deploy` and the full test
suite on Python 3.12 with PostgreSQL 16, matching production, on every push.

| Test file | Covers |
| --- | --- |
| `test_site.py` | Every page and section type renders; admin edits appear on the site; contact form |
| `test_admin.py` | Admin login, editing, drafts, scheduling, version history |
| `test_seo.py` | Titles, descriptions, canonical links, structured data, sitemap, robots, redirects, image resizing |
| `test_css.py` | Design-system rules: tokens only, standard breakpoints, no inline styles |
| `test_audit.py` | Security headers, pagination, page weight, accessibility |
| `test_theme.py` | Colour schemes: recolouring, readability checks, admin picker, preview |
| `test_features.py` | Visitor statistics, SEO health, rate limits, announcement bar, 404 texts, Analytics, WebP photos |
| `test_lighthouse.py` | Lighthouse endpoint (token, validation, retention), dashboard panel, link names, heading order, `llms.txt` |
| `test_custom_fields.py` | Courses and section extra details, including drafts and version history |

## Performance and Lighthouse

Largest Contentful Paint measured with Lighthouse's mobile settings (mid-range phone, slow 4G), median of three loads,
21 November 2026:

| Page | Previous live site | This version |
| --- | --- | --- |
| Home | 12.2 s | 1.8 s |
| About | 8.1 s | 1.7 s |
| Blog | 11.1 s | 1.4 s |
| Blog post | 7.4 s | 1.7 s |

Lighthouse on the live site, 23 November 2026: accessibility, best practices and SEO 100 on the pages checked.

**Daily Lighthouse check.** `.github/workflows/lighthouse.yml` runs Lighthouse 13 on GitHub's runners every day at
00:30 UTC against every page in the live sitemap, on a phone and a desktop. Each run publishes a score table and the
full HTML reports (kept 30 days). When the repository secret `LIGHTHOUSE_TOKEN` matches the server's, the workflow
posts a summary to `/api/lighthouse/`, which `core/lighthouse.py` validates; the dashboard then shows average scores
with day-on-day change, Core Web Vitals for the home page, the most common suggestions and every page's scores.
Start a run by hand from **Actions → Lighthouse → Run workflow**. Setup: [DEPLOY.md](DEPLOY.md#daily-lighthouse-check-once).

## SEO

**Built in:** titles up to 60 characters, descriptions up to 160, canonical links (including paginated lists),
`/sitemap.xml`, `/robots.txt`, `/llms.txt` for AI search, structured data (educational organisation, website,
breadcrumbs, articles, courses), sharing previews, 301 redirects on address changes, `noindex` on drafts, previews
and the 404 page, responsive images and lazy loading. The dashboard's SEO health check runs on every live page, post
and story each time it opens.

**One-time setup (owner):** set *Main web address* in Site Settings; verify Google Search Console and submit the
sitemap; import the site into Bing Webmaster Tools; create the Google Business Profile; optionally add a Google
Analytics ID; switch on the Lighthouse panel.

**Ongoing (people, not software):** useful content around the keywords in Site Settings, alt text on every photo,
Google reviews, and links from partners, universities, employers and directories. Backlinks can be monitored
(Search Console, Ahrefs Webmaster Tools) but should never be bought or automated: that breaks Google's spam policies.

| Area | KPI | Target | Where |
| --- | --- | --- | --- |
| Technical | SEO health score | 95+ | Admin dashboard |
| Speed | Core Web Vitals on phones | LCP < 2.5 s, INP < 200 ms, CLS < 0.1 | Lighthouse panel, Search Console |
| Indexing | Indexed pages vs sitemap | all, no errors | Search Console → Pages |
| Visibility | Impressions, clicks, CTR | growing monthly; CTR 3%+ | Search Console → Performance |
| Rankings | Average position for target keywords | top 10 | Search Console → Queries |
| Leads | Contact messages per month | growing monthly | Dashboard → Messages |
| Local | Business Profile views, calls, reviews | 4.5★+ | Google Business Profile |

Rankings also depend on content and on other sites linking here, so positions cannot be guaranteed.

## Security

- **HTTP headers** on every response: Content-Security-Policy (scripts, styles and fonts from the site only), HSTS,
  X-Frame-Options, Referrer-Policy, Permissions-Policy. `manage.py check --deploy` passes.
- **Admin:** sign-in blocked for 15 minutes after 5 wrong passwords per address; sessions expire after 8 hours;
  previews are staff-only.
- **Contact form:** spam trap and a limit of 5 messages per 10 minutes per address.
- **Uploads:** images validated by Pillow; SVG files containing scripts are rejected; camera metadata removed.
- **Privacy:** visitor statistics use a daily-rotating one-way hash; no cookies, no stored IP addresses.
- **Dependencies:** exact pins, weekly Dependabot updates, every change tested in CI.
- **Server:** fail2ban, firewall (SSH, HTTP, HTTPS only) and daily backups; see
  [DEPLOY.md → Server security](DEPLOY.md#server-security).

**Reporting a vulnerability.** Please report security problems privately to the maintainers rather than in a public
issue, so they can be fixed before they are disclosed.

## Deployment

The site runs on a Namecheap VPS (Ubuntu 24.04) behind Nginx, with Gunicorn as a systemd service (`wiseteck`) and
PostgreSQL. Updates are deployed from `main`, either with `git pull` on the server or with a zip made by
`git archive`; both keep the server's settings, uploads and database.

- First-time setup, security hardening, backups: [DEPLOY.md](DEPLOY.md)
- Step-by-step updates, rollback and a log of server changes: [SERVER-ACCESS.md](SERVER-ACCESS.md)
- Which version is live: [CHANGELOG.md](CHANGELOG.md), *Current status*

## Design system

All styling lives in `static/css/wise-teck.css`: plain CSS, no framework. Every colour, font size, line height,
space, radius and z-index is a token in the `:root` blocks at the top. Cascade layers, later wins:
`vendor → site → type → layout → system`.

| Rule | Value |
| --- | --- |
| Content width | 1200px, centred; side gaps 16px (phone) to 24px; the header and top bar share one width |
| Fluid sizing | Font sizes and spacing scale linearly from 390px to 1440px |
| Section spacing | Equal padding on every section (48px phone → 80px desktop); sections take their natural height, so every gap is equal |
| Heroes | Home fills the first screen; inner heroes 720px (desktop, tablet), at least 700px on phones |
| Call-to-action band | One minimum height per screen size: 360 / 408 / 448 / 560px; grows with longer text |
| Typography | Inter only; one style per role (h1 30–48px, h2 26–36px, body 16px / 1.7); form fields 16px so phones do not zoom |
| Phones | One card per row; photo above text in split sections |
| Buttons (phone, tablet) | 52px tall; buttons in a group share the widest width, minimum 244px |
| Breakpoints | 1200px (menu button), 1024px (tablet), 640px (phone) |
| Touch targets | At least 44px |
| Motion | Hover and fade transitions on every interactive element; reduced-motion settings respected |

`core/tests/test_css.py` enforces the rules: no hard-coded colours, radii, font sizes or z-index outside the tokens,
every margin, padding and gap from a spacing token, only the breakpoints above, and no inline styles in templates.
To add a section type, follow the `new-section-layout` skill in `.claude/skills/`.

## Management commands

| Command | Purpose |
| --- | --- |
| `manage.py seed_content` | Load the content into an empty database (`--reset` wipes admin edits; never run it on the live server) |
| `manage.py copy_original_admins --db <file>` | Copy admin accounts from the original site's database |
| `manage.py publish_scheduled` | Publish drafts whose scheduled time has passed (run every minute on the server) |
| `manage.py make_image_variants` | Generate WebP copies of every photo ahead of time |
| `manage.py check --deploy` | Django's production checklist |

## Contributing

1. Branch from an up-to-date `main`: `git checkout main && git pull && git checkout -b fix/short-description`.
2. Follow the conventions in [CLAUDE.md](CLAUDE.md): styles only in `wise-teck.css` with its tokens, no site text in
   templates, content changes for the live site as data migrations.
3. Before pushing, run the tests, `ruff check .` and `ruff format .`.
4. Commit with a short, descriptive message and the project's Git identity (see CLAUDE.md); no AI attribution (a
   project hook enforces this).
5. Push the branch, wait for CI to pass, then merge into `main` with a fast-forward.

## Licence

This repository has no licence file. It is public so the code can be reviewed and deployed, but it is not open
source: all rights are reserved.
