# Wise-Teck v3 (Django)

The Wise-Teck v3 website, fully editable. The look is the v3 static site's (same HTML, CSS and JavaScript); every word, link, photo, menu item and section is stored in the database and editable in the admin panel.

- **Site:** `/` and `/<page>/` (for example `/about/`, `/contact/`)
- **Admin panel:** `/admin/` (login required)
- **Django's built-in admin (fallback):** `/django-admin/`

## Run it locally (Windows)

```powershell
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py seed_content        # loads all v3 content and downloads its photos
.venv\Scripts\python manage.py copy_original_admins --db "D:/wise teck site/wise_teck ORIGINAL/db.sqlite3"
                                                   # the same admin login as the original site (or: createsuperuser)
.venv\Scripts\python manage.py runserver 127.0.0.1:8010
```

Open http://127.0.0.1:8010/ (site) and http://127.0.0.1:8010/admin/ (admin panel).

Locally the database is SQLite (`db.sqlite3`). On the server it is PostgreSQL, set through environment variables (see [DEPLOY.md](DEPLOY.md)).

## How content is organised

| In the admin panel | What it controls |
|---|---|
| **Website → Pages** | Each page: web address, browser title, SEO description, published or not. Open a page to see and edit its sections. |
| **Website → Sections** | The blocks of a page, top to bottom (`order`). Each has a **layout** (hero, cards, steps, quote, call-to-action …), its text, buttons, photos and **cards** (the repeated items: cards, steps, tags, stats). The form shows only the fields the chosen layout uses. |
| **Website → Menu** | Top menu and drop-downs. |
| **Website → Programs** | The three-program strip shown on many pages. Edit once, every page updates. |
| **Website → Footer** | Footer link columns. |
| **Website → Site Settings** | Logo, top bar, phone / email / address (top bar, footer and links), header button, footer tagline, social links, contact-form alert email, SEO default, 3D coin colours. |
| **Content → Success Stories** | Learner stories: home slider and the Success Stories page. A story with a "full story" gets its own page. |
| **Content → Blogs / Team / Services** | Posts (with their own pages at `/blog/<slug>/`), team members and services. Show them on any page by adding a section with the Blog / Team / Services layout. |
| **Inbox → Messages** | Contact-form messages (mark read / unread). |

### Text conventions

- **Coloured words in a title:** type the words in *Words in the title to colour*.
- **Line break in a short label** (tags, feature icons): type `|`, e.g. `Skills|Development`.
- **Paragraphs:** leave a blank line. **Bold:** `**like this**`.
- **Icons:** Font Awesome names, e.g. `fa-users`, `fa-graduation-cap` (fontawesome.com/icons, free solid set).

### Section layouts

Page tops: *Home hero* (3D coin), *Inner page hero* (breadcrumb, facts, photo with badge or stats, or 3D coin).
Home blocks: About, Ecosystem circle, Program cards, Services + skill tiles, Weekend banner, Stories slider, Corporate + collaborators.
General: Text + quote / photo / checklist, Icon cards, Numbered steps, Programs strip, Photo cards (earning blocks), Stories grid, Placeholder notice, Call-to-action band, Contact details + form, Blog / Team / Services lists.

The full field-by-field guide per layout is in `core/layouts.py` (also shown in the admin form).

## Commands

| Command | Does |
|---|---|
| `manage.py seed_content` | Load the v3 content into an empty database. |
| `manage.py seed_content --reset` | Wipe website content and load it again. **Admin edits are lost.** |
| `manage.py copy_original_admins --db <original db.sqlite3>` | Copy the original site's admin login(s), same username and password. |
| `manage.py seed_content --no-download` | Keep photo links instead of downloading the photos. |
| `python tools/compare_with_v3.py` | Check every page against the v3 static site, tag by tag (needs `../wise-teck-v3`). Expect `TOTAL DIFF LINES 0` right after seeding. |

## Project layout

