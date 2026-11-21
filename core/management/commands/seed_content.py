"""Load the Wise-Teck v3 content into the database (pages, sections, cards, menu, footer, settings,
programs, success stories) plus the original site's blog / team / services.

    py manage.py seed_content              # first time (refuses if pages already exist)
    py manage.py seed_content --reset      # wipe website content and load it again (admin edits are lost!)
    py manage.py seed_content --no-download   # keep photo links instead of downloading them into media/

Wording is the v3 static site's (tools/pages.py in wise-teck-v3), word for word. Photos are the ones
the v3 site uses; they are downloaded into media/seed/v3/ so the site does not depend on outside links.
"""

import hashlib
import json
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from core.models import (
    BlogPost,
    FooterColumn,
    FooterLink,
    Item,
    NavItem,
    Page,
    Program,
    Redirect,
    Section,
    Service,
    SiteSettings,
    SuccessStory,
    TeamMember,
)

SEED = Path(__file__).resolve().parents[2] / "seed"
IMG = json.loads((SEED / "stitch_images.json").read_text(encoding="utf-8"))


def img(page, i):
    lst = IMG.get(page) or []
    return lst[i] if i < len(lst) else ""


P = {
    "home": "/",
    "about": "/about/",
    "hub": "/wise-support-hub/",
    "college": "/wise-college/",
    "courses": "/professional-paid-courses/",
    "centre": "/earning-centre/",
    "blocks": "/earning-blocks/",
    "corporate": "/corporate-services/",
    "incubation": "/business-incubation/",
    "loan": "/student-loan-scheme/",
    "placement": "/placement/",
    "stories": "/success-stories/",
    "contact": "/contact/",
    "blog": "/blog/",
}
HOME = ("Home", P["home"])

# --------------------------------------------------------------------------------------- shared lists
PATHWAY = [
    ("fa-school", "WISE Educational & Training Programs"),
    ("fa-graduation-cap", "Wise-Teck Skills Training"),
    ("fa-building", "Wise-Teck Earning Centre"),
    ("fa-chart-line", "Self-Earning"),
]
BLOCK_STEPS = [
    ("fa-graduation-cap", "Skills Development"),
    ("fa-hand-pointer", "Earning Block Selection"),
    ("fa-laptop-code", "Practical Projects"),
    ("fa-briefcase", "Client Work"),
    ("fa-chart-line", "Self-Earning"),
]
HERO_STATS = {
    "about": [
        ("fa-diagram-project", "3", "Programs"),
        ("fa-bullseye", "8", "Core Objectives"),
        ("fa-cubes", "6", "Earning Blocks"),
    ],
    "hub": [
        ("fa-book-open", "Free", "Education"),
        ("fa-utensils", "Free", "Daily Lunch"),
        ("fa-bus", "Free", "Transport"),
    ],
    "college": [
        ("fa-graduation-cap", "ADP & BS", "Degree Programs"),
        ("fa-microchip", "4", "Specialisations"),
        ("fa-user-graduate", "MPhil/PhD", "Faculty"),
    ],
    "courses": [
        ("fa-calendar-week", "Weekend", "Classes"),
        ("fa-user-graduate", "Students", "& Graduates"),
        ("fa-briefcase", "Working", "Professionals"),
    ],
    "centre": [
        ("fa-diagram-project", "3", "Programs Feed In"),
        ("fa-cubes", "6", "Earning Blocks"),
        ("fa-hands-holding-circle", "6", "Support Services"),
    ],
    "loan": [
        ("fa-user-check", "Eligible", "Students"),
        ("fa-store", "Start", "Your Own Business"),
        ("fa-route", "Step 4", "of the Earning Journey"),
    ],
    "placement": [
        ("fa-briefcase", "Jobs", "& Careers"),
        ("fa-user-tie", "Internships", "for Students"),
        ("fa-coins", "Earning", "Opportunities"),
    ],
    "contact": [
        ("fa-phone", "+92 300 8410868", "Call Us"),
        ("fa-envelope", "info@wise-teck.org", "Email"),
        ("fa-location-dot", "48-Main Gulberg", "Lahore"),
    ],
}
STATS_STYLE = {"college": "text", "placement": "text", "contact": "text"}
SECOND_PHOTO = {
    "about": ("13", 1),
    "hub": ("03", 1),
    "college": ("04", 2),
    "courses": ("06", 2),
    "centre": ("13", 3),
    "loan": ("10", 1),
    "placement": ("08", 2),
    "contact": ("13", 5),
}
PROG_SUB = "Students from all three programs come to Wise-Teck to learn professional skills, then move to the Wise-Teck Earning Centre."
EARN_NOTE = "After completing their skills training, students move to the **Wise-Teck Earning Centre**, where they work on practical projects and explore earning opportunities."


def second_photo(key, first):
    pool = [SECOND_PHOTO.get(key)] + [("01", i) for i in range(15)] + [("13", i) for i in range(13)]
    for ref in pool:
        if ref and img(*ref) and img(*ref) != first:
            return img(*ref)
    return ""


# --------------------------------------------------------------------------------------- section builders
def it(icon="", title="", text="", link=None, **kw):
    d = {"icon": icon, "title": title, "text": text, **kw}
    if link:
        d["link_label"], d["link_url"] = link
    return d


def crumbs(*pairs):
    return "\n".join(f"{t} | {u}" if u else t for t, u in pairs)


def hero(key, crumb_pairs, eyebrow, title, hl, lead, b1, b2=None, *, photo=None, badge=None, facts=None, tags=None):
    s = {
        "layout": "page_hero",
        "crumbs": crumbs(*crumb_pairs),
        "eyebrow": eyebrow,
        "title": title,
        "highlight": hl,
        "subtitle": lead,
        "items": [],
    }
    s.update(button_label=b1[0], button_url=b1[1], button_style="navy")
    if len(b1) > 2:
        s["button_icon"] = b1[2]
    if b2:
        s.update(button2_label=b2[0], button2_url=b2[1], button2_style="ghost", button2_icon=b2[2])
    for icon, text in facts or []:
        s["items"].append({"group": "facts", "icon": icon, "title": text})
    if photo:
        src, alt = photo
        s.update(visual="photo", image_url=src, image_alt=alt)
        if badge:
            s.update(badge_icon=badge[0], badge_text=badge[1])
        if key in HERO_STATS:
            s["image2_url"] = second_photo(key, src)
            s["stats_style"] = STATS_STYLE.get(key, "")
            for icon, value, label in HERO_STATS[key]:
                s["items"].append({"group": "stats", "icon": icon, "title": value, "subtitle": label})
    if tags:
        s["visual"] = "orbit"
        for icon, t in tags:
            s["items"].append({"group": "tags", "icon": icon, "title": t})
    return s


def split(eyebrow, title, hl, body, *, visual, div="", spacing="", anchor="", button=None, side="right", **kw):
    s = {
        "layout": "split",
        "eyebrow": eyebrow,
        "title": title,
        "highlight": hl,
        "body": "\n\n".join(body),
        "visual": visual,
        "divider_after": div,
        "spacing": spacing,
        "anchor": anchor,
        "image_side": side,
        **kw,
    }
    if button:
        s.update(button_label=button[0], button_url=button[1], button_style="purple")
    return s


def cards(eyebrow, title, hl, items, *, cols=3, numbered=False, sub="", div="", spacing="", anchor=""):
    return {
        "layout": "cards",
        "eyebrow": eyebrow,
        "title": title,
        "highlight": hl,
        "subtitle": sub,
        "columns": cols,
        "numbered": numbered,
        "divider_after": div,
        "spacing": spacing,
        "anchor": anchor,
        "items": [it(*x[:3], link=x[3] if len(x) > 3 else None) for x in items],
    }


