# Wise-Teck Website (v3)

Static website for **Wise-Teck**, a project of Wise Education Society —
*Transforming Learning into Earning through Technology, Innovation and Entrepreneurship.*

Plain **HTML + CSS + vanilla JavaScript** (no build step needed to view it). A small Python
generator (`tools/`) builds every page from one shared layout so the whole site stays consistent.

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

---

## 5. Git & GitHub workflow

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
