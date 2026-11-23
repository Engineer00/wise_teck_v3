# Changelog

The record of work on the Wise-Teck website: what changed, why, and where things stand. Newest first.
How to run, test and deploy the site: [README.md](README.md) and [DEPLOY.md](DEPLOY.md).

## Current status (22 November 2026)

| | |
| --- | --- |
| **GitHub** | `main` holds the latest version; CI (lint, migrations, production checklist, 108 tests on Python 3.12 + PostgreSQL) passes |
| **Live site** | https://wiseteck.dev runs `7b9f1ca` (deployed 22 Nov 2026): Django 6.1.3, migrations up to 0018, courses and extra details, equal call-to-action bands |
| **Next update** | DEPLOY.md, *Update the live site* (git pull). Still to do once: *Server security* (fail2ban, firewall, SSH keys, daily backups) |
| **Server folder** | `/srv/wiseteck/app` (code), `/srv/wiseteck/.env` (settings), `/srv/wiseteck/app/media` (uploads). dehleze.store lives separately in `/home/dehleze/` and is never touched |
| **Passwords** | The server `root` and live admin passwords were changed to strong random ones on 21 Nov 2026 and shared privately. They are never written in this repository (it is public) |

## 2026-11-23: server secured (fail2ban, firewall, daily backups)

- Read-only check: 298,509 failed root password guesses over SSH in 30 days (25 Oct to 23 Nov), from 2,038
  addresses, mostly username `root`. No break-in: every successful login in 10 days is accounted for. Evidence kept
  on the server in `/root/security-evidence-2026-11-23/`.
- Applied (DEPLOY.md, *Server security*): fail2ban (5 wrong tries in 10 minutes = 1 hour ban, growing to a week for
  repeat offenders; watching `ssh.service`, the Ubuntu 24.04 name), firewall (only 22, 80, 443), daily backups of the
  database and uploaded photos at 02:30 UTC kept 14 days (`/root/backups/`). Both websites checked after each step.
- Still to do: a reboot at a quiet hour (pending updates); keys-only SSH login is optional.
- SERVER-ACCESS.md: a step-by-step quick start, what each tool is and why we use it, the important files in the zip.
- The header coin rests face-on (lined up with the top bar) and turns once every 8.5 s.

## 2026-11-23: daily Lighthouse on the dashboard, SEO 100, smooth hovers, top bar aligned

- **Daily Google Lighthouse check** (`.github/workflows/lighthouse.yml`): every page in the sitemap, phone and
  desktop, on GitHub's servers at 05:30 Pakistan time. Results on the run page (table, full reports) and, with the
  `LIGHTHOUSE_TOKEN` secret, in a new *Speed & quality* panel on the admin dashboard: average scores with the change
  since the day before, Core Web Vitals of the home page, the most common suggestions, every page's scores.
- **SEO and accessibility fixes Lighthouse found on the live site:** "Read More" links now say which page they open
  (hidden text for Google and screen readers, no visible change); the contact form title is an h2 (no skipped
  heading level); new `/llms.txt` for AI search. Home and blog SEO 92 → 100, contact accessibility 98 → 100.
- **Smooth hovers everywhere:** links fade their colour; cards (programs, services and others) lift again on hover.
  The scroll fade-in had been holding them flat for good.
- **Top bar lines up with the header** at every width: its first item over the logo, its last item over the
  right edge of the Apply button (it was 44px inside above 1280px).
- Measured on the live site (Lighthouse 13.6, 23 Nov): accessibility, best practices and SEO 100 after the fixes;
  speed: home on desktop 89 (main content in 1.1 s), about on desktop 98, blog on a phone 95. Phone speed for every
  page will come from the first daily run (local runs on this PC often lose the speed trace).

## 2026-11-23: menu button resets after closing, brand-violet tap colour

- The phone/tablet menu button now always goes back to its three uneven lines (full, 70%, 45%) after the menu is
  closed. Before, the "lines line up" hover look stayed on after a tap (touch screens keep `:hover` on the last tapped
  element), so from the second time on it showed three equal lines. The hover look is now for a mouse only
  (`@media (hover:hover) and (pointer:fine)`), and after a click the resting icon shows until the mouse leaves.
