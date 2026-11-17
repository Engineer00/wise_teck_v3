# Wise-Teck Website (v3)

Static website for **Wise-Teck**, a project of Wise Education Society —
*Transforming Learning into Earning through Technology, Innovation and Entrepreneurship.*

Plain **HTML + CSS + vanilla JavaScript** (no build step needed to view it). A small Python
generator (`tools/`) builds every page from one shared layout so the whole site stays consistent.

---

## Tech stack

| Layer | Technology | Used for |
|---|---|---|
| Markup | **HTML5** (static, semantic) | 13 pages: home + 12 inner pages — no server code, no database |
| Styling | **CSS3** — one file `assets/css/wise-teck.css` | Design tokens (CSS custom properties), cascade layers (`vendor` → `site` → `type`), Grid & Flexbox, keyframe animations |
| Scripting | **Vanilla JavaScript (ES6)** — no framework | Menu, scroll reveal, slider (`wt.js`); live animated waves drawn as SVG with `requestAnimationFrame` + `IntersectionObserver` (`wt-waves.js`) |
| 3D | **Three.js** (bundled in `assets/js/vendor/`) | Spinning 3D coin in the hero (`hero-three.js`, from Wise-Teck v1) |
| Graphics | **Inline SVG** | Wave art, section motifs (globe, circuits, hexagons, skyline, world map), static fallback `wt-curves.svg` |
| Font | **Inter** (Google Fonts, weights 400–800) | All text, one uniform type scale |
| Icons | **Font Awesome 6.5** (CDN) | UI and section icons |
| Page generator | **Python 3** (`tools/build.py`, `tools/pages.py`) | Builds every HTML page from one shared layout + content file |
| Dev tools | Python + Pillow, NumPy, OpenCV (in `.venv`) | Static wave artwork, design tracing, PDF content check |
| Local server | `py -m http.server` | Viewing the site locally |
| Version control | **Git + GitHub**, GitHub CLI (`gh`) | Branches, pull requests |
| Hosting | Any static host (GitHub Pages, Netlify, cPanel, etc.) | Upload the HTML + `assets/` folder — no build step required |

Accessibility & performance: decorative art is `aria-hidden`, animations pause when off-screen and
respect *prefers-reduced-motion*, asset links carry a version query for cache-busting.

---

## 1. Run the website locally

You only need Python (any 3.x) — it is used as a simple local web server.

```bash
# from the project folder
cd wise-teck-v3

# Windows
py -m http.server 8020

# macOS / Linux
python3 -m http.server 8020
```

Open **http://127.0.0.1:8020/** in your browser. Stop the server with `Ctrl + C`.

> Opening `index.html` directly from disk also works, but a local server is recommended
> (the 3D coin and fonts load more reliably).

Useful URL switches:

| URL | What it does |
|---|---|
| `index.html?static` | Freezes all animation (for screenshots / testing) |
| `index.html?overlay` | Shows the original reference design over the home page (press **O** to toggle) |

---

## 2. Edit content and rebuild the pages

All page content lives in `tools/pages.py`; the shared layout (header, footer, menu, sections) is in
`tools/build.py`. After editing, regenerate the HTML:

```bash
# one-time: create the tools environment
py -m venv .venv                       # macOS/Linux: python3 -m venv .venv
.venv\Scripts\pip install pillow numpy opencv-python-headless
#                                      # macOS/Linux: .venv/bin/pip install ...

# rebuild all pages (run from the project folder)
.venv\Scripts\python tools\pages.py

# optional: rebuild the static fallback wave artwork
.venv\Scripts\python tools\draw_waves.py

# optional: check every item of the ecosystem PDF appears on the site
.venv\Scripts\python tools\check_content.py
```

Text that the client still has to supply is shown on the site as a dashed **[Placeholder]** box.

---

## 3. Project structure

```
wise-teck-v3/
├── index.html, about.html, ...       generated pages (home + 12 inner pages)
├── assets/
│   ├── css/wise-teck.css             THE stylesheet (design tokens + all styles)
│   ├── js/wt.js                      menu, scroll reveal, slider, reference overlay
│   ├── js/wt-waves.js                live animated wave art (hero, dividers, footer)
│   ├── js/hero-three.js              3D coin (Three.js) — from Wise-Teck v1
│   ├── js/vendor/three.min.js
│   ├── img/                          original Wise-Teck logos
│   └── wt-curves.svg                 static fallback wave art (used if JS is off)
└── tools/
    ├── build.py                      shared layout + reusable section blocks
    ├── pages.py                      content of every page  ->  run to rebuild
    ├── motifs.py                     section background motifs (globe, rings, quotes, skyline...)
    ├── draw_waves.py                 static fallback wave artwork
    └── check_content.py              PDF content coverage check
```

