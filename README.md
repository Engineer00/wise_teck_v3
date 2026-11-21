# Wise-Teck

The Wise-Teck website: a dynamic Django site where every page, section, word, link, photo, menu item, colour and
setting lives in the database and is edited in a friendly admin panel. No code is needed to run the site day to day.

- **Live:** <https://wiseteck.dev> (admin: <https://wiseteck.dev/admin/>)
- **Repository:** <https://github.com/Engineer00/wise_teck_v3> (`main` is the version to deploy)
- **Server:** Namecheap VPS (Ubuntu 24.04), next to `dehleze.store`. See [DEPLOY.md](DEPLOY.md).

## What the admin can change

| Admin section | What it controls |
| --- | --- |
| **Website → Pages** | Each page: address, title, search-engine description, sharing preview, published or hidden. Every page has **drafts**, **scheduled publishing** and **version history** with one-click restore. |
| **Website → Sections** | The blocks of a page, in order. 21 section types (hero, cards, steps, split text + photo, blog list, contact form ...); the form only shows the fields that type uses. |
| **Website → Menu / Footer / Programs** | Top menu and drop-downs, footer link columns, the three-program strip. |
| **Website → Site Settings** | Logo, **colour scheme**, contact details, social links, footer text, contact-form alerts, search-engine defaults. |
| **Website → Redirects** | Old addresses → new ones. Added automatically when a page address changes. |
| **Content → Success Stories / Blogs / Team / Services** | Lists shown by the matching sections. Blog posts and stories have their own pages; long lists get page numbers. |
| **Inbox → Messages** | Contact-form messages. |

**Colour schemes.** Site Settings → *Colour scheme*: pick one of six ready-made schemes or *Custom colours* (three colour
pickers: primary, accent, dark). Every colour on the site follows: buttons, backgrounds, waves, footer, the 3D coin.
*Preview on the website* shows the scheme before saving, and colours that would make text hard to read are refused
(WCAG AA contrast). How it works: `core/theme.py`.

**Text conventions.** Coloured words in a title → *Words in the title to colour*. Line break in a short label → `|`.
New paragraph → blank line. Bold → `**like this**`. Icons → Font Awesome names such as `fa-users`.

## Run it locally (Windows)

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 manage.py migrate
py -3.13 manage.py seed_content           # loads all the content and its photos
py -3.13 manage.py createsuperuser        # or: copy_original_admins --db "<original site db.sqlite3>"
py -3.13 manage.py runserver 127.0.0.1:8010
```

Site: <http://127.0.0.1:8010/> · admin: <http://127.0.0.1:8010/admin/>. Locally the database is SQLite; on the server
it is PostgreSQL (set by environment variables). Use `py -3.13` explicitly: a `.venv` left active from another folder can
make plain `py` pick a Python without Django.

## Tests

```powershell
py -3.13 manage.py test core                  # 64 tests
py -3.13 manage.py test core.tests.test_css   # one file
```

| File | Covers |
| --- | --- |
| `test_site.py` | every page and section type renders; edits show on the site; contact form |
| `test_admin.py` | admin login, editing, drafts, scheduling, version history |
| `test_seo.py` | titles, descriptions, canonical links, structured data, sitemap, robots, redirects, image resizing |
| `test_css.py` | the universal-CSS rules (tokens only, standard breakpoints, no inline styles) |
| `test_audit.py` | security headers, pagination, page weight, accessibility fixes |
| `test_theme.py` | colour schemes: recolouring, readability checks, admin picker, staff-only preview |

## Project structure

```text
config/                  settings (env-based; production security), URLs, WSGI
core/
  models.py              content tables: Page → Section → Item, SiteSettings, NavItem, Footer*, Program,
                         SuccessStory, BlogPost, TeamMember, Service, ContactMessage, Redirect, Revision
  views.py               pages (with pagination), blog / story pages, contact form, previews, robots.txt, sitemap.xml
  layouts.py             which fields each section type uses (drives the admin form)
  theme.py               colour schemes: three brand colours → the whole palette
  versioning.py          drafts, scheduled publishing, version history
  seo.py                 titles, descriptions, canonical / prev / next links, Open Graph, JSON-LD
  images.py              shrinks and compresses uploaded photos
  signals.py             automatic redirect when a page / post / story address changes
  middleware.py          redirects from Admin → Redirects; Permissions-Policy header
  context_processors.py  site settings, menu, footer and the active colour scheme for every page
  adminpanel/            the admin panel at /admin/: views, forms, urls
  management/commands/   seed_content, copy_original_admins, publish_scheduled
  templatetags/          template helpers (title highlight, line breaks, waves, motifs, colours)
  motifs.py              the background drawings
  seed/                  seed data (photo list, original site content)
  tests/                 the test suite
