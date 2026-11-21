# Wise-Teck (Django)

Dynamic Django site: every page is `Page` → `Section` (layout = `templates/sections/<layout>.html`) → `Item`, all edited in `/admin/`.

## Commands (Windows)

- Python: use `py -3.13` — a stray `.venv` from ../wise-teck-v3 can make plain `py` pick a Python without Django
- Run: `py -3.13 manage.py runserver 127.0.0.1:8010`
- Tests (the check for any change): `py -3.13 manage.py test core` — one file: `py -3.13 manage.py test core.tests.test_css`
- Production checklist: `DJANGO_DEBUG=0 DJANGO_SECRET_KEY=<long> DJANGO_ALLOWED_HOSTS=wiseteck.dev py -3.13 manage.py check --deploy` (must report no issues)
- Fresh content: `py -3.13 manage.py seed_content --reset` (wipes admin edits — never on the live server)
- After model changes: `py -3.13 manage.py makemigrations core` then `migrate`. Content changes for the live site go in a data migration that only updates values still equal to the seed (see 0007)

## Conventions

- Universal CSS: all styles in `static/css/wise-teck.css`; every colour, radius, font size, spacing and z-index comes from a token in the top `:root` blocks (transparent colours: `rgb(var(--p-x-rgb) / .5)`). Breakpoints only 1200px (menu), 1024px (tablet), 640px (phone); everything in between is fluid (`clamp()` tokens that scale linearly from 390px to 1440px). `core/tests/test_css.py` enforces this.
- Spacing comes from the global system (`@layer system`): put `rhythm` on text blocks instead of adding margins; every section uses `--sec-pad`; inner heroes `--page-hero-min` (720 desktop/tablet, 830 phone). No inline `style=` except passing a `--custom-property`.
- Colours: never hard-code a colour outside `:root`. Colour schemes (Site Settings) recolour the `--p-*` palette, the drawing scripts (`T("#hex")` / `T3(0xhex)` in wt-waves.js / hero-three.js) and server-drawn SVG (`|themed:theme`, `recolor_markup`) — see `core/theme.py`. New drawing colours must go through those helpers.
- No site text in templates: wording lives in the database (seed: `core/management/commands/seed_content.py`), editable in the admin.
- A new section type = model choice in `Section.LAYOUTS` + `templates/sections/<layout>.html` + entry in `core/layouts.py` (admin field guide) — see the `new-section-layout` skill.
- Admin panel = the original site's panel (`core/adminpanel/`, `templates/adminpanel/`), styled only through its `--ap-*` tokens. No inline JS handlers (CSP): behaviour goes in `static/js/adminpanel.js`.
- Security: the CSP allows scripts from the site only; new third-party scripts, fonts or frames must be added to `SECURE_CSP` in `config/settings.py`.
- Commits: author `Engineer00 <salman.k.786000@gmail.com>`, never any Claude/AI attribution (a hook blocks it). Feature branch → push → fast-forward `main`.

## Gotchas

- Screenshots for visual checks: add `?static` to the URL (freezes reveal/wave/spin animations); the 3D coin and the story slider still vary between runs. Staff can preview a colour scheme with `?scheme=<key>`.
- The sitemap is cached 15 min (`cache_page`); clear the cache in tests.
- Don't run `runserver --noreload`: templates stay cached and you test stale markup.
- Git Bash rewrites arguments that start with `/` into Windows paths: prefix with `MSYS_NO_PATHCONV=1`.
- Production server also hosts `dehleze.store` — never touch its Nginx config; see DEPLOY.md. Deploying is the user's call: don't deploy unless asked.