def steps(eyebrow, title, hl, items, *, sub="", note="", div="", anchor=""):
    return {
        "layout": "steps",
        "eyebrow": eyebrow,
        "title": title,
        "highlight": hl,
        "subtitle": sub,
        "note": note,
        "item_label": "Step",
        "divider_after": div,
        "anchor": anchor,
        "items": [it(i, t) for i, t in items],
    }


def pathway(note=""):
    return steps(
        "Our Earning Pathway",
        "From Education to Self-Earning",
        "Self-Earning",
        PATHWAY,
        sub="WISE Educational & Training Programs → Wise-Teck Skills Training → Wise-Teck Earning Centre → Self-Earning",
        note=note,
    )


def strip(title="Programs Working Under Wise-Teck", *, div="b", eyebrow="", hl="", sub=PROG_SUB, lined=True, anchor=""):
    return {
        "layout": "program_strip",
        "eyebrow": eyebrow,
        "title": title,
        "highlight": hl,
        "subtitle": sub,
        "lined": lined,
        "item_label": "Read More",
        "divider_after": div,
        "anchor": anchor,
    }


def placeholder(title, text):
    return {
        "layout": "placeholder",
        "title": f"[Placeholder] {title}",
        "body": text,
        "spacing": "tight",
        "is_active": False,
    }  # hidden until Wise-Teck supplies the real content


def cta(tag, title, text, primary, secondary=None):
    s = {
        "layout": "cta",
        "eyebrow": tag,
        "title": title,
        "subtitle": text,
        "spacing": "tight",
        "anchor": "cta",
        "button_label": primary[0],
        "button_url": primary[1],
        "button_style": "gold",
    }
    if secondary:
        s.update(button2_label=secondary[0], button2_url=secondary[1], button2_style="outline-light")
    return s


def quote(text, hl, who, role, icon):
    return {"quote_text": text, "quote_highlight": hl, "quote_author": who, "quote_role": role, "quote_icon": icon}


# --------------------------------------------------------------------------------------- pages
def home():
    H = [img("01", i) for i in range(15)]
    sections = [
        {
            "layout": "home_hero",
            "eyebrow": "WISE-TECK",
            "title": "Turning Professional Skills into Self-Earning Opportunities",
            "highlight": "Opportunities",
            "subtitle": "Gain in-demand skills, work on real projects, access mentorship and corporate opportunities, and move towards employment, freelancing, or your own business.",
            "button_label": "Explore Programs",
            "button_url": "#programs",
            "button_style": "navy",
            "button2_label": "Watch Overview",
            "button2_url": "#about",
            "button2_style": "ghost",
            "button2_icon": "fa-play",
            "items": [
                {"group": "tags", "icon": i, "title": t}
                for i, t in [
                    ("fa-layer-group", "Skills|Development"),
                    ("fa-rocket", "Business|Incubation"),
                    ("fa-laptop", "Practical|Projects"),
                    ("fa-chart-column", "Self-Earning|Opportunities"),
                ]
            ],
        },
        {
            "layout": "home_about",
            "anchor": "about",
            "divider_after": "a",
            "eyebrow": "About Wise-Teck",
            "title": "About Wise-Teck",
            "body": "Wise-Teck is a professional skills, business incubation and earning platform of WISE Education Society. It bridges education with practical experience, helping students and professionals build real skills, work on projects, and create sustainable earning opportunities.",
            "button_label": "Read More",
            "button_url": P["about"],
            "image_url": H[0],
            "image_alt": "Wise-Teck Earning Centre, 48-Main Gulberg, Lahore",
        },
        {
            "layout": "home_ecosystem",
            "anchor": "ecosystem",
            "divider_after": "b",
            "motif": "eco",
            "eyebrow": "Our Ecosystem",
            "title": "From Education to Self-Earning",
            "highlight": "Self-Earning",
            "center_small": "Wise-Teck",
            "center_big": "Earning Centre",
            "center_url": P["centre"],
            "list_title": "Three Programs, One Earning Centre",
            "body": "Students from all three programs come to Wise-Teck to learn professional skills. After completing their skills training, they move to the Wise-Teck Earning Centre, where they work on practical projects and explore earning opportunities.",
            "list_items": "Wise Support Hub — Intermediate Level (ICS)\nWise College — ADP / BS Degree Programs\nProfessional Paid Courses — Weekend Classes\nWise-Teck Earning Centre — practical projects & self-earning",
            "button_label": "Visit Earning Centre",
            "button_url": P["centre"],
            "items": [
                it("fa-users", "Wise Support Hub", link_url=P["hub"]),
                it("fa-graduation-cap", "Wise College", link_url=P["college"]),
                it("fa-layer-group", "Professional Paid Courses", link_url=P["courses"]),
            ],
        },
        {
            "layout": "home_programs",
            "anchor": "programs",
            "divider_after": "a",
            "motif": "programs",
            "title": "Programs Working Under WISE-TECK",
            "lined": True,
            "subtitle": "Three integrated programs that provide education, professional skills, practical experience and earning opportunities.",
            "item_label": "Read More",
            "center_small": "Move to",
            "center_big": "Wise-Teck Earning Centre",
            "center_url": P["centre"],
            "button_icon": "fa-chart-simple",
            "items": [
                it(
                    "fa-users",
                    "Wise Support Hub",
                    image_url=H[1],
                    link_url=P["hub"],
                    bullets="Fully Funded Educational & Skills Training Program\nIntermediate Level (ICS)\nBISE Lahore",
                ),
                it(
                    "fa-graduation-cap",
                    "Wise College Degree Programs",
                    image_url=H[2],
                    link_url=P["college"],
                    bullets="Higher Education with Professional Skills\nADP / BS Programs\nUniversity of the Punjab",
                ),
                it(
                    "fa-layer-group",
                    "Professional Paid Courses",
                    image_url=H[4],
                    link_url=P["courses"],
                    bullets="Industry-Relevant Skills\nWeekend Classes\nOpen for All",
                ),
            ],
        },
        {
            "layout": "home_services",
            "anchor": "services",
            "divider_after": "b",
            "motif": "services",
            "title": "Our Professional Services",
            "lined": True,
            "subtitle": "End-to-end support for skill development, project execution and real earning opportunities.",
            "sub_title": "Practical Skills, Real Projects, Earning Opportunities.",
            "items": [
                it(i, t, link_url=h)
                for i, t, h in [
                    ("fa-cubes", "Skills Development", P["blocks"]),
                    ("fa-rocket", "Business Incubation", P["incubation"]),
                    ("fa-laptop", "Corporate Technology Services", P["corporate"]),
                    ("fa-layer-group", "Projects-Based Earning", P["centre"]),
                    ("fa-coins", "Student Loan Scheme", P["loan"]),
                    ("fa-briefcase", "Placement Department", P["placement"]),
                ]
            ]
            + [
                it("", t, group="second", image_url=s, link_url=P["blocks"])
                for s, t in [
                    (H[5], "E-Commerce|(Dehleze)"),
                    (H[6], "Web|Development"),
                    (H[7], "Graphic|Designing"),
                    (H[8], "Video|Editing"),
                    (H[9], "Digital|Marketing"),
                    (H[10], "Freelancing"),
                ]
            ],
        },
        {
            "layout": "home_weekend",
            "image_url": H[11],
            "image_alt": "Professional learner on a laptop",
            "eyebrow": "Professional Paid Courses",
            "title": "Weekend Professional Training Programs",
            "subtitle": "Industry-relevant skills for students, graduates, working professionals and entrepreneurs.",
            "button_label": "Explore Courses",
            "button_url": P["courses"],
            "button_style": "purple",
            "items": [
                it(i, t)
                for i, t in [
                    ("fa-graduation-cap", "Job|Upgradation"),
                    ("fa-briefcase", "Business|Advancement"),
                    ("fa-chart-column", "Self-Earning|Guidance"),
                    ("fa-hand-holding-dollar", "Earning|Opportunities"),
                    ("fa-calendar-week", "Weekend|Classes"),
                ]
            ],
        },
        {
            "layout": "home_stories",
            "anchor": "stories",
            "motif": "stories",
            "title": "Success Stories From Our Learners",
        },
        {
            "layout": "home_partners",
            "anchor": "partners",
            "motif": "collab",
            "title": "Corporate & Industry Collaborations",
            "subtitle": "We work with leading industry partners to provide real projects, internships and earning opportunities for our students and graduates.",
            "button_label": "Explore Partnerships",
            "button_url": P["corporate"],
            "image_url": H[14],
            "image_alt": "Corporate collaboration meeting",
            "sub_title": "Trusted Industry Collaborators",
            "items": [
                it(
                    "",
                    "Punjab Skills Development Fund",
                    logo_html='<span class="psdf"><span class="box">PSDF</span><small>PUNJAB SKILLS<br/>DEVELOPMENT<br/>FUND</small></span>',
                ),
                it(
                    "",
                    "National Incubation Center Lahore",
                    logo_html='<span class="nic"><span class="n">Ni</span><span class="c">C</span><span class="l">Lahore</span></span>',
                ),
                it("fa-handshake", "Partner With Wise-Teck", subtitle="Become a partner →", link_url=P["contact"]),
            ],
        },
    ]
    return (
        "home",
        "Wise-Teck | Turning Professional Skills into Self-Earning",
        "Wise-Teck, a project of WISE Education Society — Transforming Learning into Earning through Technology, Innovation and Entrepreneurship.",
        sections,
    )