---

## 4. Design system (one set of values for the whole site)

Font: **Inter** (Google Fonts) — everywhere. All values are CSS variables at the top of
`assets/css/wise-teck.css`; change a token once and the whole site updates.

| Role | Token | Size | Weight | Line height |
|---|---|---|---|---|
| H1 — page titles | `--fs-h1` | 52px (fluid, min 36px) | 800 | 1.12 |
| H2 — section headings | `--fs-h2` | 36px (fluid, min 28px) | 800 | 1.2 |
| H3 — card titles | `--fs-h3` | 20px | 700 | 1.3 |
| H4 — footer headings | `--fs-h4` | 16px | 700 | 1.35 |
| H5 — minor headings | `--fs-h5` | 15px | 700 | 1.4 |
| Tag line / kicker | `--fs-kicker` | 13px, UPPERCASE, +0.1em | 700 | 1.2 |
| Lead paragraph | `--fs-lead` | 18px | 400 / 500 | 1.65 |
| Body paragraph | `--fs-body` | 16px | 400 | 1.7 |
| Small text (cards, lists) | `--fs-small` | 15px | 400 | 1.6 |
| Label (chips, captions) | `--fs-label` | 14px | 600 | 1.3 |
| Button | `--fs-button` | 15px | 700 | 1.2 |
| Navigation | `--fs-nav` | 15px | 600 | — |
| Fine print | `--fs-fine` | 13px | 500 | — |

Spacing follows an 8px grid (`--space-1` … `--space-9` = 4, 8, 12, 16, 24, 32, 48, 64, 88px);
paragraph gap `--p-gap` = 12px; radii `--r-sm` … `--r-pill`.

The stylesheet uses **CSS cascade layers**: `vendor` (Font Awesome) → `site` (layout & components)
→ `type` (typography). The `type` layer always wins, so text sizes are guaranteed uniform.

**Measured in the browser on all 13 pages (1440px wide):**

| Text | Size / weight | Where | Uniform? |
|---|---|---|---|
| H1 page title | 51px / 800 (home), 44px / 800 (all 12 inner pages) | Hero of every page | ✅ |
| H2 section heading | 35.6px / 800 | 55 headings, every section | ✅ |
| H3 card title | 20px / 700 | 108 card titles | ✅ |
| H4 footer heading | 16px / 700 | Footer | ✅ |
| Lead paragraph | 18px / 400–500 | Under hero titles and section intros | ✅ |
| Body paragraph | 16px / 400 | Long text blocks | ✅ |
| Card / list text | 15px / 400 | Cards, lists, step text | ✅ |
| Kicker / tag line | 13px / 700, uppercase | Above headings | ✅ |
| Buttons | 15px / 700 | All buttons | ✅ |
| Menu | 15px / 600 (dropdown 14px) | Top navigation | ✅ |
| Footer links | 14.5px / 400 | Footer | ✅ |
| Small UI labels | 12–14px | Chips, badges, orbit labels, logo captions | component-specific |
| Big numbers | 34–40px / 800–900 | Step numbers "01, 02…" | decorative |

Font: **Inter** everywhere; the only exception is the large decorative quotation marks (Georgia).

---

## 5. Site content — pages, source and status

**Source of all text:** the Wise-Teck ecosystem document (`eco system (5).pdf`). No content is invented —
anything the PDF does not cover is shown on the site as a dashed **[Placeholder]** box for Wise-Teck to supply.
Content lives in `tools/pages.py`; check coverage any time with `.venv\Scripts\python tools\check_content.py`.
A printable to-do list is in [`CONTENT-CHECKLIST.md`](CONTENT-CHECKLIST.md).

**13 pages = 1 home page + 12 inner pages.**

### Home page sections → inner pages

