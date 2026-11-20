# Wise-Teck (Django)

The Wise-Teck website: a dynamic Django site where every page, section, word, link, photo, menu item and
setting lives in the database and is edited in the admin panel. The design is the approved Wise-Teck v3
design, now driven by one universal, token-based stylesheet with a global spacing system.

- **Live:** <https://wiseteck.dev> — admin at <https://wiseteck.dev/admin/>
- **Repository:** <https://github.com/Engineer00/wise_teck_v3> (`main` is what the server runs)
- **Server:** Namecheap VPS (Ubuntu 24.04), next to `dehleze.store` — see [DEPLOY.md](DEPLOY.md)

## Run it locally (Windows)

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 manage.py migrate
py -3.13 manage.py seed_content           # loads all the content and downloads its photos
py -3.13 manage.py createsuperuser        # or: copy_original_admins --db "<original site db.sqlite3>"
py -3.13 manage.py runserver 127.0.0.1:8010
```

Open <http://127.0.0.1:8010/> (site) and <http://127.0.0.1:8010/admin/> (admin panel).
Use `py -3.13` explicitly: a `.venv` left active from another folder can make plain `py` pick a Python without Django.
Locally the database is SQLite; on the server it is PostgreSQL (set by environment variables).

## Check your work

```powershell
py -3.13 manage.py test core                      # 42 tests: pages, editing, contact form, admin, drafts,
                                                  # history, scheduling, SEO, redirects, images, universal CSS
py -3.13 manage.py test core.tests.test_css       # one file
```

Optional: `py -3.13 tools/compare_with_v3.py` compares the markup with the v3 design files in `../wise-teck-v3`.

## Project structure

```text
config/                  settings (SQLite locally, PostgreSQL + production security via env vars), URLs, WSGI
core/
  models.py              all content tables: Page → Section → Item, SiteSettings, NavItem, Footer*, Program,
                         SuccessStory, BlogPost, TeamMember, Service, ContactMessage, Redirect, Revision
  views.py               pages, blog / story detail pages, contact form, previews, robots.txt, sitemap.xml, 404
  layouts.py             what each section layout uses (drives the admin form)
  versioning.py          drafts, scheduled publishing, version history
  seo.py                 titles, descriptions, canonical, Open Graph / X cards, JSON-LD structured data
  images.py              shrinks and compresses uploaded photos
  signals.py             automatic 301 redirect when a page / post / story address changes
  middleware.py          serves the redirects from Admin → Redirects
  adminpanel/            the admin panel at /admin/ (the original site's panel, extended): views, forms, urls
  management/commands/   seed_content, copy_original_admins, publish_scheduled
  templatetags/          template helpers (title highlight, line breaks, wave art, background motifs)
  motifs.py              the background drawings
  seed/                  seed data (photo list, original site content)
  tests/                 the test suite
templates/
  base.html, page.html, detail.html, 404.html
  sections/<layout>.html one template per section type (21 layouts)
  partials/              menu, logo, buttons, 3D coin orbit, story card, SEO tags, wave sprite
  adminpanel/            admin panel screens
static/
  css/wise-teck.css      THE site stylesheet (universal, token-based)
  css/adminpanel.css     admin panel stylesheet (its own --ap-* tokens)
  js/                    site behaviour, waves, 3D coin, admin helpers
  img/                   logo (svg + 512px png), favicon, wordmark
media/seed/              photos used by seed_content
tools/compare_with_v3.py optional markup comparison with the v3 design files
CLAUDE.md                commands and conventions for Claude Code sessions
.claude/                 project hook (no AI attribution in commits) and skills (deploy, new-section-layout)
DEPLOY.md                server setup and updates
```

## Editing content (admin panel)

| In the admin panel | What it controls |
|---|---|
| **Website → Pages** | Each page: address, title and SEO description, link-preview fields, published or not. Open a page to see its sections, create a **draft**, and see its **version history**. |
| **Website → Sections** | The blocks of a page in order: layout (21 types), text, buttons, photos and cards. The form shows only the fields the chosen layout uses. |
| **Website → Menu / Footer / Programs** | Top menu and drop-downs, footer link columns, the three-program strip shown on many pages. |
| **Website → Redirects** | Old addresses → new ones (301). Added automatically when an address changes. |
| **Website → Site Settings** | Logo, contact details, social links, footer text, contact-form alert email, SEO defaults, main web address. |
| **Content → Success Stories / Blogs / Team / Services** | Lists shown by the matching section layouts; stories and posts have their own pages. |
| **Inbox → Messages** | Contact-form messages. |

**Text conventions:** coloured words in a title → type them in *Words in the title to colour*; a line break in a short
label → `|`; paragraphs → blank line; bold → `**like this**`; icons → Font Awesome names such as `fa-users`.

**Drafts, scheduling, history:** *Create draft* copies a page privately → edit → *Preview draft* → *Publish now*, or set
*Go live at* to publish automatically. Every save keeps the previous version: *Preview*, *Open as draft* or *Restore*.
Blog posts and stories have their own *Go live at*.

## Design system (universal CSS)

All styles are in `static/css/wise-teck.css`. Every colour, radius, font size, spacing value and z-index comes from a
token in the `:root` blocks at the top (transparent colours use channel tokens: `rgb(var(--p-white-rgb) / .5)`).
Cascade layers, later wins: `vendor → site → type → layout → system`.

| Rule | Value |
|---|---|
| Content width / gutters | 1200px, centred; 24px gutters on tablet, 16px on phone — symmetric everywhere |
| Section padding | the same for every section: 80px desktop, scaling to 48px |
| Home hero | fills the first screen on desktop (capped at 860px) |
| Inner heroes | the same height on every inner page: 720px desktop; content height below 1024px |
| Text spacing | `class="rhythm"` on a text block spaces its children: eyebrow → heading 12, h1 → next 20, h2 → next 16, h3 → next 12, text → text 12, text → link 16, text → buttons 24 |
| Cards | one padding scale: 32 / 24 / 40px (phones 24 / 20 / 24), radius 24px |
| Breakpoints | 1024px (tablet) and 640px (phone) only |
| Phones | the top bar is hidden; menu, headline and main button are in the first screen |

Rules enforced by `core/tests/test_css.py`: no hard-coded colours / radii / font sizes / z-index outside the tokens,
tokens only in `:root`, only the standard breakpoints, no inline styles in templates.
A new section type: see the `new-section-layout` skill (`.claude/skills/`).

## SEO

Per page: title and description (best 50–60 / 120–160 characters), canonical link, robots (drafts, previews, 404 and
"hide from search engines" are `noindex`), Open Graph / X cards with a sharing image, JSON-LD (EducationalOrganization +
WebSite on the home page, WebPage + BreadcrumbList on every page, BlogPosting / Article on posts and stories).
`/sitemap.xml` and `/robots.txt` are generated; uploads are resized and compressed; changed addresses redirect (301).
After launch: Site Settings → Main web address = `https://wiseteck.dev`, add the site to Google Search Console and submit
`sitemap.xml`.

## Commands

| Command | Does |
|---|---|
| `manage.py seed_content` | Load the content into an empty database (`--reset` wipes admin edits — never on the live server; `--no-download` keeps photo links). |
| `manage.py copy_original_admins --db <file>` | Copy the original site's admin login(s). |
| `manage.py publish_scheduled` | Publish drafts whose *Go live at* has passed (the server runs it every minute). |
| `manage.py test core` | Run the tests. |

## Commit rules

Author `Engineer00 <salman.k.786000@gmail.com>`, no AI attribution (a project hook blocks it). Work on a feature branch,
push it, then fast-forward `main`.