def about():
    obj = [
        (
            "fa-screwdriver-wrench",
            "Skills Training",
            "Provide students with professional and technical skills needed in today's job market.",
            ("Earning Blocks", P["blocks"]),
        ),
        (
            "fa-chart-line",
            "Self-Earning",
            "Help students use their skills to earn money through real projects, freelancing, jobs, and businesses.",
            ("Earning Centre", P["centre"]),
        ),
        (
            "fa-coins",
            "Student Loan Support",
            "Help eligible students get loans to start their own businesses.",
            ("Student Loan Scheme", P["loan"]),
        ),
        (
            "fa-briefcase",
            "Job Placement",
            "Help students and graduates find jobs, internships, and earning opportunities.",
            ("Placement", P["placement"]),
        ),
        (
            "fa-laptop-code",
            "Corporate Services",
            "Provide IT, software development, digital marketing, and other technology services to companies and businesses.",
            ("Corporate Services", P["corporate"]),
        ),
        (
            "fa-rocket",
            "Business Incubation Centre",
            "Help students turn their business ideas into real businesses through guidance and support.",
            ("Incubation Centre", P["incubation"]),
        ),
        (
            "fa-handshake",
            "Industry Partnerships",
            "Build connections with companies, software houses, and industry experts to create more work and earning opportunities for students.",
            ("Partnerships", P["corporate"]),
        ),
        (
            "fa-layer-group",
            "Professional Paid Courses",
            "Offer paid courses to help students, graduates, and working professionals learn new skills, improve their jobs, and grow their careers.",
            ("Paid Courses", P["courses"]),
        ),
    ]
    sections = [
        hero(
            "about",
            [HOME, ("About Wise-Teck", "")],
            "INTRODUCTION WISE-TECK",
            "Bridging Education, Industry & Self-Earning",
            "Self-Earning",
            "Transforming Learning into Earning through Technology, Innovation and Entrepreneurship.",
            ("Our Objectives", "#objectives"),
            ("Wise Eco System", "#ecosystem", "fa-diagram-project"),
            photo=(img("02", 0) or img("01", 0), "Wise-Teck Earning Centre"),
            badge=("fa-certificate", "Registered with Registrar Firms, Lahore"),
        ),
        split(
            "Who We Are",
            "A Skills, Incubation & Earning Platform",
            "Earning Platform",
            [
                "Wise-Teck, a project of Wise Education Society, is a professional skills development, business incubation, and earning platform dedicated to transforming knowledge and skills into practical economic opportunities.",
                "Operating through an integrated education-to-earning ecosystem, Wise-Teck connects students with industry professionals, real-world projects, corporate services, and entrepreneurial opportunities.",
                "Its core focus is to develop a skilled workforce, support emerging entrepreneurs, and enable individuals to build sustainable careers through employment, freelancing, and independent businesses.",
            ],
            visual="quote",
            div="a",
            **quote(
                "Turning Students into Self-Earning Individuals.",
                "Self-Earning",
                "Wise-Teck",
                "A project of Wise Education Society",
                "fa-rocket",
            ),
        ),
        split(
            "Our Vision",
            "Education That Goes Beyond Degrees",
            "Beyond Degrees",
            [
                "To create a future where education goes beyond degrees, equipping every student with professional skills and the confidence to become self-earning member of the society."
            ],
            visual="photo",
            side="left",
            spacing="tight",
            button=("Visit Earning Centre", P["centre"]),
            image_url=img("01", 14),
            image_alt="Students and professionals collaborating",
        ),
        cards(
            "Our Core Objectives",
            "Eight Objectives, One Goal",
            "One Goal",
            obj,
            cols=4,
            numbered=True,
            div="b",
            anchor="objectives",
        ),
        strip(
            "Programs Working Under Wise-Teck",
            eyebrow="Wise Eco System",
            hl="Wise-Teck",
            lined=False,
            div="a",
            anchor="ecosystem",
            sub="Wise-Teck brings together three educational and training programs. Each program provides different education and training opportunities, while Wise-Teck helps students develop professional skills for their future careers and earning opportunities.",
        ),
        pathway(),
        cta(
            "Join Wise-Teck",
            "Start Your Journey to Self-Earning",
            "Learn professional skills, work on real projects and explore earning opportunities.",
            ("Apply Now", P["contact"]),
            ("Explore Programs", "/#programs"),
        ),
    ]
    return (
        "about",
        "About Wise-Teck | Education, Industry & Self-Earning",
        "About Wise-Teck, a project of WISE Education Society: our vision, core objectives and the Wise eco system linking education, industry and self-earning.",
        sections,
    )


def program_page(
    key,
    title,
    hl,
    eyebrow,
    lead,
    facts,
    photo,
    badge,
    ov_title,
    ov_hl,
    overview,
    cards_title,
    cards_hl,
    card_items,
    divs,
    extra=None,
    cols=4,
):
    s = [
        hero(
            key,
            [HOME, ("Programs", "/#programs"), (eyebrow.title(), "")],
            eyebrow,
            title,
            hl,
            lead,
            ("Apply Now", P["contact"]),
            ("Learn More", "#overview", "fa-arrow-down"),
            photo=photo,
            badge=badge,
            facts=facts,
        ),
        split(
            "Program Overview",
            ov_title,
            ov_hl,
            overview,
            visual="checklist",
            div=divs[0],
            anchor="overview",
            list_title="Program at a Glance",
            list_items="\n".join(t for _, t in facts),
        ),
        cards("What Students Receive", cards_title, cards_hl, card_items, cols=cols, div=divs[1]),
    ]
    if extra:
        s.append(extra)
    s += [pathway(EARN_NOTE), strip("Explore All Three WISE Programs", div=divs[2])]
    return s


