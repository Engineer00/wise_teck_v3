# Wise-Teck

The Wise-Teck website: a dynamic Django site where every page, section, word, link, photo, menu item, colour and
setting lives in the database and is edited in a friendly admin panel. No code is needed to run the site day to day.

- **Live:** <https://wiseteck.dev> (admin: <https://wiseteck.dev/admin/>)
- **Repository:** <https://github.com/Engineer00/wise_teck_v3> (`main` is the version to deploy; every push is tested by CI)
- **Server:** Namecheap VPS (Ubuntu 24.04, Python 3.12, PostgreSQL), next to `dehleze.store`. Day-to-day server work and code changes: [SERVER-ACCESS.md](SERVER-ACCESS.md); setup, security and backups: [DEPLOY.md](DEPLOY.md).
- **Versions:** Django 6.1.3 and the other exact versions in `requirements.txt` (the versions the tests run on).
- **History:** [CHANGELOG.md](CHANGELOG.md) records what changed, why, the decisions and the open items; its
  *Current status* says which version is live (`main` was deployed on 22 November 2026).

## What the admin can change

| Admin section | What it controls |
| --- | --- |
| **Dashboard** | Visitors (last 30 days, top pages, where visitors come from, phone / tablet / desktop), **SEO health** score with fix-it links, **Google Lighthouse** scores for every page (daily, phone and desktop), Google tools, messages, drafts, recent changes. |
| **Website → Pages** | Each page: address, title, search description, sharing preview, published or hidden. **Drafts**, **scheduled publishing** and **version history** with one-click restore. |
| **Website → Sections** | The blocks of a page, in order. 22 section types; the form shows only the fields the type uses, with the best photo size next to every photo field. **Extra details**: label + value rows (e.g. *Fee · Rs 15,000*) added to a section without a developer, shown as a small table in text, card, step, team, services and course sections. |
| **Website → Menu / Footer / Programs** | Top menu and drop-downs, footer link columns, the three-program strip. |
| **Website → Site Settings** | Logo, **colour scheme**, **announcement bar**, contact details, header button, footer, social links, contact-form messages and alerts, **404 page**, search engines, **Google Analytics ID**, keywords to watch. |
| **Website → Redirects** | Old addresses → new ones. Added automatically when a page address changes. |
| **Content → Success Stories / Blogs / Team / Services** | Lists shown by the matching sections. Blog posts and stories have their own pages; long lists get page numbers. |
| **Content → Courses** | Professional paid courses: name, what students learn, duration, fee, weekend schedule, next start date (hidden once passed). Shown as cards on the Professional Paid Courses page, each with an enquiry link; the section appears once the first course is added. |
| **Inbox → Messages** | Contact-form messages. |

**Colour schemes.** Site Settings → *Colour scheme*: six ready-made schemes or *Custom colours* (primary, accent,
dark). Buttons, backgrounds, waves, footer and the 3D coin's rings follow; *Preview on the website* shows it before
saving; colours that would make text hard to read are refused (WCAG AA). How it works: `core/theme.py`.

**Text conventions.** Coloured words in a title → *Words in the title to colour*. Line break in a short label → `|`.
New paragraph → blank line. Bold → `**like this**`. Icons → Font Awesome names such as `fa-users`.

### Fixed on purpose

Some things are deliberately not editable, so the site always looks right on every screen:

- **The logo** keeps its colours in every colour scheme (header, footer, 3D coin face). Change it by uploading a new one.
- **Typography and spacing:** one font (Inter), one size per role per screen size, the same spacing for every section.
- **Layout and breakpoints:** desktop, tablet (below 1024px) and phone (below 640px) layouts; the menu button below 1200px.
- **Wave and background drawings:** their shapes and motion stay; their colours follow the colour scheme.
- **Status colours** (red errors, green success) and the security settings.

## Photo sizes