| Home section | Content shown (short version) | "Read more" opens |
|---|---|---|
| Hero | Tagline, intro line, Apply Now / Explore Programs, 3D coin | `contact.html` |
| About Wise-Teck | Introduction paragraph + photo | `about.html` |
| Our Ecosystem | 3 programs → Earning Centre diagram + summary | `earning-centre.html` |
| Programs Working Under WISE-TECK | 3 program cards | `wise-support-hub.html`, `wise-college.html`, `professional-paid-courses.html` |
| Our Professional Services | Service cards | `business-incubation.html`, `corporate-services.html`, `student-loan-scheme.html`, `placement.html` |
| Earning Blocks / weekend courses | Teaser | `earning-blocks.html`, `professional-paid-courses.html` |
| Success Stories | 2 learner stories | `success-stories.html` (menu) |
| Corporate & Industry Collaborations | PSDF, NIC, become a partner | `contact.html` |
| Call to action + footer | Contact details, links | `contact.html` |

### Where each part of the PDF appears

| PDF section | On the site | Status |
|---|---|---|
| Name, "Registered with Registrar Firms, Lahore", tagline | Home hero, About, footer, page titles | ✅ word for word |
| Introduction — Bridging Education, Industry & Self-Earning (3 paragraphs + "Turning Students into Self-Earning Individuals") | Home About (short), `about.html` (full) | ✅ word for word |
| Our Vision | `about.html` | ✅ word for word |
| Our Core Objectives (all 8) | `about.html` | ✅ word for word |
| Wise Eco System — Programs Working Under Wise-Teck | Home Ecosystem + Programs, `about.html`, `earning-centre.html` | ✅ — "four programs" changed to **three** (owner decision) |
| Wise Support Hub (funded, intermediate, BISE, full description) | Home card, `wise-support-hub.html` | ✅ word for word |
| Wise College (degree level, PU, full description) | Home card, `wise-college.html` | ✅ word for word |
| Wise Institute of Employability Skills (NAVTTC) | — | ❌ **removed on purpose** (owner decision; NAVTTC logo removed too) |
| Wise-Teck Earning Centre — about, pathway, outcome, What We Provide (6 points) | `earning-centre.html` (+ incubation / placement pages) | ✅ — program list shows the three remaining programs |
| Our Earning Blocks — all 6 blocks + How Earning Blocks Work | `earning-blocks.html` | ✅ word for word |
| Professional Paid Courses (objective 8) | Home card, `professional-paid-courses.html` | ✅ |
| Corporate Services, Business Incubation, Student Loan, Job Placement (objectives 3–6) | Their own inner pages | ✅ |

### Sentence-by-sentence map (every line of the document)

Checked automatically against all 13 pages. Format: *page → section heading*. "Hero" = the top banner of that page.