def hub():
    s = program_page(
        "hub",
        "Wise Support Hub",
        "Support Hub",
        "WISE SUPPORT HUB",
        "Fully funded intermediate (ICS) education for orphaned and underprivileged girls, with free professional skills training up to self-earning.",
        [
            ("fa-hand-holding-heart", "Fully Funded Educational & Skills Training Program"),
            ("fa-school", "Intermediate Level"),
            ("fa-certificate", "Affiliated with BISE"),
        ],
        (img("03", 0) or img("01", 1), "Students in the computer lab"),
        ("fa-heart", "Free education, lunch, transport & skills training"),
        "A Better, Financially Independent Future",
        "Financially Independent",
        [
            "Wise Support Hub provides fully funded intermediate (ICS) education for orphaned and underprivileged girls, along with free education, free daily lunch, free transport, and free professional skills training up to self-earning, helping students build a better and financially independent future during studies."
        ],
        "Everything Provided Free of Cost",
        "Free of Cost",
        [
            (
                "fa-book-open",
                "Free Education",
                "Fully funded intermediate (ICS) education, affiliated with the Board of Intermediate and Secondary Education (BISE).",
            ),
            ("fa-utensils", "Free Daily Lunch", "A free daily lunch for every student."),
            ("fa-bus", "Free Transport", "Free transport so students can attend every day."),
            (
                "fa-laptop-code",
                "Free Skills Training",
                "Free professional skills training up to self-earning, during studies.",
            ),
        ],
        ("b", "a", "b"),
    )
    s.append(
        cta(
            "Wise Support Hub",
            "Help Build a Financially Independent Future",
            "Fully funded education and skills training for orphaned and underprivileged girls.",
            ("Contact Admissions", P["contact"]),
            ("Earning Centre", P["centre"]),
        )
    )
    return (
        "wise-support-hub",
        "Wise Support Hub | Free Education for Girls | Wise-Teck",
        "Wise Support Hub: fully funded intermediate (ICS) education and free professional skills training for orphaned and underprivileged girls.",
        s,
    )


def college():
    why = cards(
        "Why Wise College",
        "Learning Supported By",
        "Supported By",
        [
            ("fa-user-tie", "Experienced Faculty", "Experienced MPhil/PhD faculty."),
            ("fa-chalkboard", "Digital Classrooms", "Modern digital classrooms."),
            (
                "fa-chart-line",
                "Skills up to Self-Earning",
                "Professional skills training up to self-earning, enabling students to explore earning opportunities during their studies.",
            ),
        ],
        spacing="tight",
    )
    s = program_page(
        "college",
        "Wise College",
        "College",
        "WISE COLLEGE",
        "ADP and BS degree programs with professional skills training up to self-earning — affiliated with the University of the Punjab.",
        [
            ("fa-graduation-cap", "Higher Education with Professional Skills"),
            ("fa-award", "Degree Level Program"),
            ("fa-building-columns", "Affiliated with University of the Punjab (PU)"),
        ],
        (img("04", 0) or img("01", 2), "Students in a lecture hall"),
        ("fa-user-graduate", "MPhil/PhD faculty & digital classrooms"),
        "Degrees That Lead to Earning",
        "Earning",
        [
            "Wise College offers ADP and BS degree programs in Artificial Intelligence, E-Commerce, Software Engineering, and Data Science, supported by experienced MPhil/PhD faculty, digital classrooms, and professional skills training up to self-earning, enabling students to develop practical skills and explore earning opportunities during their studies."
        ],
        "ADP & BS Degree Programs",
        "Degree Programs",
        [
            ("fa-brain", "Artificial Intelligence", "ADP and BS degree program in Artificial Intelligence."),
            ("fa-cart-shopping", "E-Commerce", "ADP and BS degree program in E-Commerce."),
            ("fa-code", "Software Engineering", "ADP and BS degree program in Software Engineering."),
            ("fa-chart-pie", "Data Science", "ADP and BS degree program in Data Science."),
        ],
        ("a", "b", "a"),
        extra=why,
    )
    s.append(
        cta(
            "Wise College",
            "Earn a Degree, Build Real Skills",
            "ADP and BS programs in AI, E-Commerce, Software Engineering and Data Science.",
            ("Apply Now", P["contact"]),
            ("Earning Centre", P["centre"]),
        )
    )
    return (
        "wise-college",
        "Wise College Degree Programs | Wise-Teck",
        "Wise College offers ADP and BS degree programs affiliated with the University of the Punjab, combined with professional skills training.",
        s,
    )


def courses():
    feats = [
        ("fa-graduation-cap", "Job Upgradation", "Improve your current job with new professional skills."),
        ("fa-briefcase", "Business Advancement", "Skills that help grow your business."),
        ("fa-chart-column", "Self-Earning Guidance", "Guidance to start earning with your skills."),
        ("fa-hand-holding-dollar", "Earning Opportunities", "Access to Wise-Teck earning opportunities."),
    ]
    s = program_page(
        "courses",
        "Professional Paid Courses",
        "Paid Courses",
        "PROFESSIONAL PAID COURSES",
        "Paid courses to help students, graduates, and working professionals learn new skills, improve their jobs, and grow their careers.",
        [
            ("fa-briefcase", "Industry-Relevant Skills"),
            ("fa-calendar-week", "Weekend Classes"),
            ("fa-door-open", "Open for All"),
        ],
        (img("01", 11), "Professional learner on a laptop"),
        ("fa-calendar-week", "Weekend Professional Training Programs"),
        "Weekend Professional Training Programs",
        "Training Programs",
        [
            "Wise-Teck offers paid courses to help students, graduates, and working professionals learn new skills, improve their jobs, and grow their careers.",
            "Industry-relevant skills for students, graduates, working professionals and entrepreneurs.",
        ],
        "Why Take a Paid Course",
        "Paid Course",
        feats,
        ("b", "a", "b"),
        extra=placeholder(
            "Course List, Fees & Timings",
            "Add each course with its duration, fee, weekend schedule and next start date — to be supplied by Wise-Teck.",
        ),
    )
    s.append(
        cta(
            "Professional Paid Courses",
            "Upgrade Your Skills This Weekend",
            "Industry-relevant weekend classes, open for all.",
            ("Enquire Now", P["contact"]),
            ("Earning Centre", P["centre"]),
        )
    )
    return (
        "professional-paid-courses",
        "Professional Paid Courses | Wise-Teck",
        "Weekend professional training programs at Wise-Teck for students, graduates and working professionals: practical skills that lead to earning.",
        s,
    )


def centre():
    s = [
        hero(
            "centre",
            [HOME, ("Wise-Teck Earning Centre", "")],
            "WISE-TECK EARNING CENTRE",
            "From Professional Skills to Self-Earning",
            "Self-Earning",
            "The final stage of Wise Education Society's education-to-earning model.",
            ("Our Earning Blocks", P["blocks"]),
            ("Earning Pathway", "#pathway", "fa-route"),
            photo=(img("07", 0) or img("01", 0), "Students working in the Earning Centre"),
            badge=("fa-chart-line", "Freelancing, employment & own business"),
        ),
        split(
            "About Earning Centre",
            "Where Skills Start Earning",
            "Start Earning",
            [
                "Wise-Teck Earning Centre is the final stage of Wise Education Society's education-to-earning model.",
                "Students from all three WISE programs — Wise Support Hub, Wise College Degree Programs, and Professional Paid Courses — receive professional skills training through Wise-Teck during or after their studies.",
                "After developing their skills, students move to the Wise-Teck Earning Centre, where they work on real-world projects, gain practical experience, and receive guidance to start earning.",
                "The Earning Centre helps students build their careers through freelancing, employment, and starting their own businesses.",
            ],
            visual="quote",
            div="a",
            **quote(
                "To help students turn their education and professional skills into real earning opportunities and become financially independent.",
                "financially independent.",
                "Wise Earning Centre Outcome",
                "Our goal for every student",
                "fa-bullseye",
            ),
        ),
        cards(
            "What We Provide",
            "Support at Every Step",
            "Step",
            [
                ("fa-diagram-project", "Real-World Projects", "Practical experience through real-world projects"),
                ("fa-user-tie", "Professional Guidance", "Guidance from experienced professionals"),
                ("fa-laptop-house", "Freelancing & Client Work", "Freelancing and client work opportunities"),
                ("fa-briefcase", "Job & Career Support", "Job and career support", ("Placement", P["placement"])),
                (
                    "fa-rocket",
                    "Business Startup Mentorship",
                    "Business startup guidance and mentorship",
                    ("Incubation Centre", P["incubation"]),
                ),
                ("fa-handshake", "Industry Networking", "Industry connections and professional networking"),
            ],
            cols=3,
            numbered=True,
            div="b",
        ),
        steps("Our Earning Pathway", "From Education to Self-Earning", "Self-Earning", PATHWAY, anchor="pathway"),
        strip(div="a"),
        cta(
            "Earning Blocks",
            "Different Skills. Different Opportunities.",
            "One Goal: Self-Earning. Explore the earning blocks at the Wise-Teck Earning Centre.",
            ("Our Earning Blocks", P["blocks"]),
            ("Apply Now", P["contact"]),
        ),
    ]
    return (
        "earning-centre",
        "Wise-Teck Earning Centre | From Skills to Self-Earning",
        "The Wise-Teck Earning Centre turns professional skills into income through practical projects, mentorship, guidance and earning opportunities.",
        s,
    )