The admin shows the best size next to every photo field (hover the badge for where the photo appears). Upload JPG
for photos and PNG for logos; up to 20 MB. Every upload is turned the right way up, stripped of camera data, resized
to at most 2000px and compressed, and the site serves WebP copies at 480 / 800 / 1200 / 1600px so phones download
small files. Bigger photos are fine; smaller ones look soft on sharp screens.

| Where it appears | Best size (px) | Shape |
| --- | --- | --- |
| Inner-page hero photo; top of a blog post or story | 1920 × 800 | wide banner (2.4 : 1) |
| Second hero photo (next to the first, when the hero has stats) | 1200 × 500 | wide |
| Home · About photo | 1200 × 800 | 3 : 2 |
| Photo beside text (split section) | 1400 × 1050 | 4 : 3 |
| Home · Weekend courses photo | 1400 × 960 | landscape |
| Home · Corporate collaborations photo | 1440 × 600 | wide |
| Card photos: programs, earning blocks, team | 800 × 500 | 16 : 10 |
| Home · photo tiles | 800 × 450 | 16 : 9 |
| Blog post photo (card on lists, banner on the post) | 1920 × 1080 | 16 : 9, subject centred |
| Success-story photo (round on lists) | 1000 × 1000 | square, face centred |
| Collaborator logo | 400 × 200 | transparent PNG |
| Service icon | SVG, or 112 × 112 PNG | square |
| Round logo (shown 40–48px in the header and footer, larger on the home page and 3D coin) | 512 × 512 | square transparent PNG |
| Browser tab icon | 512 × 512 | square PNG |
| Sharing preview (WhatsApp, Facebook, LinkedIn, X); a built-in Wise-Teck card is used when empty | 1200 × 630 | 1.9 : 1 |

**Video:** the site has no video upload (videos make a server slow and expensive). Put videos on YouTube (1920 × 1080,
MP4) and link them from a button, e.g. the home page's *Watch Overview*.

The sizes live in one place, `core/images.py` (`SLOTS`), which the admin badges read.

## SEO

**Automatic (nothing to do):** page titles of at most 60 characters (the " | Wise-Teck" suffix is left off when it
would not fit), descriptions cut at 160 characters, canonical links, page 2+ of lists with their own canonical and
prev / next links, `/sitemap.xml` (updates itself), `/robots.txt`, `/llms.txt` (the same pages, written for AI search
such as ChatGPT, Gemini and Perplexity), structured data (educational organisation, website,
breadcrumbs, articles, courses), sharing previews with a 1200 × 630 default image, 301 redirects when an address changes,
`noindex` on drafts, previews and the 404 page, responsive WebP photos, lazy loading, fast pages. The dashboard's
**SEO health** runs every check on every live page, post and story each time it opens, and the **Lighthouse** panel
shows Google's daily speed, SEO and accessibility check of every page (see *Lighthouse* below).

**Your part, once:** Site Settings → *Main web address* = `https://wiseteck.dev`; verify Google Search Console (paste
the code into Site Settings) and submit the sitemap (dashboard → Google tools → Copy); create the Google Business
Profile (Lahore); add the site to Bing Webmaster Tools (one click: import from Search Console; Bing's index also
feeds ChatGPT search and Copilot); optionally add a Google Analytics ID; switch on the Lighthouse panel (DEPLOY.md).

**Your part, ongoing:** publish useful content (two or more blog posts a month around the keywords in Site Settings),
fix what SEO health and Lighthouse list, describe every photo, ask students for Google reviews, and ask partners
(PSDF, NIC, universities, employers, local directories, education portals) to link to the site. Keep the name,
address and phone identical everywhere.

**Automated vs. not:** technical SEO and monitoring are automatic (SEO health, daily Lighthouse, Search Console
alerts once verified). Backlinks can be *monitored* (Search Console → Links, or the free Ahrefs Webmaster Tools) but
not created by software: bought or automated links break Google's spam policies and can get the site removed from
results. Content can be drafted with AI help, but a person should review it and add real facts.

**KPIs (targets):**