templates/
  base.html, page.html, detail.html, 404.html
  sections/<type>.html   one template per section type (21)
  partials/              header, logo + wordmark, buttons, 3D coin, story card, pagination, SEO tags
  adminpanel/            admin panel screens (incl. the colour-scheme picker)
static/
  css/wise-teck.css      THE site stylesheet (universal, token based)
  css/adminpanel.css     admin panel stylesheet (its own --ap-* tokens)
  js/                    site behaviour, waves, 3D coin, admin helpers
  img/                   logo mark (svg + 512px png), wordmark, favicon
media/seed/              photos used by seed_content
CLAUDE.md                commands and conventions for Claude Code sessions
.claude/                 project hook (no AI attribution in commits) and skills (deploy, new-section-layout)
DEPLOY.md                server setup and updating the live site
```

## Design system (universal CSS)

Everything is styled by `static/css/wise-teck.css`: plain modern CSS, no framework. Every colour, font size, line
height, space, radius and z-index is a token in the `:root` blocks at the top. Cascade layers, later wins:
`vendor → site → type → layout → system`.

| Rule | Value |
| --- | --- |
| Content width / side gaps | 1200px, centred; 16px phone, 24px tablet; the header lines up with the content |
| Fluid sizes | font sizes and spacing grow in a straight line from phone (390px) to desktop (1440px) |
| Section padding | the same for every section at a given width: 48px phone → 80px desktop |
| Heroes | home fills the first screen; every inner hero has one height per screen: 720px desktop and tablet, 830px phone |
| Typography | Inter; one style per role: h1 30/32 → 48/52, h2 26 → 36, h3 20, intro 18, paragraphs 16 / 1.7, labels 14, tag lines 13 caps |
| Line breaks | headings break into even lines; on tablets text keeps its desktop line breaks |
| Text spacing | `class="rhythm"` spaces a text block's children (tag line → heading 12, h1 → next 20, h2 → 16, text → buttons 24) |
| Cards | one padding scale (32 / 24 / 40px; phones 24 / 20 / 24), radius 24px |
| Breakpoints | 1200px (menu → menu button), 1024px (tablet), 640px (phone) |
| Touch | buttons and links have at least a 44px touch area |

Rules enforced by `core/tests/test_css.py`: no hard-coded colours / radii / font sizes / z-index outside the tokens, tokens
only in `:root`, only the breakpoints above, no inline styles in templates. New section type: see the
`new-section-layout` skill in `.claude/skills/`.

## SEO and performance

- Per page: title (50–60 characters), description (120–160; longer ones are clipped automatically), canonical link,
  robots, Open Graph / X cards, JSON-LD (organisation, website, breadcrumbs, articles). Page 2+ of a list has its own
  canonical and prev / next links.
- Generated `/sitemap.xml` and `/robots.txt`; changed addresses redirect (301); uploads are resized and compressed.
- Light pages: no inline drawings, the 3D library loads after the page, photos below the first screen load lazily.
- Security headers: Content-Security-Policy, HSTS, Permissions-Policy, X-Frame-Options, Referrer-Policy.
  `manage.py check --deploy` passes.

## Commands

| Command | Does |
| --- | --- |
| `manage.py seed_content` | Load the content into an empty database (`--reset` wipes admin edits: never on the live server). |
| `manage.py copy_original_admins --db <file>` | Copy the original site's admin login(s). |
| `manage.py publish_scheduled` | Publish drafts whose *Go live at* has passed (the server runs it every minute). |
| `manage.py test core` | Run the tests. |

## Commit rules

Author `Engineer00 <salman.k.786000@gmail.com>`, no AI attribution (a project hook blocks it). Work on a feature
branch, push it, then fast-forward `main`.