def blocks():
    B = [
        (
            img("06", 0),
            "Software & Web Development",
            "Students develop websites, software, and online solutions for businesses and clients.",
        ),
        (
            img("06", 2),
            "E-Commerce & Dehleze",
            "Students learn online selling, product management, and order handling through Dehleze, Wise-Teck's multi-vendor e-commerce platform.",
        ),
        (
            img("06", 3),
            "Digital Marketing & Creative Services",
            "Students work on graphic design, video editing, social media management, content creation, and digital marketing projects.",
        ),
        (
            img("06", 5),
            "Freelancing & Remote Services",
            "Students learn how to find online clients, create freelance profiles, write proposals, and complete projects.",
        ),
        (
            img("06", 4),
            "AI, Data Analytics & Business Solutions",
            "Students use AI, Power BI, data analysis, and other digital tools to work on business projects.",
        ),
        (
            img("10", 0) or img("04", 6),
            "Entrepreneurship & Business Incubation",
            "Students receive guidance to develop business ideas, start small businesses, and create their own earning opportunities.",
        ),
    ]
    s = [
        hero(
            "blocks",
            [HOME, ("Earning Centre", P["centre"]), ("Our Earning Blocks", "")],
            "OUR EARNING BLOCKS",
            "Different Skills. Different Opportunities. One Goal: Self-Earning.",
            "One Goal: Self-Earning.",
            "Wise-Teck Earning Centre has different earning blocks where students use their skills to work on real projects and explore earning opportunities.",
            ("Explore Blocks", "#blocks"),
            ("How It Works", "#how", "fa-gears"),
            tags=[
                ("fa-code", "Software & Web"),
                ("fa-cart-shopping", "E-Commerce & Dehleze"),
                ("fa-pen-nib", "Digital & Creative"),
                ("fa-laptop-house", "Freelancing"),
                ("fa-brain", "AI & Data"),
                ("fa-rocket", "Entrepreneurship"),
            ],
        ),
        {
            "layout": "earning_blocks",
            "anchor": "blocks",
            "divider_after": "b",
            "eyebrow": "Six Earning Blocks",
            "title": "Choose Your Earning Block",
            "highlight": "Earning Block",
            "subtitle": "Students join an earning block according to their skills and interests.",
            "item_label": "EARNING BLOCK",
            "items": [it("", t, d, image_url=src) for src, t, d in B],
        },
        steps(
            "How Earning Blocks Work",
            "From Skills to Self-Earning",
            "Self-Earning",
            BLOCK_STEPS,
            anchor="how",
            div="a",
            sub="Skills Development → Earning Block Selection → Practical Projects → Client Work → Self-Earning",
            note="Students join an earning block according to their **skills and interests**.",
        ),
        cta(
            "Wise-Teck Earning Centre",
            "Ready to Start Earning?",
            "Pick the earning block that matches your skills and interests.",
            ("Apply Now", P["contact"]),
            ("Visit Earning Centre", P["centre"]),
        ),
    ]
    return (
        "earning-blocks",
        "Our Earning Blocks | Wise-Teck",
        "Explore the six earning blocks at the Wise-Teck Earning Centre and choose the skills, projects and mentorship that lead you to self-earning.",
        s,
    )


def service_page(slug, key, crumb, eyebrow, title, hl, lead, visual, body):
    h = hero(
        key,
        [HOME, ("Services", "/#services"), (crumb, "")],
        eyebrow,
        title,
        hl,
        lead,
        ("Get in Touch", P["contact"]),
        ("Learn More", "#details", "fa-arrow-down"),
        **visual,
    )
    return (slug, f"{crumb} | Wise-Teck", lead, [h] + body)


def corporate():
    return service_page(
        "corporate-services",
        "corporate",
        "Corporate Technology Services",
        "CORPORATE TECHNOLOGY SERVICES",
        "Technology Services, Delivered",
        "Delivered",
        "Wise-Teck provides IT support, software development, digital marketing and other technology services for companies and businesses of every size.",
        {
            "tags": [
                ("fa-server", "IT|Services"),
                ("fa-code", "Software|Development"),
                ("fa-bullhorn", "Digital|Marketing"),
                ("fa-handshake", "Industry|Partnerships"),
            ]
        },
        [
            split(
                "Corporate Services",
                "Technology Services for Businesses",
                "Businesses",
                [
                    "Wise-Teck provides IT, software development, digital marketing, and other technology services to companies and businesses.",
                    "Through industry partnerships, Wise-Teck builds connections with companies, software houses, and industry experts to create more work and earning opportunities for students.",
                ],
                visual="photo",
                div="b",
                anchor="details",
                image_url=img("01", 14),
                image_alt="Corporate collaboration meeting",
            ),
            cards(
                "What We Offer",
                "Our Corporate Services",
                "Services",
                [
                    ("fa-server", "IT Services", "IT services for companies and businesses."),
                    (
                        "fa-code",
                        "Software Development",
                        "Websites, software, and online solutions for businesses and clients.",
                    ),
                    ("fa-bullhorn", "Digital Marketing", "Digital marketing, social media and creative services."),
                    (
                        "fa-microchip",
                        "Other Technology Services",
                        "Other technology services, including AI, data analytics and business solutions.",
                    ),
                ],
                cols=4,
                div="a",
            ),
            placeholder(
                "Service Details & Past Clients",
                "Add service packages, process, industries served and client examples — to be supplied by Wise-Teck.",
            ),
            cta(
                "Partner With Us",
                "Work With Wise-Teck",
                "Technology services for your business, and real projects for skilled students.",
                ("Contact Us", P["contact"]),
                ("Earning Blocks", P["blocks"]),
            ),
        ],
    )


