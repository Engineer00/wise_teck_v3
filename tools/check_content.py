"""Check that every item of the ecosystem PDF appears on the site (home and/or inner pages).

    python tools/check_content.py
Prints, for each PDF item, the pages where its key phrase is found (or MISSING).
NAVTTC / Employability Skills items are reported separately (removed on the owner's instruction).
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ITEMS = [
    ("Header", "Registered with Registrar", "Registered with Registrar"),
    ("Header", "Tagline", "Transforming Learning into Earning through Technology, Innovation and Entrepreneurship"),
    ("Introduction", "Heading", "Bridging Education, Industry & Self-Earning"),
    ("Introduction", "Paragraph 1", "professional skills development, business incubation, and earning platform dedicated to transforming knowledge"),
    ("Introduction", "Paragraph 2", "Operating through an integrated education-to-earning ecosystem"),
    ("Introduction", "Paragraph 3", "Its core focus is to develop a skilled workforce"),
    ("Introduction", "Line", "Turning Students into Self-Earning Individuals"),
    ("Vision", "Vision", "education goes beyond degrees"),
    ("Objectives", "1 Skills Training", "professional and technical skills needed in today's job market"),
    ("Objectives", "2 Self-Earning", "earn money through real projects, freelancing, jobs, and businesses"),
    ("Objectives", "3 Student Loan Support", "Help eligible students get loans to start their own businesses"),
    ("Objectives", "4 Job Placement", "find jobs, internships, and earning opportunities"),
    ("Objectives", "5 Corporate Services", "IT, software development, digital marketing, and other technology services"),
    ("Objectives", "6 Business Incubation Centre", "turn their business ideas into real businesses through guidance and support"),
    ("Objectives", "7 Industry Partnerships", "companies, software houses, and industry experts"),
    ("Objectives", "8 Professional Paid Courses", "learn new skills, improve their jobs, and grow their careers"),
    ("Wise Eco System", "Heading", "Programs Working Under"),
    ("Wise Eco System", "Intro (now three programs)", "educational and training programs"),
    ("Wise Eco System", "Flow to Earning Centre", "come to Wise-Teck to learn professional skills"),
    ("Wise Support Hub", "Type", "Fully Funded Educational & Skills Training Program"),
    ("Wise Support Hub", "Level", "Intermediate Level"),
    ("Wise Support Hub", "Affiliation", "Board of Intermediate and Secondary Education"),
    ("Wise Support Hub", "Description", "orphaned and underprivileged girls"),
    ("Wise Support Hub", "Free lunch / transport", "free daily lunch, free transport"),
    ("Wise College", "Type", "Higher Education with Professional Skills"),
    ("Wise College", "Level", "Degree Level Program"),
    ("Wise College", "Affiliation", "University of the Punjab"),
    ("Wise College", "Programs", "Artificial Intelligence, E-Commerce, Software Engineering, and Data Science"),
    ("Wise College", "Faculty / classrooms", "MPhil/PhD faculty"),
    ("Earning Centre", "Heading", "From Professional Skills to Self-Earning"),
    ("Earning Centre", "About 1", "final stage of Wise Education Society"),
    ("Earning Centre", "About 2", "during or after their studies"),
    ("Earning Centre", "About 3", "gain practical experience, and receive guidance to start earning"),
    ("Earning Centre", "About 4", "freelancing, employment, and starting their own businesses"),
    ("Earning Centre", "Pathway", "Wise-Teck Skills Training"),
    ("Earning Centre", "Outcome", "become financially independent"),
    ("Earning Centre", "Provide 1", "Practical experience through real-world projects"),
    ("Earning Centre", "Provide 2", "Guidance from experienced professionals"),
    ("Earning Centre", "Provide 3", "Freelancing and client work opportunities"),
    ("Earning Centre", "Provide 4", "Job and career support"),
    ("Earning Centre", "Provide 5", "Business startup guidance and mentorship"),
    ("Earning Centre", "Provide 6", "Industry connections and professional networking"),
    ("Earning Blocks", "Heading", "Different Skills. Different Opportunities."),
    ("Earning Blocks", "Intro", "has different earning blocks where students use their skills"),
    ("Earning Blocks", "i Software & Web", "websites, software, and online solutions"),
    ("Earning Blocks", "ii E-Commerce & Dehleze", "multi-vendor e-commerce platform"),
    ("Earning Blocks", "iii Digital Marketing & Creative", "graphic design, video editing, social media management"),
    ("Earning Blocks", "iv Freelancing & Remote", "create freelance profiles, write proposals"),
    ("Earning Blocks", "v AI, Data & Business", "AI, Power BI, data analysis"),
    ("Earning Blocks", "vi Entrepreneurship & Incubation", "start small businesses, and create their own"),
    ("Earning Blocks", "How they work", "Earning Block Selection"),
    ("Earning Blocks", "Closing line", "according to their skills and interests"),
]
REMOVED = [("Wise Institute of Employability Skills (NAVTTC)", "Employability")]


def text_of(f):
    s = f.read_text(encoding="utf-8")
    s = re.sub(r"<(script|style|svg)[\s\S]*?</\1>", " ", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).replace("’", "'").replace("‘", "'")


pages = {f.name: text_of(f) for f in sorted(ROOT.glob("*.html")) if not f.name.startswith("_")}
order = ["index.html"] + sorted(k for k in pages if k != "index.html")
missing = 0
cur = None
for sec, name, phrase in ITEMS:
    if sec != cur:
        print(f"\n== {sec}"); cur = sec
    where = [k for k in order if phrase.lower() in pages[k].lower()]
    if not where:
        missing += 1
    tag = "MISSING" if not where else ", ".join(("HOME" if k == "index.html" else k.replace(".html", "")) for k in where)
    print(f"  {'!!' if not where else 'ok'}  {name:34s} {tag}")
print("\n== Removed on owner's instruction")
for name, phrase in REMOVED:
    where = [k for k in order if phrase.lower() in pages[k].lower()]
    print(f"  {'ok' if not where else '!!'}  {name:34s} {'not on site (as requested)' if not where else 'STILL ON: ' + ', '.join(where)}")
print(f"\nPDF items checked: {len(ITEMS)}   missing: {missing}")
