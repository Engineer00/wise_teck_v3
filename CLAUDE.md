# Wise-Teck v3 (Django)

Dynamic Django site: every page is `Page` → `Section` (layout = `templates/sections/<layout>.html`) → `Item`, all edited in `/admin/`.

# Commands (Windows)
- Python: use `py -3.13` — a stray `.venv` from ../wise-teck-v3 can make plain `py` pick a Python without Django
- Run: `py -3.13 manage.py runserver 127.0.0.1:8010`
- Tests (the check for any change): `py -3.13 manage.py test core` — one file: `py -3.13 manage.py test core.tests.test_css`
- This Django site is the design source. Optional: `py -3.13 tools/compare_with_v3.py` compares markup with the v3 design files in ../wise-teck-v3
- Fresh content: `py -3.13 manage.py seed_content --reset` (wipes admin edits — never on the live server)
- After model changes: `py -3.13 manage.py makemigrations core` then `migrate`

# Conventions
- Universal CSS: all styles in `static/css/wise-teck.css`; every colour, radius, font size, spacing and z-index comes from a token in the top `:root` blocks (transparent colours: `rgb(var(--p-x-rgb) / .5)`); breakpoints only 1024px / 640px. Spacing comes from the global system (`@layer system`): put `rhythm` on text blocks instead of adding margins; every section uses `--sec-pad`; inner heroes `--page-hero-min`. No inline `style=` except passing a `--custom-property`. `core/tests/test_css.py` enforces this.
- No site text in templates: wording lives in the database (seed: `core/management/commands/seed_content.py`), editable in the admin.
- A new section type = model choice in `Section.LAYOUTS` + `templates/sections/<layout>.html` + entry in `core/layouts.py` (admin field guide) — see the `new-section-layout` skill.
- Admin panel = the original site's panel (`core/adminpanel/`, `templates/adminpanel/`), styled only through its `--ap-*` tokens.
- Commits: author `Engineer00 <salman.k.786000@gmail.com>`, never any Claude/AI attribution (a hook blocks it). Feature branch → push → fast-forward `main`.

# Gotchas
- Screenshots for visual checks: add `?static` to the URL (freezes reveal/wave/spin animations); the 3D coin and the story slider still vary between runs.
- The sitemap is cached 15 min (`cache_page`); clear the cache in tests.
- Don't run `runserver --noreload`: templates stay cached and you test stale markup.
- Production server also hosts `dehleze.store` — never touch its Nginx config; see DEPLOY.md.