- Tapping a link or button on a phone flashed the browser's default sky blue. The tap colour is now a light brand
  violet everywhere; the menu button shows a soft lavender ring while pressed.
- Checked in Chrome at 390px by touch (three open/close rounds) and at 1024px with a mouse.

## 2026-11-22: deployed to wiseteck.dev

- The live site moved from the 20 November version (`c119ede`) to `7b9f1ca`: everything from 21 and 22 November.
  Django 6.0.10 → 6.1.3, migrations 0004–0018 applied (content changes only where never edited in the admin).
- Backup taken first on the server: `/root/deploy-backup-2026-11-22-0633/` (database dump, uploaded photos,
  previous commit). It also keeps three files someone had edited directly on the server on 20 Nov and an extra
  migration made there; all of those edits were already in GitHub, so the server copy was reset to GitHub's.
- Checked after the deploy: every page, the sitemap, robots.txt and the admin (including Courses) open; home has its
  six waves; call-to-action band 360px desktop / 560px phone; security headers present; dehleze.store untouched.
- Seen once during the restart: three site workers took longer than 30 seconds while the WebP photo copies were made,
  and were replaced automatically (pages may have failed for a few seconds). Not repeated since.

## 2026-11-22: courses and extra details (the site's version of WordPress ACF custom fields)

- **Content → Courses** (new admin screen): one record per professional paid course with exactly the fields a
  course needs: name, what students learn, icon, duration, fee, weekend schedule, next start date, link, order, show.
  The Professional Paid Courses page lays them out automatically as cards: each card shows only the facts that are
  filled in, a start date disappears by itself once it has passed, and *Enquire Now* opens the contact form with
  "Professional Paid Courses" already chosen (a course can have its own link instead). The courses are also listed
  for Google as structured data (schema.org Course, for courses with a description).
- The hidden "[Placeholder] Course List, Fees & Timings" notice on that page became the new **Courses** section
  (migration 0018, only if the placeholder is unchanged). No courses are seeded: Wise-Teck has not sent its course
  list yet, so the section stays hidden and the live page looks the same until the first course is added.
- **Extra details on sections**: under *Extra details (label + value)* on a section's form, an editor adds rows such
  as *Fee · Rs 15,000* or *Certificate · Included* without a developer. They appear as a small table: in the text
  column of a text + photo / quote / checklist block, and under the cards in icon cards, steps, program strip, photo
  cards, team, services and courses sections. The box is shown only for those section types. Extra details are kept
  in version history and copied into drafts like the cards.
- Checked at 1440, 1024, 768 and 390px with sample courses and details (removed afterwards): gaps between sections
  unchanged (160 / 135 / 119 / 96px), course cards in a row equal height with their links aligned, no sideways
  scrolling; added and saved a detail through the admin in a browser. 11 new tests (94 in total).

## 2026-11-22: equal call-to-action bands, waves between every home section

- **Call-to-action band** (the purple band at the end of each inner page): it had no minimum or maximum height, so
  it varied from page to page with the length of its text (up to 98px apart at 1024px). It now has a **minimum**
  height per screen size, set just above the tallest band: **360px** desktop, **408px** at 1024-1199px, **448px**
  tablet, **560px** phone (`--band-min*` tokens). The content stays centred and the text keeps 40px to the buttons.
  No maximum: a longer text written in the admin makes that band taller instead of being cut off. Checked at 159
  widths from 360 to 1920px: every band is the same height at each width.