def incubation():
    return service_page(
        "business-incubation",
        "incubation",
        "Business Incubation Centre",
        "BUSINESS INCUBATION CENTRE",
        "Turning Business Ideas into Real Businesses",
        "Real Businesses",
        "The Wise-Teck Business Incubation Centre helps students turn their business ideas into real businesses through mentorship, guidance and support.",
        {
            "tags": [
                ("fa-lightbulb", "Business|Ideas"),
                ("fa-user-tie", "Startup|Mentorship"),
                ("fa-handshake", "Industry|Networking"),
                ("fa-coins", "Student Loan|Support"),
            ]
        },
        [
            split(
                "About the Centre",
                "Supporting Emerging Entrepreneurs",
                "Entrepreneurs",
                [
                    "Wise-Teck, a project of Wise Education Society, is a professional skills development, business incubation, and earning platform dedicated to transforming knowledge and skills into practical economic opportunities.",
                    "Its core focus is to develop a skilled workforce, support emerging entrepreneurs, and enable individuals to build sustainable careers through employment, freelancing, and independent businesses.",
                ],
                visual="quote",
                div="b",
                anchor="details",
                **quote(
                    "Transforming Learning into Earning through Technology, Innovation and Entrepreneurship.",
                    "Entrepreneurship.",
                    "Wise-Teck",
                    "Turning Students into Self-Earning Individuals.",
                    "fa-rocket",
                ),
            ),
            cards(
                "How We Support You",
                "From Idea to Your Own Business",
                "Your Own Business",
                [
                    (
                        "fa-lightbulb",
                        "Business Idea Development",
                        "Students receive guidance to develop their business ideas.",
                    ),
                    (
                        "fa-user-tie",
                        "Startup Guidance & Mentorship",
                        "Business startup guidance and mentorship to help students start small businesses.",
                    ),
                    (
                        "fa-chalkboard-user",
                        "Guidance from Experienced Professionals",
                        "Wise-Teck connects students with industry professionals, real-world projects and entrepreneurial opportunities.",
                    ),
                    (
                        "fa-handshake",
                        "Industry Connections & Networking",
                        "Connections with companies, software houses, and industry experts to create more work and earning opportunities.",
                    ),
                    (
                        "fa-coins",
                        "Student Loan Support",
                        "Help for eligible students to get loans to start their own businesses.",
                        ("Student Loan Scheme", P["loan"]),
                    ),
                    (
                        "fa-diagram-project",
                        "Practical Projects & Client Work",
                        "Practical experience through real-world projects, freelancing and client work opportunities.",
                    ),
                ],
                cols=3,
                numbered=True,
                div="a",
            ),
            steps(
                "How It Works",
                "Your Path to Self-Earning",
                "Self-Earning",
                BLOCK_STEPS,
                note="**Entrepreneurship & Business Incubation** is one of the earning blocks at the Wise-Teck Earning Centre. Students join an earning block according to their skills and interests.",
            ),
            strip("Open to Students from All Three WISE Programs", div="b"),
            cta(
                "Our Outcome",
                "Become Financially Independent",
                "To help students turn their education and professional skills into real earning opportunities and become financially independent.",
                ("Share Your Idea", P["contact"]),
                ("Student Loans", P["loan"]),
            ),
        ],
    )


def loan():
    photo_src = img("10", 0) or img("04", 6)
    return service_page(
        "student-loan-scheme",
        "loan",
        "Student Loan Scheme",
        "STUDENT LOAN SCHEME",
        "Student Loan Support",
        "Support",
        "The Wise-Teck Student Loan Scheme helps eligible students get loans to start their own businesses, with guidance from the idea to launch.",
        {"photo": (photo_src, "Young entrepreneurs"), "badge": ("fa-coins", "For eligible students")},
        [
            split(
                "Student Loan Support",
                "Funding to Start Your Own Business",
                "Your Own Business",
                [
                    "Wise-Teck helps eligible students get loans to start their own businesses.",
                    "Loan support works alongside the Business Incubation Centre, which helps students turn their business ideas into real businesses through guidance and support.",
                ],
                visual="photo",
                div="a",
                anchor="details",
                button=("Incubation Centre", P["incubation"]),
                image_url=photo_src,
                image_alt="Young entrepreneurs working on a business",
            ),
            cards(
                "How It Connects",
                "Part of the Self-Earning Journey",
                "Self-Earning",
                [
                    (
                        "fa-lightbulb",
                        "Develop Your Idea",
                        "Students receive guidance to develop business ideas.",
                        ("Incubation Centre", P["incubation"]),
                    ),
                    (
                        "fa-coins",
                        "Get Loan Support",
                        "Eligible students get help to obtain loans to start their own businesses.",
                    ),
                    (
                        "fa-store",
                        "Start Your Business",
                        "Start small businesses and create your own earning opportunities.",
                    ),
                ],
                div="b",
            ),
            placeholder(
                "Eligibility, Loan Amounts & Application Process",
                "Add who is eligible, loan limits, partner institutions, required documents and the step-by-step application process — to be supplied by Wise-Teck.",
            ),
            cta(
                "Student Loan Scheme",
                "Have a Business Idea?",
                "Talk to us about loan support and the Business Incubation Centre.",
                ("Contact Us", P["contact"]),
                ("Incubation Centre", P["incubation"]),
            ),
        ],
    )


def placement():
    s = [
        hero(
            "placement",
            [HOME, ("Placement", "")],
            "JOB PLACEMENT",
            "Jobs, Internships & Earning Opportunities",
            "Earning Opportunities",
            "Wise-Teck job placement and career services help students and graduates find jobs, internships and earning opportunities with industry partners.",
            ("Get Career Support", P["contact"]),
            ("Learn More", "#details", "fa-arrow-down"),
            photo=(img("08", 1) or img("01", 14), "Graduate at work"),
            badge=("fa-briefcase", "Job and career support"),
        ),
        split(
            "Placement Department",
            "From Skills to Careers",
            "Careers",
            [
                "Wise-Teck helps students and graduates find jobs, internships, and earning opportunities.",
                "Through industry partnerships, Wise-Teck builds connections with companies, software houses, and industry experts to create more work and earning opportunities for students.",
            ],
            visual="checklist",
            div="a",
            anchor="details",
            list_title="Career Support Includes",
            list_items="Job and career support\nInternship opportunities\nIndustry connections and professional networking\nFreelancing and client work opportunities\nGuidance from experienced professionals",
        ),
        cards(
            "Career Pathways",
            "Three Ways to Earn",
            "Earn",
            [
                ("fa-briefcase", "Employment", "Find jobs and internships with industry partners."),
                (
                    "fa-laptop-house",
                    "Freelancing",
                    "Find online clients, create freelance profiles, write proposals, and complete projects.",
                    ("Earning Blocks", P["blocks"]),
                ),
                (
                    "fa-rocket",
                    "Own Business",
                    "Start small businesses and create your own earning opportunities.",
                    ("Incubation Centre", P["incubation"]),
                ),
            ],
            sub="The Earning Centre helps students build their careers through freelancing, employment, and starting their own businesses.",
            div="b",
        ),
        placeholder(
            "Hiring Partners & Placement Process",
            "Add hiring partners, placement process and results — to be supplied by Wise-Teck.",
        ),
        cta(
            "Placement Department",
            "Ready for Your Next Step?",
            "Get help finding jobs, internships and earning opportunities.",
            ("Contact Placement", P["contact"]),
            ("Earning Centre", P["centre"]),
        ),
    ]
    return (
        "placement",
        "Job Placement & Career Services | Wise-Teck",
        "Helping students and graduates find jobs, internships, and earning opportunities.",
        s,
    )


def stories():
    s = [
        hero(
            "stories",
            [HOME, ("About", P["about"]), ("Success Stories", "")],
            "SUCCESS STORIES",
            "Stories From Our Learners",
            "Learners",
            "Students who turned professional skills into real earning opportunities.",
            ("Start Your Story", P["contact"]),
            tags=[
                ("fa-laptop-code", "Web|Development"),
                ("fa-bullhorn", "Digital|Marketing"),
                ("fa-laptop-house", "Freelancing"),
                ("fa-chart-line", "Self-Earning"),
            ],
        ),
        {
            "layout": "story_grid",
            "divider_after": "a",
            "eyebrow": "Success Stories",
            "title": "Real Skills, Real Earning",
            "highlight": "Real Earning",
        },
        placeholder(
            "More Success Stories",
            "Add more learner stories (name, program, earning result, photo) — to be supplied by Wise-Teck.",
        ),
        cta(
            "Your Turn",
            "Write Your Own Success Story",
            "Learn professional skills and start earning through the Wise-Teck Earning Centre.",
            ("Apply Now", P["contact"]),
            ("Explore Programs", "/#programs"),
        ),
    ]
    return (
        "success-stories",
        "Success Stories | From Skills to Jobs & Earning | Wise-Teck",
        "Read success stories from Wise-Teck learners who turned professional skills into jobs, earning and businesses of their own.",
        s,
    )