| # | Text from the document | Where it is on the site |
|---|---|---|
| 1 | Wise-Teck (Registered with Registrar firm, Lahore) | about.html → Hero (fact badge); contact.html → Hero — *written as "Registrar Firms"* |
| 2 | Tagline: Transforming Learning into Earning through Technology, Innovation and Entrepre… | Home → Hero (intro line); about.html → quote card; business-incubation.html; page &lt;meta&gt; description |
| 3 | Bridging Education, Industry & Self-Earning | about.html → Hero |
| 4 | Wise-Teck, a project of Wise Education Society, is a professional skills development, b… | about.html → A Skills, Incubation & Earning Platform; business-incubation.html → Supporting Emerging Entrepreneurs |
| 5 | Operating through an integrated education-to-earning ecosystem, Wise-Teck connects stud… | about.html → A Skills, Incubation & Earning Platform |
| 6 | Its core focus is to develop a skilled workforce, support emerging entrepreneurs, and e… | about.html → A Skills, Incubation & Earning Platform; business-incubation.html → Supporting Emerging Entrepreneurs |
| 7 | Turning Students into Self-Earning Individuals. | about.html → A Skills, Incubation & Earning Platform; business-incubation.html → Supporting Emerging Entrepreneurs |
| 8 | To create a future where education goes beyond degrees, equipping every student with pr… | about.html → Education That Goes Beyond Degrees |
| 9 | Skills Training: Provide students with professional and technical skills needed in toda… | about.html → Eight Objectives, One Goal |
| 10 | Self-Earning: Help students use their skills to earn money through real projects, freel… | about.html → Eight Objectives, One Goal |
| 11 | Student Loan Support: Help eligible students get loans to start their own businesses. | about.html → Eight Objectives, One Goal |
| 12 | Job Placement: Help students and graduates find jobs, internships, and earning opportun… | about.html → Eight Objectives, One Goal |
| 13 | Corporate Services: Provide IT, software development, digital marketing, and other tech… | about.html → Eight Objectives, One Goal |
| 14 | Business Incubation Centre: Help students turn their business ideas into real businesse… | about.html → Eight Objectives, One Goal |
| 15 | Industry Partnerships: Build connections with companies, software houses, and industry … | about.html → Eight Objectives, One Goal |
| 16 | Professional Paid Courses: Offer paid courses to help students, graduates, and working … | about.html → Eight Objectives, One Goal |
| 17 | Programs Working Under Wise-Teck | Home → Programs Working Under WISE-TECK; about.html → Programs Working Under Wise-Teck; earning-centre.html → Programs Working Under Wise-Teck |
| 18 | Wise-Teck brings together four educational and training programs. | about.html → Programs Working Under Wise-Teck — *edited: four→three / Firms* |
| 19 | Each program provides different education and training opportunities, while Wise-Teck h… | about.html → Programs Working Under Wise-Teck |
| 20 | Students from all four programs come to Wise-Teck to learn professional skills. | Home → From Education to Self-Earning; wise-support-hub.html → Explore All Three WISE Programs; wise-college.html → Explore All Three WISE Programs; professional-paid-courses.html → Explore All Three WISE Programs (+2 more) — *edited: four→three / Firms* |
| 21 | After completing their skills training, they move to the Wise-Teck Earning Centre, wher… | Home → From Education to Self-Earning |
| 22 | Fully Funded Educational & Skills Training Program | Home → Programs Working Under WISE-TECK; about.html → Programs Working Under Wise-Teck; wise-support-hub.html → Hero; wise-support-hub.html → A Better, Financially Independent Future (+5 more) |
| 23 | Intermediate Level | Home → From Education to Self-Earning; Home → Programs Working Under WISE-TECK; about.html → Programs Working Under Wise-Teck; wise-support-hub.html → Hero (+6 more) |
| 24 | Affiliated with Board of Intermediate and Secondary Education (BISE) | wise-support-hub.html → A Better, Financially Independent Future; also "Affiliated with BISE" badge in its Hero |
| 25 | Wise Support Hub provides fully funded intermediate (ICS) education for orphaned and un… | wise-support-hub.html → A Better, Financially Independent Future |
| 26 | Higher Education with Professional Skills | Home → Programs Working Under WISE-TECK; about.html → Programs Working Under Wise-Teck; wise-support-hub.html → Explore All Three WISE Programs; wise-college.html → Hero (+5 more) |
| 27 | Degree Level Program | about.html → Programs Working Under Wise-Teck; wise-support-hub.html → Explore All Three WISE Programs; wise-college.html → Hero; wise-college.html → Degrees That Lead to Earning (+4 more) |
| 28 | Affiliated with University of the Punjab (PU) | wise-college.html → Hero; wise-college.html → Degrees That Lead to Earning |
| 29 | Wise College offers ADP and BS degree programs in Artificial Intelligence, E-Commerce, … | wise-college.html → Degrees That Lead to Earning |
| 30 | Wise Institute of Employability Skills (NAVTTC) | ❌ Removed on purpose (NAVTTC program dropped) |
| 31 | Govt Fully Funded Project | ❌ Removed on purpose (NAVTTC program dropped) |
| 32 | Hi-Tech / Hi-End / Conventional Skills Training | ❌ Removed on purpose (NAVTTC program dropped) |
| 33 | Registered & Accredited with National Vocational and Technical Training Commission (NAV… | ❌ Removed on purpose (NAVTTC program dropped) |
| 34 | Wise Institute of Employability Skills provides professional and technical skills train… | ❌ Removed on purpose (NAVTTC program dropped) |
| 35 | After completing their training, students join the Wise-Teck Earning Centre, where they… | ❌ Removed on purpose (NAVTTC program dropped) |
| 36 | From Professional Skills to Self-Earning | earning-centre.html → Hero |
| 37 | Wise-Teck Earning Centre is the final stage of Wise Education Society's education-to-ea… | earning-centre.html → Where Skills Start Earning |
| 38 | Students from all four WISE programs — Wise Support Hub, Wise College Degree Programs, … | earning-centre.html → Where Skills Start Earning; business-incubation.html → Open to Students from All Three WISE Programs — *edited: four→three / Firms* |
| 39 | After developing their skills, students move to the Wise-Teck Earning Centre, where the… | earning-centre.html → Where Skills Start Earning |
| 40 | The Earning Centre helps students build their careers through freelancing, employment, … | earning-centre.html → Where Skills Start Earning; placement.html → Three Ways to Earn |
| 41 | WISE Educational & Training Programs → Wise-Teck Skills Training → Wise-Teck Earning Ce… | about.html → From Education to Self-Earning; wise-support-hub.html → From Education to Self-Earning; wise-college.html → From Education to Self-Earning; professional-paid-courses.html → From Education to Self-Earning |
| 42 | To help students turn their education and professional skills into real earning opportu… | earning-centre.html → Where Skills Start Earning; business-incubation.html → Become Financially Independent |
| 43 | Practical experience through real-world projects | earning-centre.html → Support at Every Step; business-incubation.html → From Idea to Your Own Business |
| 44 | Guidance from experienced professionals | earning-centre.html → Support at Every Step; business-incubation.html → From Idea to Your Own Business; placement.html → From Skills to Careers |
| 45 | Freelancing and client work opportunities | earning-centre.html → Support at Every Step; business-incubation.html → From Idea to Your Own Business; placement.html → From Skills to Careers |
| 46 | Job and career support | earning-centre.html → Support at Every Step; placement.html → Hero; placement.html → From Skills to Careers |
| 47 | Business startup guidance and mentorship | earning-centre.html → Support at Every Step; business-incubation.html → From Idea to Your Own Business |
| 48 | Industry connections and professional networking | earning-centre.html → Support at Every Step; placement.html → From Skills to Careers |
| 49 | Different Skills. Different Opportunities. One Goal: Self-Earning. | earning-centre.html → Different Skills. Different Opportunities.; earning-blocks.html → Hero |
| 50 | Wise-Teck Earning Centre has different earning blocks where students use their skills t… | earning-blocks.html → Hero |
| 51 | Students develop websites, software, and online solutions for businesses and clients. | earning-blocks.html → Choose Your Earning Block |
| 52 | Students learn online selling, product management, and order handling through Dehleze, … | earning-blocks.html → Choose Your Earning Block |
| 53 | Students work on graphic design, video editing, social media management, content creati… | earning-blocks.html → Choose Your Earning Block |
| 54 | Students learn how to find online clients, create freelance profiles, write proposals, … | earning-blocks.html → Choose Your Earning Block |
| 55 | Students use AI, Power BI, data analysis, and other digital tools to work on business p… | earning-blocks.html → Choose Your Earning Block |
| 56 | Students receive guidance to develop business ideas, start small businesses, and create… | earning-blocks.html → Choose Your Earning Block |
| 57 | Skills Development → Earning Block Selection → Practical Projects → Client Work → Self-… | earning-blocks.html → From Skills to Self-Earning |
| 58 | Students join an earning block according to their skills and interests. | earning-blocks.html → Choose Your Earning Block; earning-blocks.html → From Skills to Self-Earning; business-incubation.html → Your Path to Self-Earning |

**Result:** 52 of 58 lines are on the site word for word (3 with the agreed edits); the 6 NAVTTC lines are removed on purpose. Nothing from the document is missing.

Only intentional edits to the PDF text: "four" → "three" programs, NAVTTC program removed,
"Registrar firm" written as "Registrar Firms".

### Content still missing (not in the PDF — to be supplied by Wise-Teck)

| Page | Needed |
|---|---|
| Professional Paid Courses | Course list, duration, fees, weekend timings, start dates |
| Corporate Services | Service packages, process, industries served, past clients |
| Student Loan Scheme | Eligibility, loan amounts, partner institutions, documents, how to apply |
| Placement | Hiring partners, placement process, results |
| Success Stories | More stories (name, program, earning result, photo) |
| Contact | Form connected to email; Google Map (optional) |
| Whole site | Real photos (current images are samples), social media links, "Watch Overview" video, partner logo approval |

### Image & video sizes (for whoever supplies the media)

The site is designed for a desktop window **1440px wide**; content sits in a centred column of about 1150px;
the home hero is 700px tall. Current photos are temporary samples at only **512 × 279px** — too small, they look soft
in the larger frames. Supply the sizes below (about 2× the on-screen size so photos stay sharp on high-resolution screens).
Photos are cropped automatically to fit each frame — keep the main subject in the centre.
Format: **JPG or WebP**, ideally under 400KB each.

**Hero areas**

| Where | Shows now | Size on screen | Shape | Supply at |
|---|---|---|---|---|
| Home hero (right side) | 3D spinning coin + orbit | ~520 × 520px | square | nothing needed (uses the logo) |
| Inner page feature band (below the centred banner) | Page photo in a white rounded frame | **980 × 366px** (frame 992 × 378) | **21 : 8** wide strip | **2000 × 760px** |
| Inner pages with an orbit (Earning Blocks, Corporate, Incubation, Success Stories) | 3D coin + icons | ~470 × 470px | square | nothing needed |
| Logo (menu & footer) | Spinning logo | 44 × 44px | square | already fine (150 × 150) |

**Other images**

| Section | Size on screen | Shape | Supply at |
|---|---|---|---|
| Home — About Wise-Teck photo (slanted frame) | 599 × 390px | ~3 : 2 | 1200 × 800px |
| Home — Program cards (3) | 350 × 219px | 16 : 10 | 800 × 500px |
| Earning Blocks page — block cards (6) | 367 × 229px | 16 : 10 | 800 × 500px |
| Home — Services thumbnails (6) | 179 × 138px | ~4 : 3 | 400 × 300px |
| Home — Weekend courses image | 306 × 210px | ~3 : 2 | 640 × 440px |
| Success story photos | 110 × 110px (round) | 1 : 1 | 300 × 300px |
| Home — Collaborations image | 559 × 233px | ~12 : 5 | 1200 × 500px |

**Video (not on the site yet)** — the hero's "Watch Overview" button currently scrolls to About.
To add one: **MP4 (H.264), 1920 × 1080, 16 : 9**, about 1–2 minutes, under 15MB (or a YouTube link).
It would open in a pop-up player of about **960 × 540px**; also supply a 1920 × 1080 JPG cover image.

**Where image files go:** put them in `assets/img/`, then point the page to them in `tools/pages.py` and rebuild.

### How to add missing content

1. Open `tools/pages.py`, find the page (e.g. `"courses"`) and replace the `placeholder(...)` block with the real text.
2. Rebuild: `.venv\Scripts\python tools\pages.py`
3. Check in the browser, then commit and push (section 6).

---

## 6. Git & GitHub workflow

Repository: **https://github.com/Engineer00/wise_teck_v3**

### Install the tools (Windows)

```bash
winget install --id Git.Git -e          # Git
winget install --id GitHub.cli -e       # GitHub CLI (gh)
gh auth login                           # sign in to GitHub once (choose HTTPS + browser)
```

### First-time setup (already done for this project)

```bash
git init -b main
git add -A
git commit -m "Initial Wise-Teck v3 website"
git remote add origin https://github.com/Engineer00/wise_teck_v3.git
git push -u origin main
```

### Clone on another computer

```bash
git clone https://github.com/Engineer00/wise_teck_v3.git
cd wise_teck_v3
```

### Every new feature: branch -> pull main -> work -> push -> pull request

```bash
git checkout main
git pull origin main                    # get the latest main
git checkout -b feature/<short-name>    # e.g. feature/inner-page-headers
git pull origin main                    # make sure the branch starts from the newest main

# ... edit files, rebuild pages (section 2), check in the browser ...

git add -A
git commit -m "Describe the change"
git push -u origin feature/<short-name>

gh pr create --base main --fill         # open a pull request on GitHub
```

### Keep a feature branch up to date while working

```bash
git checkout feature/<short-name>
git pull origin main                    # merge the latest main into your branch
```

### After the pull request is merged

```bash
git checkout main
git pull origin main
git branch -d feature/<short-name>
```

### How to use a feature branch (example: `feature/inner-page-headers`)

A feature branch holds one piece of work, separate from `main`, until it is reviewed and merged.

```bash
# 1. get the branch from GitHub and switch to it
git fetch origin
git checkout feature/inner-page-headers        # first time: creates a local copy tracking origin

# 2. bring it up to date with main before working on / reviewing it
git pull origin main

# 3. view the site from this branch
py -m http.server 8020                          # open http://127.0.0.1:8020/

# 4. see what the branch changes compared with main
git log --oneline main..feature/inner-page-headers
git diff --stat main..feature/inner-page-headers

# 5. keep working on it (commit + push as often as you like)
git add -A
git commit -m "Describe the change"
git push origin feature/inner-page-headers

# 6. switch back to main at any time (your branch work stays saved on the branch)
git checkout main
```

**Merge the branch into main** — recommended: through a pull request on GitHub

```bash
gh pr create --base main --head feature/inner-page-headers --title "Compact inner page headers" --fill
gh pr view --web                                # review it in the browser, then click "Merge"
```

or merge locally

```bash
git checkout main
git pull origin main
git merge feature/inner-page-headers
git push origin main
```

**Delete the branch after merging**

```bash
git branch -d feature/inner-page-headers                 # local
git push origin --delete feature/inner-page-headers      # on GitHub
```

### One-click setup script (Windows)

`setup-wise-teck.ps1` does everything below automatically: installs Git/Python if missing, asks for your
commit name/email once, clones or updates the project, switches to the feature branch, pulls the latest
code and starts the site. Safe to run again any time to get the newest version.

```powershell
# download the script (first time only), then run it
Invoke-WebRequest https://raw.githubusercontent.com/Engineer00/wise_teck_v3/feature/inner-page-headers/setup-wise-teck.ps1 -OutFile setup-wise-teck.ps1
powershell -ExecutionPolicy Bypass -File .\setup-wise-teck.ps1

# options
powershell -ExecutionPolicy Bypass -File .\setup-wise-teck.ps1 -Path D:\Projects    # clone somewhere else (default D:\)
powershell -ExecutionPolicy Bypass -File .\setup-wise-teck.ps1 -Branch main         # use another branch
powershell -ExecutionPolicy Bypass -File .\setup-wise-teck.ps1 -SetupTools          # also prepare page rebuilding
powershell -ExecutionPolicy Bypass -File .\setup-wise-teck.ps1 -NoServe             # update only, don't start the site
```

After the first run the script is also inside the project folder (`D:\wise_teck_v3\setup-wise-teck.ps1`).

### Pull the feature branch to your computer

```bash
# A) you do NOT have the project yet — clone straight onto the feature branch
git clone -b feature/inner-page-headers https://github.com/Engineer00/wise_teck_v3.git
cd wise_teck_v3

# B) you already have the project — download and switch to the feature branch
cd wise_teck_v3
git fetch origin                                   # get the newest branches from GitHub
git checkout feature/inner-page-headers            # switch (first time creates the local branch)
git pull origin feature/inner-page-headers         # get the newest commits of this branch
```

Check which branch you are on (the one with `*`):

```bash
git branch            # local branches
git status            # first line shows the current branch
```

### Switch between main and the feature branch

```bash
git checkout feature/inner-page-headers      # work on the feature
git checkout main                            # back to main
```

Commit or stash your changes before switching (`git stash`, later `git stash pop`).
The local server (`py -m http.server 8020`) always shows the branch that is checked out — just refresh the browser.

### Push your work — to the feature branch or to main?

**Normal rule: push to the feature branch, then merge into main.** Never work directly on main.

```bash
# push to the FEATURE branch (day-to-day work)
git checkout feature/inner-page-headers
git add -A
git commit -m "Describe the change"
git push origin feature/inner-page-headers
```

```bash
# put the feature into MAIN (when the work is finished and checked)
git checkout main
git pull origin main
git merge feature/inner-page-headers
git push origin main
# (or open a pull request: gh pr create --base main --head feature/inner-page-headers --fill)
```

### Make main the same as the feature branch

Merging (above) is the safe way: main gets every commit of the feature branch and keeps its history.
After `git push origin main` both branches contain the same code; check with:

```bash
git diff main origin/feature/inner-page-headers     # no output = identical
```

### Commit author

Commits are authored as **Engineer00 &lt;salman.k.786000@gmail.com&gt;** (set once per clone):

```bash
git config user.name "Engineer00"
git config user.email "salman.k.786000@gmail.com"
```

### Handy commands

```bash
git status                              # what changed
git log --oneline -10                   # recent commits
git branch -a                           # all branches
git diff                                # unstaged changes
```
