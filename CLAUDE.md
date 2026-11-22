# Wise-Teck (Django)

Dynamic Django site: every page is `Page` → `Section` (layout = `templates/sections/<layout>.html`) → `Item`, all edited in `/admin/`.

## Commands (Windows)

- Python: use `py -3.13` — a stray `.venv` from ../wise-teck-v3 can make plain `py` pick a Python without Django
- Run: `py -3.13 manage.py runserver 127.0.0.1:8010`
- Tests (the check for any change): `py -3.13 manage.py test core` — one file: `py -3.13 manage.py test core.tests.test_css`
- Lint and format (CI fails otherwise): `py -3.13 -m ruff check .` and `py -3.13 -m ruff format .` (rules: `pyproject.toml`)
- CI: `.github/workflows/ci.yml` runs lint, format, `makemigrations --check`, `check --deploy` and the tests on Python 3.12 + PostgreSQL for every push
- Production checklist: `DJANGO_DEBUG=0 DJANGO_SECRET_KEY=<long> DJANGO_ALLOWED_HOSTS=wiseteck.dev py -3.13 manage.py check --deploy` (must report no issues)
- Fresh content: `py -3.13 manage.py seed_content --reset` (wipes admin edits — never on the live server)
- After model changes: `py -3.13 manage.py makemigrations core` then `migrate`. Content changes for the live site go in a data migration that only updates values still equal to the seed (see 0007)

## Conventions

- Universal CSS: all styles in `static/css/wise-teck.css`; every colour, radius, font size, spacing and z-index comes from a token in the top `:root` blocks (transparent colours: `rgb(var(--p-x-rgb) / .5)`). Breakpoints only 1200px (menu), 1024px (tablet), 640px (phone); everything in between is fluid (`clamp()` tokens that scale linearly from 390px to 1440px). `core/tests/test_css.py` enforces this, including that every margin / padding / gap uses a spacing token (`--sp-*`, `--sec-pad`, `--head-gap`, `--grid-gap`, or a named overlap token such as `--feature-overlap`).
- Spacing comes from the global system (`@layer system`): put `rhythm` on text blocks instead of adding margins; every section uses `--sec-pad`; inner heroes `--page-hero-min` (720 desktop/tablet, at least 700 on phones via `--page-hero-min-sm`). Sections keep their natural height (no min-height): equal padding gives equal gaps. Exception: the call-to-action band (`.band`) has one minimum height per screen size (`--band-min*`, set just above the tallest band), so every inner page ends the same way. Buttons on phones/tablets: `--btn-h` tall, groups as wide as their widest button (min `--btn-w`). No inline `style=` except passing a `--custom-property`.
- Colours: never hard-code a colour outside `:root`. Colour schemes (Site Settings) recolour the `--p-*` palette, the drawing scripts (`T("#hex")` / `T3(0xhex)` in wt-waves.js / hero-three.js) and server-drawn SVG (`|themed:theme`, `recolor_markup`) — see `core/theme.py`. New drawing colours must go through those helpers.
- No site text in templates: wording lives in the database (seed: `core/management/commands/seed_content.py`), editable in the admin.
- A new section type = model choice in `Section.LAYOUTS` + `templates/sections/<layout>.html` + entry in `core/layouts.py` (admin field guide) — see the `new-section-layout` skill.
- Custom fields (the site's answer to WordPress ACF): content with known fields gets its own model and admin screen (e.g. `Course`, shown by the `courses` layout); one-off facts are a section's **extra details** (`Detail`: label + value rows, drawn by `sections/_details.html` where the layout's GUIDE entry has `details=`). Section children (items, details) are saved in page versions and drafts (`core/versioning.py`).
- Admin panel = the original site's panel (`core/adminpanel/`, `templates/adminpanel/`), styled only through its `--ap-*` tokens. No inline JS handlers (CSP): behaviour goes in `static/js/adminpanel.js`.
- Security: the CSP allows scripts, styles and fonts from the site only (Inter and Font Awesome are self-hosted in `static/vendor/`); a new third-party source must be added to `SECURE_CSP` in `config/settings.py`. Google Analytics widens it per response (`AnalyticsCSPMiddleware`) only when Site Settings has an ID.
- Photos: every `<img>` of an uploaded photo uses `{% srcset url "slot" %}` (WebP copies, `core/images.py`). A new photo slot = an entry in `images.SLOTS` (best upload size, shown in the admin) and `images.DRAWN` (srcset `sizes`), plus `photos=` / `item_photo=` in `core/layouts.py`.
- Owner features: `core/stats.py` (cookie-free visitor statistics, middleware), `core/seo_audit.py` (dashboard SEO health; titles checked exactly as `core/seo.py` prints them), `core/throttle.py` (sign-in and contact-form rate limits; trusts only the last X-Forwarded-For entry).
- Dependencies: exact pins in `requirements.txt` (what CI tests); dev tools in `requirements-dev.txt`.
- Commits: author `Engineer00 <salman.k.786000@gmail.com>`, never any Claude/AI attribution (a hook blocks it). Feature branch → push → fast-forward `main`.

## Gotchas

- Screenshots for visual checks: add `?static` to the URL (freezes reveal/wave/spin animations); the 3D coin and the story slider still vary between runs. Staff can preview a colour scheme with `?scheme=<key>`.
- The sitemap is cached 15 min (`cache_page`); clear the cache in tests.
- Don't run `runserver --noreload`: templates stay cached and you test stale markup. Editing `config/settings.py` or several files at once can stop the dev server's auto-reloader: restart it.
- Visitor statistics skip `?static`, bots and signed-in staff, so screenshots and admin browsing do not count.
- Git Bash rewrites arguments that start with `/` into Windows paths: prefix with `MSYS_NO_PATHCONV=1`.
- Production server also hosts `dehleze.store` — never touch its Nginx config; see DEPLOY.md. Deploying is the user's call: don't deploy unless asked.