| Area | KPI | Target | Where to see it |
| --- | --- | --- | --- |
| Technical | SEO health score | 95+ | Admin dashboard |
| Speed | Core Web Vitals on phones | LCP < 2.5 s, INP < 200 ms, CLS < 0.1 | PageSpeed Insights, Search Console |
| Indexing | Pages indexed vs pages in the sitemap | all, 0 errors | Search Console → Pages |
| Visibility | Impressions, clicks, click-through rate | growing monthly; CTR 3%+ | Search Console → Performance |
| Rankings | Average position for the keywords to watch | top 10 | Search Console → Queries |
| Traffic | Visitors from Google | growing monthly | Dashboard → Where visitors come from |
| Leads | Contact messages per month | growing monthly | Dashboard → Messages |
| Local | Business Profile views, calls, reviews | 4.5★+ | Google Business Profile |

Technical SEO can be made complete and is checked automatically; rankings also depend on content and other sites
linking here, so nobody can honestly guarantee positions.

## Speed

Measured on a simulated mid-range phone over slow 4G (Lighthouse's mobile settings), median of 3 loads:

| Page | Largest content shown: live site before | This version |
| --- | --- | --- |
| Home | 12.2 s | 1.8 s |
| About | 8.1 s | 1.7 s |
| Blog | 11.1 s | 1.4 s |
| Blog post | 7.4 s | 1.7 s |

How: fonts and icons served from the site (no outside servers before text shows), no inline drawings, WebP photos
in the right size, lazy loading below the first screen, the 3D library loaded when the browser is idle, first-screen
content shown at once (no fade-in), long lists split into pages.

## Lighthouse (daily, automatic)

Every day at 00:30 UTC (05:30 in Pakistan) `.github/workflows/lighthouse.yml` runs Google Lighthouse 13 on GitHub's
servers against every page in the live sitemap, on a phone and a desktop (`tools/lighthouse/run.mjs`; a lost trace is
retried up to 3 times). Results:

- the run page on GitHub: a table of every page's scores, and the full HTML reports to download (kept 30 days);
- the admin dashboard, when the repository secret `LIGHTHOUSE_TOKEN` equals the server's `LIGHTHOUSE_TOKEN`: the
  workflow posts a summary to `/api/lighthouse/` (403 for a wrong token, 404 when the server has none; every value is
  checked and trimmed in `core/lighthouse.py`). The panel shows the average Performance, Accessibility, Best
  practices and SEO scores with the change since the previous day, Core Web Vitals of the home page, the most common
  suggestions and every page's scores. The newest 120 checks are kept.

Start one by hand: GitHub → Actions → Lighthouse → *Run workflow* (the dashboard links there). Nothing runs on the
web server. Switching it on: DEPLOY.md → *Daily Lighthouse check*.

## Security

- Headers on every page: Content-Security-Policy (scripts, styles and fonts only from the site itself), HSTS,
  X-Frame-Options, Referrer-Policy, Permissions-Policy. `manage.py check --deploy` passes.
- Admin: password guessing stopped after 5 wrong tries per address (15 minutes' wait); sessions end after 8 hours;
  staff-only previews. Contact form: spam trap and 5 messages per 10 minutes per address.
- Uploads: images checked by Pillow; SVG icons containing scripts are refused; camera data (location) removed.
- Visitor statistics store no cookies and no IP addresses (a daily-changing one-way hash).
- Dependencies pinned; Dependabot proposes security updates weekly; CI tests every change.
- Server hardening (firewall, fail2ban, SSH keys, backups): DEPLOY.md → *Server security*.

## Run it locally (Windows)

```powershell
py -3.13 -m pip install -r requirements-dev.txt
py -3.13 manage.py migrate
py -3.13 manage.py seed_content           # loads all the content and its photos
py -3.13 manage.py createsuperuser        # or: copy_original_admins --db "<original site db.sqlite3>"
py -3.13 manage.py runserver 127.0.0.1:8010
```

Site: <http://127.0.0.1:8010/> · admin: <http://127.0.0.1:8010/admin/>. Locally the database is SQLite; on the server
it is PostgreSQL (set by environment variables). Use `py -3.13` explicitly: a `.venv` left active from another folder can
make plain `py` pick a Python without Django.

## Tests and code quality

```powershell
py -3.13 manage.py test core                  # 108 tests
py -3.13 -m ruff check .                      # lint (rules in pyproject.toml)
py -3.13 -m ruff format .                     # formatting
```

GitHub Actions (`.github/workflows/ci.yml`) runs lint, formatting, the migration check, Django's production
checklist and all tests on Python 3.12 + PostgreSQL 16 (as on the server) for every push.

| File | Covers |
| --- | --- |
| `test_site.py` | every page and section type renders; edits show on the site; contact form |
| `test_admin.py` | admin login, editing, drafts, scheduling, version history |
| `test_seo.py` | titles, descriptions, canonical links, structured data, sitemap, robots, redirects, image resizing |
| `test_css.py` | the universal-CSS rules (tokens only, standard breakpoints, no inline styles) |
| `test_audit.py` | security headers, pagination, page weight, accessibility fixes |
| `test_theme.py` | colour schemes: recolouring, readability checks, admin picker, staff-only preview |
| `test_features.py` | visitor statistics, SEO health, rate limits, announcement, 404 texts, Analytics, WebP photos, size hints |
| `test_lighthouse.py` | the Lighthouse endpoint (token, cleaning, keeping 120 runs), the dashboard panel, the SEO fixes it found (link names, heading order, `/llms.txt`) |
| `test_custom_fields.py` | courses (cards, hidden past start dates, enquiry link, structured data, admin) and section extra details (table, admin box, version history, drafts) |

## Project structure

```text
config/                  settings (env-based; production security), URLs, WSGI
core/
  models.py              content tables: Page → Section → Item / Detail (extra details), SiteSettings, menu, footer,
                         programs, stories, blog, team, services, courses, messages, redirects, versions, visitor
                         statistics, rate-limit attempts
  views.py               pages (with pagination), blog / story pages, contact form, previews, robots.txt, sitemap.xml,
                         llms.txt, the Lighthouse results endpoint
  lighthouse.py          daily Lighthouse results: checks what the workflow sends, builds the dashboard panel
  layouts.py             which fields each section type uses, its photo sizes and whether it shows extra details
                         (drives the admin form)
  images.py              upload shrinking, responsive WebP copies (srcset), recommended photo sizes
  theme.py               colour schemes: three brand colours → the whole palette
  seo.py / seo_audit.py  search-engine tags and structured data / the SEO health checks
  stats.py               cookie-free visitor statistics for the dashboard
  throttle.py            rate limits for sign-in and the contact form
  permissions.py         staff-only access
  versioning.py          drafts, scheduled publishing, version history (pages with their sections, cards, details)
  signals.py             automatic redirect when a page / post / story address changes
  middleware.py          redirects, Permissions-Policy, Analytics CSP
  context_processors.py  site settings, menu, footer and the colour scheme for every page
  adminpanel/            the admin panel at /admin/: views, forms, urls
  management/commands/   seed_content, copy_original_admins, publish_scheduled, make_image_variants
  templatetags/          template helpers (title highlight, line breaks, waves, motifs, colours, srcset)
  motifs.py              the background drawings
  seed/                  seed data (photo list, original site content)
  tests/                 the test suite
templates/
  base.html, page.html, detail.html, 404.html, 500.html
  sections/<type>.html   one template per section type (22), plus _details.html (the extra-details table)
  partials/              header, logo + wordmark, buttons, 3D coin, story card, pagination, SEO tags
  adminpanel/            admin panel screens (dashboard, forms, colour-scheme picker)
static/
  css/wise-teck.css      THE site stylesheet (universal, token based)
  css/adminpanel.css     admin panel stylesheet (its own --ap-* tokens)
  js/                    site behaviour, waves, 3D coin, analytics loader, admin helpers
  img/                   logo mark, wordmark, favicon, default sharing card
  vendor/                Inter font and Font Awesome Free, served from the site
media/seed/              photos used by seed_content
.github/                 CI workflow, daily Lighthouse workflow, Dependabot
tools/lighthouse/        the Lighthouse runner used by that workflow
pyproject.toml           Ruff lint and format rules
CLAUDE.md                commands and conventions for Claude Code sessions
.claude/                 project hook (no AI attribution in commits) and skills (deploy, new-section-layout)
DEPLOY.md                server setup, updating the live site, server security, backups
SERVER-ACCESS.md         logging in to the server, finding your way, changing the code and putting it live
```

## Design system (universal CSS)

Everything is styled by `static/css/wise-teck.css`: plain modern CSS, no framework. Every colour, font size, line
height, space, radius and z-index is a token in the `:root` blocks at the top. Cascade layers, later wins:
`vendor → site → type → layout → system`.

| Rule | Value |
| --- | --- |
| Content width / side gaps | 1200px, centred; 16px phone, 24px tablet; the header lines up with the content |
| Fluid sizes | font sizes and spacing grow in a straight line from phone (390px) to desktop (1440px) |
| Section padding | the same for every section at a given width: 48px phone → 80px desktop; sections are as tall as their content (equal spacing, not forced equal heights), so the gap between any two sections is the same: 96px phone, 119px tablet, 160px desktop |
| Heroes | home fills the first screen; inner heroes are 720px on desktop and tablet, at least 700px on phones (content-heavy ones grow) |
| Call-to-action band | the purple band ending each inner page has one minimum height per screen: 360px desktop, 408px at 1024–1199px, 448px tablet, 560px phone (no maximum: longer text makes it taller) |
| Typography | Inter only; one style per role: h1 30/32 → 48/52, h2 26 → 36, sub-heading 22 → 28, h3 20, intro 18, text 16 / 1.7, labels 14, tag lines 13 caps; form fields 16 (no zoom on phones) |
| Phones | one card per row; sliders show one card; small icon tiles two per row; photo first, text below in photo + text sections |
| Buttons (phones + tablets) | 52px tall; every button in a group as wide as the widest one, never under 244px; hero button pairs centred |
| Text spacing | `class="rhythm"` spaces a text block's children (tag line → heading 12, h1 → next 20, h2 → 16, text → buttons 24) |
| Cards | one padding scale (32 / 24 / 40px; phones 24 / 20 / 24), radius 24px |
| Extra details | a glass table of label + value rows: under the cards (up to 800px wide, centred), or full width in the text column of a split section |
| Breakpoints | 1200px (menu → menu button), 1024px (tablet), 640px (phone) |
| Touch | buttons and links have at least a 44px touch area |

Rules enforced by `core/tests/test_css.py`: no hard-coded colours / radii / font sizes / z-index outside the tokens,
**every margin, padding and gap from a spacing token** (a new section needs no spacing CSS of its own), tokens only in
`:root`, only the breakpoints above, no inline styles in templates. The few deliberate overlaps have named tokens
(`--feature-overlap`, `--hero-wave-room`, `--eorbit-shift` ...). New section type: see the
`new-section-layout` skill in `.claude/skills/`.

## Commands

| Command | Does |
| --- | --- |
| `manage.py seed_content` | Load the content into an empty database (`--reset` wipes admin edits: never on the live server). |
| `manage.py copy_original_admins --db <file>` | Copy the original site's admin login(s). |
| `manage.py publish_scheduled` | Publish drafts whose *Go live at* has passed (the server runs it every minute). |
| `manage.py make_image_variants` | Make the WebP copies of every photo ahead of time (after a deploy or bulk upload). |
| `manage.py test core` | Run the tests. |

## Commit rules

Author `Engineer00 <salman.k.786000@gmail.com>`, no AI attribution (a project hook blocks it). Work on a feature
branch, push it (CI runs), then fast-forward `main`.