- **Home page waves**: the weekend-courses, success-stories and corporate sections had no wave between them, so the
  weekend card read as part of the stories. Waves added after weekend courses and success stories (data migration
  0016 changes them only if they still have no divider; the admin's "Wave divider after" field controls them).
  Gaps between sections are unchanged: 160px desktop, 135px at 1024px, 119px tablet, 96px phone.
- Section heights stay natural everywhere else (equal padding, equal gaps); only the inner heroes and this band
  have a fixed minimum.

## 2026-11-21: responsive polish, owner features, security, performance

### Design system and spacing
- One universal stylesheet (`static/css/wise-teck.css`), every value from a token. Spacing is 100% tokens: every
  margin, padding and gap (378 rules), enforced by `test_spacing_comes_from_tokens`. A second test fails if any
  `var(--token)` is used but never defined.
- Sections keep their natural height and every section has the same padding, so the gap between any two sections is
  the same: **160px desktop, 119px tablet, 96px phone** (forced 560px desktop section heights removed: they made the
  gaps uneven). Wave dividers add no extra space; a heading block never adds space above itself.
- 14 dead spacing rules removed after checking every rule on every page at six widths; verified that no element moved.
- One seamless background on every page (soft violet and champagne glows, faint dot texture); the repeating tile that
  drew hard lines across the page on phones is gone, and inner pages no longer use flat colour bands.
- Inter is the only font, on the site and in the admin, served from the site itself.

### Phones and tablets
- Home hero: 40px between the buttons and the 3D coin diagram at every width; the diagram's lowest label 24px above
  the wave; on phones the diagram's icons scale with it and the side labels sit above their icons, so no label touches
  an icon down to 320px.
- Inner heroes: equal space above the content and below it (to the wave). On phones at least 700px tall with at least
  40px of space each side (11 of 15 pages are exactly 700px; the four content-heavy pages grow just enough). The hero
  photo starts 24px below the wave.
- Inner photo pair: stacked and tilted on phones, 4px apart, the gold/navy frame hugging the photos; stat cards centred
  under the framed photos.
- One card per row; the stories slider shows one story; photo first, text below in photo / quote / checklist sections;
  form fields 16px (no zoom on iPhone); heading levels in order; centred sub-headings.

### Buttons
- Phones and tablets: every button 52px tall and 244px wide (the *Explore Partnerships* size); in a group every button
  is as wide as the widest; hero button pairs centred. Checked: all 35 buttons on every page are 244 x 52px.
- Six long labels shortened so they fit (migration 0015): Visit Earning Centre, Share Your Idea, Incubation Centre,
  Call Us Now, Student Loans.

### Menu (phones and tablets)
- Brand navy-violet blurred backdrop, light brand panel, brand-violet highlight with an accent bar for hover, open
  submenu and the current page; closes on a tap outside or Esc. The Apply Now button keeps the standard pill size.
- Menu button: glossy violet tile with a thin gold rim, stepped lines that turn into an X.

### Sections and cards
- Success stories: large ringed portraits (176px desktop, 112px phones); the two collage photos replaced by clean
  square portraits (migration 0012).
- Collaborators: logo fills the left half of the capsule, name the right half, all three equal size; the "Industry
  Collaborator" line removed (migration 0013).
- Weekend courses: five equal columns on tablet and desktop, two per row on phones.
- About hero: the "A project of Wise Education Society" chip hidden (migration 0014; can be switched back on).

### Photos and images
- The 32 seed photos that were 512px wide replaced by their full-size originals (1408 x 768), same file names.
- Every uploaded photo is served as WebP copies at 480 / 800 / 1200 / 1600px (srcset); `make_image_variants` makes them
  ahead of time. Default 1200 x 630 sharing card.
- The admin shows the best upload size next to every photo field (badge with tooltip); the table is in README.md.

### Owner features (admin)
- Dashboard: cookie-free visitor statistics (views, visitors, trend, top pages, sources, devices), SEO health score
  with fix-it links, Google tools (Search Console with sitemap copy button, Analytics, Trends for the keywords,
  PageSpeed, Rich Results, Business Profile).
- Site Settings: colour scheme (six presets + custom, readability check, preview), announcement bar, 404 page texts,
  contact-form messages, Google Analytics ID, keywords to watch.
- Admin look: calm neutral workspace, midnight-violet sidebar, one violet accent; summary cards, empty states, styled
  file inputs, 3 x 2 colour-scheme picker. The logo keeps its colours in every scheme.

### SEO
- Titles at most 60 characters (brand suffix dropped when it would not fit), descriptions at most 160, canonical and
  prev / next links, sitemap, robots.txt, structured data, 301 redirects on address changes, noindex on drafts and 404.
- Content fixes (migrations 0007, 0010): page titles and blog summaries brought within the limits.
- SEO health in the dashboard: 99/100 on the seed content.

### Performance (simulated mid-range phone, slow 4G)

| Page | Largest content shown: live site | This version |
| --- | --- | --- |
| Home | 12.2 s | 1.8 s |
| About | 8.1 s | 1.7 s |
| Blog | 11.1 s | 1.4 s |
| Blog post | 7.4 s | 1.7 s |

How: self-hosted fonts and icons, WebP photos in the right size, lazy loading, the 3D coin started when the browser is
idle, first-screen content shown at once, home page HTML from 278KB to 86KB.

### Security
- Content-Security-Policy (scripts, styles and fonts from the site only), HSTS, X-Frame-Options, Referrer-Policy,
  Permissions-Policy; `check --deploy` clean.
- Sign-in limited to 5 wrong passwords per address per 15 minutes (only the proxy-added address is trusted); contact
  form limited to 5 messages per 10 minutes; admin sessions end after 8 hours; SVG uploads with scripts refused.
- Read-only server check (21 Nov): about 9,000 password guesses a day against `root` over SSH, no firewall, no
  fail2ban, no backups; no sign of a break-in. Root and admin passwords changed to strong ones the same day. The
  remaining steps (fail2ban, firewall, SSH keys, reboot, daily backups) are in DEPLOY.md, *Server security*.

### Engineering
- Exact dependency pins (Django 6.1.3, the version tested), Ruff lint and format, GitHub Actions CI, Dependabot,
  `.editorconfig`, `.gitattributes`, self-contained 500 page, unused Django admin removed. 82 tests.

## 2026-11-20: universal CSS, test suite, global spacing (the version that is live)
- Universal token stylesheet, cascade layers, fluid sizes; permanent test suite; global spacing system; equal inner
  heroes; phone top bar removed. Commits `c119ede`, `afb262a`, `1fd40fd`.

## 2026-11-19: rebuilt on Django
- The static v3 design rebuilt as a dynamic Django site: every page, section, word, link, photo and setting editable in
  the admin panel (pages, sections, menu, footer, programs, stories, blogs, team, services, redirects, messages),
  drafts, scheduled publishing, version history. Commit `f4a36d1`. Live at https://wiseteck.dev since 20 Nov.

## Before 2026-11-19: static v3 design
- Design iterations of the static site: colour palette (violet, metallic gold, navy), footer, inner banners, feature
  photos, ecosystem orbit, universal layout system and mobile pass.

## Decisions (and why)

| Decision | Why |
| --- | --- |
| Equal spacing, not equal section heights | Forced equal heights leave short sections with extra space, which makes the gaps unequal; equal padding is the industry standard |
| Home hero fills the first screen; inner heroes share one height (phones: at least 700px) | Standard for home and inner pages; phones keep at least 40px around the content |
| Buttons 244 x 52px on phones and tablets, groups equal width | One button size everywhere; long labels shortened instead of making buttons wider |
| Hero text first on phones, photos first in content sections | The headline and buttons must be visible without scrolling; content sections read like cards |
| Inter only, one family | Consistent, premium, light to load |
| The logo keeps its colours in every colour scheme | A brand mark never recolours automatically; upload a new logo to change it |
| The admin has its own calm palette | Like Shopify or Stripe admin: the tool stays the same whatever the website's scheme |
| Fixed: type scale, spacing, layout, wave shapes | So nothing an editor changes can break the phone layout |

## Open items
- **Server security:** do the steps in DEPLOY.md once (fail2ban, firewall, key-only SSH, daily backups). The server
  has no automatic backups yet; the only copy is the one taken before the 22 Nov deploy.
- **Small server fixes (optional):** send www.wiseteck.dev to wiseteck.dev with a redirect (it shows the site
  directly; its canonical link already points to wiseteck.dev); stop the Gunicorn 27 warning "Control server error:
  Permission denied: /var/www/.gunicorn" in the site log (harmless).
- **Courses:** add Wise-Teck's courses in Content → Courses; the course list appears on the Professional Paid Courses
  page with the first one.
- **Owner accounts:** verify Google Search Console and submit the sitemap; create the Google Business Profile;
  optionally add a Google Analytics ID.
- **Server tidy-up:** remove `/root/attack.sh`, `/root/attack-report.txt` (an analysis report) and the empty
  `/var/www/wiseteck` folder.
- **Later:** a CSS consolidation pass (fold the old v3 override rules into single definitions, replace one-off tokens
  with a scale, add Stylelint); Search Console figures inside the admin (needs a Google Cloud service account).