def contact():
    s = [
        hero(
            "contact",
            [HOME, ("Contact", "")],
            "CONTACT & ADMISSIONS",
            "Let’s Start Your Journey",
            "Journey",
            "Questions about programs, courses, services or partnerships? Get in touch with Wise-Teck.",
            ("Call Us Now", "tel:+923008410868", "fa-phone"),
            photo=(img("02", 0) or img("01", 0), "Wise-Teck Earning Centre, 48-Main Gulberg, Lahore"),
            badge=("fa-location-dot", "48-Main Gulberg, Lahore"),
        ),
        {
            "layout": "contact",
            "anchor": "details",
            "divider_after": "b",
            "form_title": "Send Us a Message",
            "form_fields": "Full Name | Your name\nPhone | +92 ...\nEmail | you@example.com\nI’m interested in |\nMessage | How can we help?",
            "list_items": "Wise Support Hub\nWise College\nProfessional Paid Courses\nEarning Centre\nBusiness Incubation\nStudent Loan Scheme\nCorporate Services\nPlacement\nPartnership\nOther",
            "button_label": "Send Message",
            "button_icon": "fa-paper-plane",
            "items": [
                it("fa-phone", "Phone", "+92 300 8410868", link_url="tel:+923008410868"),
                it("fa-envelope", "Email", "info@wise-teck.org", link_url="mailto:info@wise-teck.org"),
                it("fa-location-dot", "Address", "48-Main Gulberg, Lahore"),
                it(
                    "fa-building-columns",
                    "Wise-Teck",
                    "A project of Wise Education Society · Registered with Registrar Firms, Lahore",
                ),
            ],
        },
    ]
    return (
        "contact",
        "Contact & Admissions | Wise-Teck",
        "Contact Wise-Teck for admissions, programs and partnerships: call +92 300 8410868, email info@wise-teck.org or visit 48-Main Gulberg, Lahore.",
        s,
    )


def blog():
    s = [
        hero(
            "blog",
            [HOME, ("Blog", "")],
            "BLOG",
            "News & Insights",
            "Insights",
            "Updates, stories and articles from Wise-Teck.",
            ("Contact Us", P["contact"]),
        ),
        {
            "layout": "blog_list",
            "divider_after": "a",
            "eyebrow": "Latest Articles",
            "title": "From the Wise-Teck Blog",
            "highlight": "Blog",
            "item_label": "Read More",
        },
        cta(
            "Join Wise-Teck",
            "Start Your Journey to Self-Earning",
            "Learn professional skills, work on real projects and explore earning opportunities.",
            ("Apply Now", P["contact"]),
            ("Explore Programs", "/#programs"),
        ),
    ]
    return (
        "blog",
        "Blog: IT Skills, AI & Self-Earning | Wise-Teck",
        "Articles from Wise-Teck on IT skills, AI, cybersecurity and self-earning: practical guides for students, graduates and working professionals.",
        s,
    )


PAGES = [
    home,
    about,
    hub,
    college,
    courses,
    centre,
    blocks,
    corporate,
    incubation,
    loan,
    placement,
    stories,
    contact,
    blog,
]

NAV = [
    ("Home", P["home"], None),
    (
        "About",
        "#",
        [
            ("About Wise-Teck", P["about"]),
            ("Vision & Objectives", P["about"] + "#objectives"),
            ("Success Stories", P["stories"]),
        ],
    ),
    (
        "Programs",
        "#",
        [
            ("Wise Support Hub", P["hub"]),
            ("Wise College Degree Programs", P["college"]),
            ("Professional Paid Courses", P["courses"]),
        ],
    ),
    (
        "Services",
        "#",
        [
            ("Corporate Technology Services", P["corporate"]),
            ("Business Incubation Centre", P["incubation"]),
            ("Student Loan Scheme", P["loan"]),
        ],
    ),
    ("Earning Centre", "#", [("Wise-Teck Earning Centre", P["centre"]), ("Our Earning Blocks", P["blocks"])]),
    ("Placement", P["placement"], None),
    ("Contact", P["contact"], None),
]
FOOTER = [
    (
        "Quick Links",
        [
            ("Home", P["home"]),
            ("About", P["about"]),
            ("Programs", "/#programs"),
            ("Services", "/#services"),
            ("Contact", P["contact"]),
        ],
    ),
    (
        "Our Programs",
        [
            ("Wise Support Hub", P["hub"]),
            ("Wise College Degree Programs", P["college"]),
            ("Professional Paid Courses", P["courses"]),
        ],
    ),
    (
        "Our Services",
        [
            ("Earning Centre", P["centre"]),
            ("Placement Department", P["placement"]),
            ("Student Loan Scheme", P["loan"]),
            ("Corporate Services", P["corporate"]),
        ],
    ),
]
PROGRAMS = [
    (
        "fa-users",
        "Wise Support Hub",
        "Fully Funded Educational & Skills Training Program · Intermediate Level",
        P["hub"],
    ),
    (
        "fa-graduation-cap",
        "Wise College",
        "Higher Education with Professional Skills · Degree Level Program",
        P["college"],
    ),
    (
        "fa-layer-group",
        "Professional Paid Courses",
        "Paid courses for students, graduates, and working professionals.",
        P["courses"],
    ),
]
STORIES = [
    (
        "Aima Asif",
        "Web Development",
        "The hands-on training and project work helped me gain real experience and start my freelancing journey during my studies.",
        "seed/stories/aima-asif.jpg",
    ),
    (
        "Noshaba",
        "Digital Marketing",
        "The practical skills and guidance at Wise-Teck gave me the confidence to work on real projects and earn independently.",
        "seed/stories/noshaba.jpg",
    ),
]

SECTION_FIELDS = {f.name for f in Section._meta.get_fields() if getattr(f, "concrete", False)} - {
    "id",
    "page",
    "order",
    "image",
    "image2",
}
ITEM_FIELDS = {f.name for f in Item._meta.get_fields() if getattr(f, "concrete", False)} - {
    "id",
    "section",
    "order",
    "image",
}


