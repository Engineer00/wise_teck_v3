<#
.SYNOPSIS
  Gets the Wise-Teck v3 website from GitHub and runs it locally (Windows).

.DESCRIPTION
  Safe to run again at any time. It will:
    1. install Git and Python with winget if they are missing
    2. ask for your Git name / email once (used for your commits)
    3. clone the repository, or update it if it is already there
    4. switch to the branch you choose (default: feature/inner-page-headers) and pull the latest code
    5. optionally create the Python tools environment (-SetupTools) for rebuilding pages
    6. start the local web server and open the site in your browser (skip with -NoServe)

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\setup-wise-teck.ps1
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\setup-wise-teck.ps1 -Path D:\Projects -Branch main -SetupTools
#>
param(
    [string]$Path   = "D:\",                                   # folder the project is cloned into
    [string]$Branch = "feature/inner-page-headers",            # branch to work on
    [string]$Repo   = "https://github.com/Engineer00/wise_teck_v3.git",
    [int]   $Port   = 8020,
    [switch]$SetupTools,                                       # also create .venv for tools\pages.py
    [switch]$NoServe                                           # do not start the local server
)

$ErrorActionPreference = "Stop"

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "    $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "    $msg" -ForegroundColor Red; exit 1 }

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}

function Ensure-Tool($cmd, $wingetId, $label) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { Ok "$label found"; return }
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Fail "$label is missing and winget is not available. Install $label manually, then run this script again."
    }
    Write-Host "    Installing $label ..."
    winget install --id $wingetId -e --accept-source-agreements --accept-package-agreements
    Refresh-Path
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Fail "$label was installed but is not on PATH yet. Close this window, open a new one and run the script again."
    }
    Ok "$label installed"
}

function Git-Run {
    git @args
    if ($LASTEXITCODE -ne 0) { Fail "git $($args -join ' ') failed (see message above)." }
}

# ---------------------------------------------------------------- 1. tools
Step "Checking Git and Python"
Ensure-Tool "git" "Git.Git" "Git"
Ensure-Tool "py"  "Python.Python.3.12" "Python"

# ---------------------------------------------------------------- 2. git identity
Step "Checking your Git name and email"
$name  = git config --global user.name
$email = git config --global user.email
if (-not $name)  { $name  = Read-Host "    Your name for commits";  if ($name)  { git config --global user.name  "$name" } }
if (-not $email) { $email = Read-Host "    Your email for commits"; if ($email) { git config --global user.email "$email" } }
if ($name -and $email) { Ok "Commits will be authored as $name <$email>" }
else { Write-Host "    Name/email not set - you can still view the site; set them before committing (see README)." -ForegroundColor Yellow }

# ---------------------------------------------------------------- 3. clone or update
$repoName = [IO.Path]::GetFileNameWithoutExtension($Repo)
$project  = Join-Path $Path $repoName

Step "Getting the project into $project"
if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Path $Path | Out-Null }

if (Test-Path (Join-Path $project ".git")) {
    Ok "Project already exists - updating it"
    Set-Location $project
    Git-Run fetch origin
} else {
    Git-Run clone $Repo $project
    Set-Location $project
}

# ---------------------------------------------------------------- 4. branch + pull
Step "Switching to branch '$Branch' and pulling the latest code"
if (git status --porcelain) {
    Fail "You have unsaved changes in $project. Commit them (git add -A; git commit -m '...') or run 'git stash', then run this script again."
}
Git-Run checkout $Branch
Git-Run pull origin $Branch
if ($Branch -ne "main") { Git-Run pull origin main }      # keep the feature branch up to date with main
Ok "On branch $(git branch --show-current) - latest commit: $(git log -1 --format='%h %s')"

# ---------------------------------------------------------------- 5. optional tools env
if ($SetupTools) {
    Step "Creating the Python tools environment (.venv)"
    if (-not (Test-Path ".venv")) { py -m venv .venv }
    & .\.venv\Scripts\python -m pip install --quiet --upgrade pip
    & .\.venv\Scripts\pip install --quiet pillow numpy opencv-python-headless
    Ok "Ready. Rebuild pages with:  .venv\Scripts\python tools\pages.py"
}

# ---------------------------------------------------------------- 6. run the site
if ($NoServe) {
    Step "Done. To view the site later run:  cd $project ; py -m http.server $Port"
    exit 0
}
Step "Starting the website at http://127.0.0.1:$Port/  (press Ctrl + C to stop)"
Start-Process "http://127.0.0.1:$Port/"
py -m http.server $Port --bind 127.0.0.1