```
config/            settings (SQLite locally, PostgreSQL via env vars), URLs
core/models.py     all content tables
core/layouts.py    what each section layout uses (drives the admin form)
core/views.py      pages, blog / story detail, contact form
core/adminpanel_*  the admin panel (from the original site, extended)
core/management/commands/seed_content.py   the v3 content
core/motifs.py     background drawings (from v3 tools/motifs.py)
templates/         base.html, page.html, sections/<layout>.html, partials/, adminpanel/
static/            v3 CSS / JS / images (unchanged) + site-extras.css + admin panel files
```

## Drafts, scheduled publishing and version history

**Version history.** Every save or delete in the admin panel keeps the version from before it: for a page, a copy of the whole page with all its sections and cards; for menu items, footer columns (with their links), programs, settings, stories, posts and so on, a copy of that item. Open a page (or any item) and scroll to **Version history**:
- **Preview** shows an old page version exactly as it looked, without changing anything.
- **Open as draft** copies an old version into a draft, so you can check or adjust it before it goes live.
- **Restore** puts the old version back live at once. The version it replaces is kept too, so a restore can be undone.

The newest 60 versions of each page or item are kept. The dashboard shows the latest changes and who made them.

**Drafts.** On a page, **Create draft** makes a private copy of the page with all its sections and cards. Edit the draft's sections as usual: visitors keep seeing the live page. **Preview draft** shows it as visitors will see it. **Publish now** replaces the live page with the draft (the old live version goes into the history); **Discard draft** throws it away. The page address never changes.

**Scheduled publishing.** On a draft, set **Go live at** and save: the draft replaces the live page at that time. Blog posts and success stories have their own **Go live at**: they stay hidden until then (they must also be marked Published). The dashboard lists everything scheduled. Scheduled drafts go live on the first visit after their time; on the server a one-minute timer makes it exact (see DEPLOY.md).

## SEO

Built to current search-engine best practice; everything is editable in the admin.

| What | Where it comes from | Edit in |
|---|---|---|
| `<title>` and meta description | Each page's title and SEO description (aim for 50–60 and 120–160 characters) | Pages → Page |
| Canonical link | The page's own address on the main web address (or an override) | Site Settings → Main web address; Pages → Canonical |
| `robots` meta | `index, follow` for live pages; `noindex` for drafts, previews, 404 and pages marked “Hide from search engines” | Pages → Hide from search engines |
| Link previews (Open Graph, X cards) | Sharing title / description / image, falling back to the page title, description and main photo, then the default sharing image | Pages → Link previews; Site Settings → Default sharing image |
| Structured data (JSON-LD, schema.org) | Home: EducationalOrganization (name, logo, phone, email, address, social profiles) + WebSite. Every page: WebPage + BreadcrumbList from its breadcrumb. Blog posts: BlogPosting; stories: Article | Site Settings (organisation details); page hero breadcrumb |
| `/sitemap.xml` | Every published, indexable page, blog post and full success story, with last-changed dates | automatic |
| `/robots.txt` | Blocks the admin and previews, points to the sitemap; extra rules optional | Site Settings → Extra robots.txt rules |
| Redirects (301) | Old addresses → new ones. Changing a page, blog post or story address adds one automatically (no chains) | Website → Redirects |
| Addresses (slugs) | Short, lowercase, hyphenated; system addresses (admin, static, media, preview …) are refused | Pages → Address |
| Images | New uploads are rotated correctly, resized to max 2000 px, compressed and stripped of camera data; every image has editable alt text | automatic; “Photo description” fields |
| Page structure | One `<h1>` per page, sections use `<h2>`/`<h3>`, `lang="en"`, mobile-first responsive layout | templates |
| Google Search Console | Verification tag | Site Settings → Google Search Console code |

After going live: set **Site Settings → Main web address** (e.g. `https://wise-teck.dev`), add the site in Google Search Console, and submit `https://<domain>/sitemap.xml`.