class Command(BaseCommand):
    help = "Load the Wise-Teck v3 content (pages, sections, menu, footer, settings, programs, stories, blog, team, services)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true", help="Delete existing website content first (admin edits are lost)."
        )
        parser.add_argument(
            "--no-download", action="store_true", help="Keep photo links instead of downloading the photos."
        )

    # ---------------------------------------------------------------- photos
    def photo(self, url):
        """Download a photo once into media/seed/v3/ and return its media path ('' when it cannot be fetched)."""
        if not url or self.no_download:
            return ""
        if url in self.cache:
            return self.cache[url]
        name = hashlib.sha1(url.encode()).hexdigest()[:16]
        folder = Path(settings.MEDIA_ROOT) / "seed" / "v3"
        folder.mkdir(parents=True, exist_ok=True)
        existing = list(folder.glob(name + ".*"))
        if existing:
            rel = existing[0].relative_to(settings.MEDIA_ROOT).as_posix()
        else:
            try:
                full = url + "=s0" if "googleusercontent.com" in url and "=" not in url.rsplit("/", 1)[-1] else url
                req = urllib.request.Request(
                    full, headers={"User-Agent": "Mozilla/5.0 (site content import)"}
                )  # =s0: original size
                with urllib.request.urlopen(req, timeout=30) as r:
                    data, ctype = r.read(), r.headers.get("Content-Type", "")
                ext = {"image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}.get(ctype.split(";")[0], ".jpg")
                (folder / (name + ext)).write_bytes(data)
                rel = f"seed/v3/{name}{ext}"
            except Exception as e:  # keep the link instead
                self.stderr.write(f"  could not download a photo ({e}); keeping its link")
                rel = ""
        self.cache[url] = rel
        return rel

    def set_photo(self, obj, field, url_field, url):
        rel = url if url.startswith("seed/") else self.photo(url)  # local seed photo or a link to download
        if rel:
            setattr(obj, field, rel)
            setattr(obj, url_field, "")
        else:
            setattr(obj, url_field, url)

    # ---------------------------------------------------------------- main
    def handle(self, *args, reset=False, no_download=False, **opts):
        self.no_download, self.cache = no_download, {}
        if Page.objects.exists() and not reset:
            self.stderr.write(
                self.style.WARNING("Content already exists. Use --reset to replace it (admin edits are lost).")
            )
            return
        with transaction.atomic():
            if reset:
                for m in (Page, NavItem, FooterColumn, Program, SuccessStory, BlogPost, TeamMember, Service, Redirect):
                    m.objects.all().delete()
            self.settings()
            self.menu()
            self.pages()
            self.original_content()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {Page.objects.count()} pages, {Section.objects.count()} sections, {Item.objects.count()} cards, "
                f"{SuccessStory.objects.count()} stories, {BlogPost.objects.count()} blog posts, {TeamMember.objects.count()} team members, "
                f"{Service.objects.count()} services."
            )
        )

    def settings(self):
        s = SiteSettings.load()
        s.site_name = "WISE-TECK"
        s.topbar_text = "A Project of WISE Education Society"
        s.phone, s.email, s.address = "+92 300 8410868", "info@wise-teck.org", "48-Main Gulberg, Lahore"
        s.registration = "Registered with Registrar Firms, Lahore"
        s.apply_label, s.apply_url = "Apply Now", P["contact"]
        s.footer_text = "Skills, Projects, Mentorship and Earning Opportunities."
        s.facebook = s.instagram = s.linkedin = s.youtube = "#"
        s.meta_description = home()[2]
        s.contact_success = "Thank you — we will contact you soon."
        s.seo_name, s.city, s.country_code = "Wise-Teck", "Lahore", "PK"
        s.save()
        # old addresses keep working: the v3 static pages and the original site
        old = {
            "/index.html": "/",
            **{
                f"/{f}": u
                for f, u in [
                    ("about.html", P["about"]),
                    ("wise-support-hub.html", P["hub"]),
                    ("wise-college.html", P["college"]),
                    ("professional-paid-courses.html", P["courses"]),
                    ("earning-centre.html", P["centre"]),
                    ("earning-blocks.html", P["blocks"]),
                    ("corporate-services.html", P["corporate"]),
                    ("business-incubation.html", P["incubation"]),
                    ("student-loan-scheme.html", P["loan"]),
                    ("placement.html", P["placement"]),
                    ("success-stories.html", P["stories"]),
                    ("contact.html", P["contact"]),
                ]
            },
            "/explore-ecosystem/": P["about"] + "#ecosystem",
        }
        for o, n in old.items():
            Redirect.objects.update_or_create(
                old_path=o, defaults={"new_path": n, "permanent": True, "is_active": True}
            )

    def menu(self):
        for n, (label, url, kids) in enumerate(NAV):
            top = NavItem.objects.create(label=label, url=url, order=n)
            for k, (cl, cu) in enumerate(kids or []):
                NavItem.objects.create(label=cl, url=cu, parent=top, order=k)
        for n, (title, links) in enumerate(FOOTER):
            col = FooterColumn.objects.create(title=title, order=n)
            for k, (label, url) in enumerate(links):
                FooterLink.objects.create(column=col, label=label, url=url, order=k)
        for n, (icon, title, text, url) in enumerate(PROGRAMS):
            Program.objects.create(icon=icon, title=title, text=text, link_url=url, order=n)
        for n, (name, prog, quote_, src) in enumerate(STORIES):
            st = SuccessStory(
                title=f"{name} — {prog}",
                client_name=name,
                category=prog,
                short_description=quote_,
                display_order=n,
                is_featured=True,
            )
            self.set_photo(st, "image", "image_url", src)
            st.save()

    def pages(self):
        for build in PAGES:
            slug, title, desc, sections = build()
            page = Page.objects.create(slug=slug, title=title, meta_description=desc)
            for order, data in enumerate(sections, 1):
                data = dict(data)
                items = data.pop("items", [])
                unknown = set(data) - SECTION_FIELDS
                assert not unknown, (slug, unknown)
                sec = Section(
                    page=page,
                    order=order * 10,
                    **{k: v for k, v in data.items() if k not in ("image_url", "image2_url")},
                )
                self.set_photo(sec, "image", "image_url", data.get("image_url", ""))
                self.set_photo(sec, "image2", "image2_url", data.get("image2_url", ""))
                sec.save()
                for n, x in enumerate(items, 1):
                    x = {k: v for k, v in x.items() if v not in (None, "")}
                    unknown = set(x) - ITEM_FIELDS
                    assert not unknown, (slug, unknown)
                    item = Item(section=sec, order=n * 10, **{k: v for k, v in x.items() if k != "image_url"})
                    self.set_photo(item, "image", "image_url", x.get("image_url", ""))
                    item.save()
            self.stdout.write(f"  {page.get_absolute_url():32s} {len(sections)} sections")

    def original_content(self):
        """Blog, team and services from the original site (via v1); its four real stories are added unpublished."""
        path = SEED / "original_content.json"
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        media = Path(settings.MEDIA_ROOT)

        def file_or_blank(rel):
            return rel if rel and (media / rel).exists() else ""

        for n, s in enumerate(data.get("stories", [])):
            SuccessStory.objects.create(
                title=s["title"],
                slug=s.get("slug", ""),
                client_name=s.get("client_name", ""),
                category=s.get("category", ""),
                short_description=s.get("short_description", ""),
                description=s.get("description", ""),
                image=file_or_blank(s.get("image")),
                display_order=10 + n,
                is_featured=False,
                is_active=False,
            )
        for t in data.get("team", []):
            TeamMember.objects.create(
                name=t["name"],
                designation=t.get("designation", ""),
                short_description=t.get("short_description", ""),
                description=t.get("description", ""),
                image=file_or_blank(t.get("image")),
                service=t.get("service", ""),
                display_order=t.get("display_order", 0),
                is_active=t.get("is_active", True),
            )
        for b in data.get("blog", []):
            BlogPost.objects.create(
                title=b["title"],
                slug=b.get("slug", ""),
                short_description=b.get("short_description", ""),
                content=b.get("content", ""),
                featured_image=file_or_blank(b.get("featured_image") or b.get("image")),
                author=b.get("author", ""),
                category=b.get("category", ""),
                is_featured=b.get("is_featured", False),
                is_active=b.get("is_active", True),
                published_at=timezone.make_aware(parse_datetime(b["published_at"])) if b.get("published_at") else None,
            )
        for s in data.get("services", []):
            Service.objects.create(
                name=s["name"],
                short_description=s.get("short_description", ""),
                image=file_or_blank(s.get("image")),
                icon_file=file_or_blank(s.get("icon_file")),
                link_url=s.get("link_url", ""),
                display_order=s.get("display_order", 0),
                is_active=s.get("is_active", True),
            )
