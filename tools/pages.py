"""Page content for the Wise-Teck v3 site. Wording from "eco system (5).pdf" (home copy from the
reference design). Run:  python tools/pages.py
"""
from pathlib import Path

from motifs import motif
from build import (P, SECS, IMG, img, page, nav, sec_slice, btn, sec_head, blk, cards, steps, pstrip,
                   checklist, placeholder, quote, media, split, cta, page_hero, photo, orb, divider,
                   HOME_CRUMB, PATHWAY, BLOCK_STEPS, pathway_block, programs_block, ROOT, HERO_ART, wave_div)


def S(name):
    """Home section wrapper attrs: locked height + overlay reference position."""
    return f'data-ref-top="{SECS[name]["top"]}"'


# =====================================================================================  HOME
def home():
    H = [img("01", i) for i in range(15)]
    hero = f'''<header class="hero home-hero wt-sec" {S("hero")}>
  {HERO_ART}
{nav("home")}
  <div class="container hero-body">
    <div class="reveal">
      <div class="eyebrow">WISE-TECK</div>
      <h1>Turning Professional Skills into Self-Earning <span class="accent">Opportunities</span></h1>
      <p class="lead">Gain in-demand skills, work on real projects, access mentorship and corporate opportunities, and move towards employment, freelancing, or your own business.</p>
      <div class="ctas">{btn("Explore Programs", "#programs", "navy")}<a class="btn btn-ghost" href="#about"><span class="play"><i class="fa-solid fa-play"></i></span>Watch Overview</a></div>
    </div>
    {orb(None, [("fa-layer-group", "Skills<br/>Development"), ("fa-rocket", "Business<br/>Incubation"), ("fa-laptop", "Practical<br/>Projects"), ("fa-chart-column", "Self-Earning<br/>Opportunities")])}
  </div>
</header>'''

    about = f'''<section class="section about wt-sec" id="about" {S("about")}>
  <div class="container about-grid">
    <div class="reveal">
      <span class="kicker left">About Wise-Teck</span>
      <h2>About Wise-Teck</h2>
      <p>Wise-Teck is a professional skills, business incubation and earning platform of WISE Education Society. It bridges education with practical experience, helping students and professionals build real skills, work on projects, and create sustainable earning opportunities.</p>
      {btn("Read More", P["about"])}
    </div>
    <div class="about-media reveal d2"><div class="frame"><img src="{H[0]}" alt="Wise-Teck Earning Centre, 48-Main Gulberg, Lahore"/></div></div>
  </div>
</section>'''

    eco = f'''<section class="section eco wt-sec" id="ecosystem" {S("eco")}>
  <div class="container">
    <div class="sec-head reveal" style="margin-bottom:30px"><span class="kicker">Our Ecosystem</span><h2>From Education to <span class="accent">Self-Earning</span></h2></div>
    <div class="eco-grid">
      <figure class="reveal" style="margin:0">
        <div class="eorbit eorbit--in" style="--n:3">
          <div class="eorbit__system" aria-hidden="true"><svg class="eorbit__svg" viewBox="0 0 480 480" focusable="false">
            <defs><linearGradient id="orbitStroke" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#8b7cf6" stop-opacity=".6"/><stop offset="50%" stop-color="#6b4fd4" stop-opacity=".4"/><stop offset="100%" stop-color="#94a3b8" stop-opacity=".45"/></linearGradient><radialGradient id="orbitHalo"><stop offset="0" stop-color="#e4defd" stop-opacity=".95"/><stop offset=".7" stop-color="#ece9fd" stop-opacity=".55"/><stop offset="1" stop-color="#f1effe" stop-opacity="0"/></radialGradient></defs>
            <circle class="eorbit__halo" cx="240" cy="240" r="132" fill="url(#orbitHalo)"/>
            <circle class="eorbit__path" cx="240" cy="240" r="124" stroke="url(#orbitStroke)"/>
            <circle class="eorbit__path eorbit__path--near" cx="240" cy="240" r="102" stroke="url(#orbitStroke)"/></svg></div>
          <span class="eorbit__ray" style="--i:0" aria-hidden="true"><i class="ed ed1"></i><i class="ed ed2"></i></span><span class="eorbit__ray" style="--i:1" aria-hidden="true"><i class="ed ed1"></i><i class="ed ed2"></i></span><span class="eorbit__ray" style="--i:2" aria-hidden="true"><i class="ed ed1"></i><i class="ed ed2"></i></span>
          <div class="eorbit__center" aria-hidden="true"><div class="eorbit__spin"><img class="eorbit__face" src="assets/img/logo-round.svg" alt="" width="140" height="140"/><img class="eorbit__face eorbit__face--back" src="assets/img/logo-round.svg" alt="" width="140" height="140"/></div></div>
          <a class="eorbit__clabel" href="{P["centre"]}"><span>Wise-Teck</span><b>Earning Centre</b></a>
          <ol class="eorbit__nodes">
            <li class="eorbit__node" style="--i:0"><a href="{P["hub"]}"><span class="eorbit__badge"><i class="fa-solid fa-users"></i></span><span class="eorbit__t">Wise Support Hub</span></a></li>
            <li class="eorbit__node" style="--i:1"><a href="{P["college"]}"><span class="eorbit__badge"><i class="fa-solid fa-graduation-cap"></i></span><span class="eorbit__t">Wise College</span></a></li>
            <li class="eorbit__node" style="--i:2"><a href="{P["courses"]}"><span class="eorbit__badge"><i class="fa-solid fa-layer-group"></i></span><span class="eorbit__t">Professional Paid Courses</span></a></li>
          </ol>
        </div>
      </figure>
      <div class="glass eco-card v1glow reveal d2">
        <div class="badge"><i class="fa-solid fa-check"></i></div>
        <h3>Three Programs, One Earning Centre</h3>
        <p>Students from all three programs come to Wise-Teck to learn professional skills. After completing their skills training, they move to the Wise-Teck Earning Centre, where they work on practical projects and explore earning opportunities.</p>
        <ul class="checks"><li><i class="fa-solid fa-check"></i>Wise Support Hub &mdash; Intermediate Level (ICS)</li><li><i class="fa-solid fa-check"></i>Wise College &mdash; ADP / BS Degree Programs</li><li><i class="fa-solid fa-check"></i>Professional Paid Courses &mdash; Weekend Classes</li><li><i class="fa-solid fa-check"></i>Wise-Teck Earning Centre &mdash; practical projects &amp; self-earning</li></ul><a class="more" href="{P["centre"]}" style="margin-top:16px;display:inline-flex">Explore the Earning Centre <i class="fa-solid fa-arrow-right"></i></a>
      </div>
    </div>
  </div>
</section>'''

    progs = [
        (H[1], "fa-users", "Wise Support Hub", ["Fully Funded Educational &amp; Skills Training Program", "Intermediate Level (ICS)", "BISE Lahore"], P["hub"], "fa-angles-right"),
        (H[2], "fa-graduation-cap", "Wise College Degree Programs", ["Higher Education with Professional Skills", "ADP / BS Programs", "University of the Punjab"], P["college"], "fa-arrow-right"),
        (H[4], "fa-layer-group", "Professional Paid Courses", ["Industry-Relevant Skills", "Weekend Classes", "Open for All"], P["courses"], None),
    ]
    pc = []
    for n, (src, ic, t, lines, href, arrow) in enumerate(progs):
        li = "".join(f"<li>{x}</li>" for x in lines)
        pc.append(f'<article class="prog reveal d{n}"><div class="ph"><img src="{src}" alt="{t}"/></div><div class="bd"><span class="pic"><i class="fa-solid {ic}"></i></span><h3>{t}</h3><ul>{li}</ul><a class="more" href="{href}">Read More <i class="fa-solid fa-arrow-right"></i></a></div></article>')
        if arrow:
            pc.append(f'<div class="prog-arrow"><i class="fa-solid {arrow}"></i></div>')
    programs = f'''<section class="section programs wt-sec" id="programs" {S("programs")}>
  <div class="container">
    <div class="sec-head reveal" style="margin-bottom:30px"><h2 class="lined">Programs Working Under WISE-TECK</h2><p>Three integrated programs that provide education, professional skills, practical experience and earning opportunities.</p></div>
    <div class="prog-row">{"".join(pc)}</div>
    <div class="flow">
      <svg viewBox="0 0 1200 110" preserveAspectRatio="none" aria-hidden="true"><defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#6a2bd9"/></marker></defs>
        <path d="M190,0 L190,48 Q190,66 208,66 L400,66" fill="none" stroke="#6a2bd9" stroke-width="2" marker-end="url(#ah)" vector-effect="non-scaling-stroke"/>
        <path d="M1010,0 L1010,48 Q1010,66 992,66 L800,66" fill="none" stroke="#6a2bd9" stroke-width="2" marker-end="url(#ah)" vector-effect="non-scaling-stroke"/></svg>
      <a class="pill" href="{P["centre"]}"><i class="fa-solid fa-chart-simple"></i><span><small>Move to</small>Wise-Teck Earning Centre</span></a>
    </div>
  </div>
</section>'''

    svc = [("fa-cubes", "Skills Development", P["blocks"]), ("fa-rocket", "Business Incubation", P["incubation"]),
           ("fa-laptop", "Corporate Technology Services", P["corporate"]), ("fa-layer-group", "Projects-Based Earning", P["centre"]),
           ("fa-coins", "Student Loan Scheme", P["loan"]), ("fa-briefcase", "Placement Department", P["placement"])]
    sk = [(H[5], "E-Commerce<br/>(Dehleze)"), (H[6], "Web<br/>Development"), (H[7], "Graphic<br/>Designing"),
          (H[8], "Video<br/>Editing"), (H[9], "Digital<br/>Marketing"), (H[10], "Freelancing")]
    services = f'''<section class="section wt-sec" id="services" {S("services")}>
  <div class="container">
    <div class="sec-head reveal" style="margin-bottom:26px"><h2 class="lined">Our Professional Services</h2><p>End-to-end support for skill development, project execution and real earning opportunities.</p></div>
    <div class="svc-grid">{"".join(f'<a class="svc reveal d{i % 4}" href="{h}"><i class="fa-solid {ic}"></i>{t}</a>' for i, (ic, t, h) in enumerate(svc))}</div>
    <h2 class="reveal" style="margin:34px 0 18px">Practical Skills, Real Projects, Earning Opportunities.</h2>
    <div class="sk-grid">{"".join(f'<a class="sk reveal d{i % 4}" href="{P["blocks"]}"><img src="{s}" alt="" loading="lazy"/><span>{t} <i class="fa-solid fa-arrow-right"></i></span></a>' for i, (s, t) in enumerate(sk))}</div>
  </div>
</section>'''

    weekend = f'''<section class="section weekend wt-sec" {S("weekend")}>
  <div class="container">
    <div class="wk glass reveal">
      <div class="img"><img src="{H[11]}" alt="Professional learner on a laptop"/></div>
      <div>
        <div class="wk-top"><div><div class="tag">Professional Paid Courses</div><h2>Weekend Professional Training Programs</h2><p>Industry-relevant skills for students, graduates, working professionals and entrepreneurs.</p></div>{btn("Explore Courses", P["courses"], "purple")}</div>
        <div class="wk-feats"><div><i class="fa-solid fa-graduation-cap"></i>Job<br/>Upgradation</div><div><i class="fa-solid fa-briefcase"></i>Business<br/>Advancement</div><div><i class="fa-solid fa-chart-column"></i>Self-Earning<br/>Guidance</div><div><i class="fa-solid fa-hand-holding-dollar"></i>Earning<br/>Opportunities</div><div><i class="fa-solid fa-calendar-week"></i>Weekend<br/>Classes</div></div>
      </div>
    </div>
  </div>
</section>'''

    def story(src, name, prog, text):
        return f'<div class="story"><img src="{src}" alt="{name}"/><div><div class="q">&ldquo;</div><blockquote>{text}</blockquote><b>{name}</b><small>{prog}</small></div></div>'
    a = story(H[12], "Aima Asif", "Web Development", "The hands-on training and project work helped me gain real experience and start my freelancing journey during my studies.")
    b = story(H[13], "Noshaba", "Digital Marketing", "The practical skills and guidance at Wise-Teck gave me the confidence to work on real projects and earn independently.")
    stories = f'''<section class="section stories wt-sec" id="stories" {S("stories")}>
  <div class="container">
    <div class="st-head reveal"><h2>Success Stories From Our Learners</h2><div class="arrows"><button class="arrow-btn" data-st="-1" aria-label="Previous"><i class="fa-solid fa-chevron-left"></i></button><button class="arrow-btn" data-st="1" aria-label="Next"><i class="fa-solid fa-chevron-right"></i></button></div></div>
    <div class="st-track reveal d1"><div class="st-slides" id="stSlides"><div class="st-slide">{a}{b}</div><div class="st-slide">{b}{a}</div></div></div>
    <div class="dots" id="stDots"><button class="on" aria-label="Slide 1"></button><button aria-label="Slide 2"></button></div>
  </div>
</section>'''

    corp = f'''<section class="section corp wt-sec" id="partners" {S("corp")}>
  <div class="container corp-grid">
    <div class="reveal"><h2>Corporate &amp; Industry Collaborations</h2><p>We work with leading industry partners to provide real projects, internships and earning opportunities for our students and graduates.</p>{btn("Explore Partnerships", P["corporate"])}</div>
    <div class="ph reveal d2"><img src="{H[14]}" alt="Corporate collaboration meeting"/></div>
  </div>
</section>'''

    collab = f'''<section class="section wt-sec collab-strip" {S("collab")} style="text-align:center">
  <div class="container">
    <h2 class="reveal" style="margin-bottom:18px">Trusted Industry Collaborators</h2>
    <div class="collab-row">
      <div class="pcard reveal"><span class="lg"><span class="psdf"><span class="box">PSDF</span><small>PUNJAB SKILLS<br/>DEVELOPMENT<br/>FUND</small></span></span><div><b>Punjab Skills Development Fund</b><small>Industry Collaborator</small></div></div>
      <div class="pcard reveal d1"><span class="lg"><span class="nic"><span class="n">Ni</span><span class="c">C</span><span class="l">Lahore</span></span></span><div><b>National Incubation Center Lahore</b><small>Industry Collaborator</small></div></div>
      <a class="pcard cta reveal d2" href="{P["contact"]}"><span class="lg"><i class="fa-solid fa-handshake"></i></span><div><b>Partner With Wise-Teck</b><small>Become a partner &rarr;</small></div></a>
    </div>
  </div>
</section>'''

    # section background motifs (lavender / violet, faint, behind the content) - tools/motifs.py
    def _m(sec, kind):
        return sec.replace('<div class="container', motif(kind) + '<div class="container', 1)
    eco, programs, services, stories, collab = (_m(eco, "eco"), _m(programs, "programs"), _m(services, "services"),
                                                _m(stories, "stories"), _m(collab, "collab"))
    parts = [about, eco, programs, services, weekend, stories, corp, collab]
    # like the reference: soft silk dividers only between the first four section pairs
    # (About|Ecosystem, Ecosystem|Programs, Programs|Services, Services|Weekend); the lower group
    # (Weekend, Stories, Corporate, Collaborators) is divided by spacing alone.
    body = "\n".join(x + ("\n" + wave_div() if i < 4 else "") for i, x in enumerate(parts))
    return page("home", "Wise-Teck | Turning Professional Skills into Self-Earning",
                "Wise-Teck, a project of WISE Education Society — Transforming Learning into Earning through Technology, Innovation and Entrepreneurship.",
                hero, body, home=True)


# =====================================================================================  ABOUT
def about():
    hero = page_hero("about", [HOME_CRUMB, ("About Wise-Teck", "")], "INTRODUCTION WISE-TECK",
                     'Bridging Education, Industry &amp; <span class="accent">Self-Earning</span>',
                     "Transforming Learning into Earning through Technology, Innovation and Entrepreneurship.",
                     btn("Our Objectives", "#objectives", "navy") + '<a class="btn btn-ghost" href="#ecosystem"><span class="play"><i class="fa-solid fa-diagram-project"></i></span>Wise Eco System</a>',
                     photo(img("02", 0) or img("01", 0), "Wise-Teck Earning Centre", ("fa-certificate", "Registered with Registrar Firms, Lahore")),
                     facts=[("fa-building-columns", "A project of Wise Education Society")])
    intro = blk(split(
        '<span class="kicker left">Who We Are</span><h2>A Skills, Incubation &amp; <span class="accent">Earning Platform</span></h2>'
        "<p>Wise-Teck, a project of Wise Education Society, is a professional skills development, business incubation, and earning platform dedicated to transforming knowledge and skills into practical economic opportunities.</p>"
        "<p>Operating through an integrated education-to-earning ecosystem, Wise-Teck connects students with industry professionals, real-world projects, corporate services, and entrepreneurial opportunities.</p>"
        "<p>Its core focus is to develop a skilled workforce, support emerging entrepreneurs, and enable individuals to build sustainable careers through employment, freelancing, and independent businesses.</p>",
        quote('Turning Students into <span class="accent">Self-Earning</span> Individuals.', "Wise-Teck", "A project of Wise Education Society", "fa-rocket")),
        div=("about", "b"))
    vision = blk(split(media(img("01", 14), "Students and professionals collaborating"),
                       '<span class="kicker left">Our Vision</span><h2>Education That Goes <span class="accent">Beyond Degrees</span></h2>'
                       "<p>To create a future where education goes beyond degrees, equipping every student with professional skills and the confidence to become self-earning member of the society.</p>"
                       + btn("Explore the Earning Centre", P["centre"], "purple"), rev=False), "tight")
    obj = [("fa-screwdriver-wrench", "Skills Training", "Provide students with professional and technical skills needed in today's job market.", ("Earning Blocks", P["blocks"])),
           ("fa-chart-line", "Self-Earning", "Help students use their skills to earn money through real projects, freelancing, jobs, and businesses.", ("Earning Centre", P["centre"])),
           ("fa-coins", "Student Loan Support", "Help eligible students get loans to start their own businesses.", ("Student Loan Scheme", P["loan"])),
           ("fa-briefcase", "Job Placement", "Help students and graduates find jobs, internships, and earning opportunities.", ("Placement", P["placement"])),
           ("fa-laptop-code", "Corporate Services", "Provide IT, software development, digital marketing, and other technology services to companies and businesses.", ("Corporate Services", P["corporate"])),
           ("fa-rocket", "Business Incubation Centre", "Help students turn their business ideas into real businesses through guidance and support.", ("Incubation Centre", P["incubation"])),
           ("fa-handshake", "Industry Partnerships", "Build connections with companies, software houses, and industry experts to create more work and earning opportunities for students.", ("Partnerships", P["corporate"])),
           ("fa-layer-group", "Professional Paid Courses", "Offer paid courses to help students, graduates, and working professionals learn new skills, improve their jobs, and grow their careers.", ("Paid Courses", P["courses"]))]
    objectives = blk(sec_head("Our Core Objectives", 'Eight Objectives, <span class="accent">One Goal</span>') + cards(obj, 4, True), sid="objectives", div=("eco", "b"))
    eco = blk(sec_head("Wise Eco System", 'Programs Working Under <span class="accent">Wise-Teck</span>',
                       "Wise-Teck brings together three educational and training programs. Each program provides different education and training opportunities, while Wise-Teck helps students develop professional skills for their future careers and earning opportunities.")
              + pstrip(), sid="ecosystem", div=("prog", "b"))
    body = intro + vision + objectives + eco + pathway_block() + cta("Join Wise-Teck", "Start Your Journey to Self-Earning", "Learn professional skills, work on real projects and explore earning opportunities.", ("Apply Now", P["contact"]), ("Explore Programs", P["home"] + "#programs"))
    return page("about", "About Wise-Teck | Bridging Education, Industry & Self-Earning", "About Wise-Teck — vision, core objectives and the Wise eco system.", hero, body)


# =====================================================================================  PROGRAM PAGES
def program_page(key, title_html, eyebrow, lead, facts, photo_src, photo_alt, badge, overview_title, overview, cards_title, card_items, extra="", cols=4):
    hero = page_hero(key, [HOME_CRUMB, ("Programs", P["home"] + "#programs"), (eyebrow.title(), "")], eyebrow, title_html, lead,
                     btn("Apply Now", P["contact"], "navy") + f'<a class="btn btn-ghost" href="#overview"><span class="play"><i class="fa-solid fa-arrow-down"></i></span>Learn More</a>',
                     photo(photo_src, photo_alt, badge), facts=facts)
    ov = blk(split(f'<span class="kicker left">Program Overview</span><h2>{overview_title}</h2>' + overview,
                   checklist("Program at a Glance", [t for _, t in facts])), sid="overview", div=("about", "b"))
    cd = blk(sec_head("What Students Receive", cards_title) + cards(card_items, cols), div=("eco", "b"))
    note = "After completing their skills training, students move to the <b>Wise-Teck Earning Centre</b>, where they work on practical projects and explore earning opportunities."
    return hero, ov + cd + extra + pathway_block(note) + programs_block(key, "Explore All Three WISE Programs")


def hub():
    hero, body = program_page(
        "hub", 'Wise <span class="accent">Support Hub</span>', "WISE SUPPORT HUB",
        "Fully funded intermediate (ICS) education for orphaned and underprivileged girls, with free professional skills training up to self-earning.",
        [("fa-hand-holding-heart", "Fully Funded Educational &amp; Skills Training Program"), ("fa-school", "Intermediate Level"), ("fa-certificate", "Affiliated with BISE")],
        img("03", 0) or img("01", 1), "Students in the computer lab", ("fa-heart", "Free education, lunch, transport &amp; skills training"),
        'A Better, <span class="accent">Financially Independent</span> Future',
        "<p>Wise Support Hub provides fully funded intermediate (ICS) education for orphaned and underprivileged girls, along with free education, free daily lunch, free transport, and free professional skills training up to self-earning, helping students build a better and financially independent future during studies.</p>",
        'Everything Provided <span class="accent">Free of Cost</span>',
        [("fa-book-open", "Free Education", "Fully funded intermediate (ICS) education, affiliated with the Board of Intermediate and Secondary Education (BISE)."),
         ("fa-utensils", "Free Daily Lunch", "A free daily lunch for every student."),
         ("fa-bus", "Free Transport", "Free transport so students can attend every day."),
         ("fa-laptop-code", "Free Skills Training", "Free professional skills training up to self-earning, during studies.")])
    body += cta("Wise Support Hub", "Help Build a Financially Independent Future", "Fully funded education and skills training for orphaned and underprivileged girls.", ("Contact Admissions", P["contact"]), ("Earning Centre", P["centre"]))
    return page("hub", "Wise Support Hub | Wise-Teck", "Fully funded intermediate (ICS) education and skills training for orphaned and underprivileged girls.", hero, body)


def college():
    hero, body = program_page(
        "college", 'Wise <span class="accent">College</span>', "WISE COLLEGE",
        "ADP and BS degree programs with professional skills training up to self-earning — affiliated with the University of the Punjab.",
        [("fa-graduation-cap", "Higher Education with Professional Skills"), ("fa-award", "Degree Level Program"), ("fa-building-columns", "Affiliated with University of the Punjab (PU)")],
        img("04", 0) or img("01", 2), "Students in a lecture hall", ("fa-user-graduate", "MPhil/PhD faculty &amp; digital classrooms"),
        'Degrees That Lead to <span class="accent">Earning</span>',
        "<p>Wise College offers ADP and BS degree programs in Artificial Intelligence, E-Commerce, Software Engineering, and Data Science, supported by experienced MPhil/PhD faculty, digital classrooms, and professional skills training up to self-earning, enabling students to develop practical skills and explore earning opportunities during their studies.</p>",
        'ADP &amp; BS <span class="accent">Degree Programs</span>',
        [("fa-brain", "Artificial Intelligence", "ADP and BS degree program in Artificial Intelligence."),
         ("fa-cart-shopping", "E-Commerce", "ADP and BS degree program in E-Commerce."),
         ("fa-code", "Software Engineering", "ADP and BS degree program in Software Engineering."),
         ("fa-chart-pie", "Data Science", "ADP and BS degree program in Data Science.")],
        extra=blk(sec_head("Why Wise College", 'Learning <span class="accent">Supported By</span>') + cards([
            ("fa-user-tie", "Experienced Faculty", "Experienced MPhil/PhD faculty."),
            ("fa-chalkboard", "Digital Classrooms", "Modern digital classrooms."),
            ("fa-chart-line", "Skills up to Self-Earning", "Professional skills training up to self-earning, enabling students to explore earning opportunities during their studies.")]), "tight"))
    body += cta("Wise College", "Earn a Degree, Build Real Skills", "ADP and BS programs in AI, E-Commerce, Software Engineering and Data Science.", ("Apply Now", P["contact"]), ("Earning Centre", P["centre"]))
    return page("college", "Wise College Degree Programs | Wise-Teck", "ADP and BS degree programs affiliated with the University of the Punjab.", hero, body)


def courses():
    feats = [("fa-graduation-cap", "Job Upgradation", "Improve your current job with new professional skills."),
             ("fa-briefcase", "Business Advancement", "Skills that help grow your business."),
             ("fa-chart-column", "Self-Earning Guidance", "Guidance to start earning with your skills."),
             ("fa-hand-holding-dollar", "Earning Opportunities", "Access to Wise-Teck earning opportunities."),
             ("fa-calendar-week", "Weekend Classes", "Weekend classes that fit around work and study.")]
    hero, body = program_page(
        "courses", 'Professional <span class="accent">Paid Courses</span>', "PROFESSIONAL PAID COURSES",
        "Paid courses to help students, graduates, and working professionals learn new skills, improve their jobs, and grow their careers.",
        [("fa-briefcase", "Industry-Relevant Skills"), ("fa-calendar-week", "Weekend Classes"), ("fa-door-open", "Open for All")],
        img("01", 11), "Professional learner on a laptop", ("fa-calendar-week", "Weekend Professional Training Programs"),
        'Weekend Professional <span class="accent">Training Programs</span>',
        "<p>Wise-Teck offers paid courses to help students, graduates, and working professionals learn new skills, improve their jobs, and grow their careers.</p><p>Industry-relevant skills for students, graduates, working professionals and entrepreneurs.</p>",
        'Why Take a <span class="accent">Paid Course</span>', feats[:4],
        extra=blk(placeholder("Course List, Fees &amp; Timings", "Add each course with its duration, fee, weekend schedule and next start date — to be supplied by Wise-Teck.") , "tight"))
    body += cta("Professional Paid Courses", "Upgrade Your Skills This Weekend", "Industry-relevant weekend classes, open for all.", ("Enquire Now", P["contact"]), ("Earning Centre", P["centre"]))
    return page("courses", "Professional Paid Courses | Wise-Teck", "Weekend professional training programs for students, graduates and working professionals.", hero, body)


# =====================================================================================  EARNING CENTRE
def centre():
    hero = page_hero("centre", [HOME_CRUMB, ("Wise-Teck Earning Centre", "")], "WISE-TECK EARNING CENTRE",
                     'From Professional Skills to <span class="accent">Self-Earning</span>',
                     "The final stage of Wise Education Society's education-to-earning model.",
                     btn("Our Earning Blocks", P["blocks"], "navy") + '<a class="btn btn-ghost" href="#pathway"><span class="play"><i class="fa-solid fa-route"></i></span>Earning Pathway</a>',
                     photo(img("07", 0) or img("01", 0), "Students working in the Earning Centre", ("fa-chart-line", "Freelancing, employment &amp; own business")))
    about_c = blk(split('<span class="kicker left">About Earning Centre</span><h2>Where Skills <span class="accent">Start Earning</span></h2>'
                        "<p>Wise-Teck Earning Centre is the final stage of Wise Education Society's education-to-earning model.</p>"
                        "<p>Students from all three WISE programs — Wise Support Hub, Wise College Degree Programs, and Professional Paid Courses — receive professional skills training through Wise-Teck during or after their studies.</p>"
                        "<p>After developing their skills, students move to the Wise-Teck Earning Centre, where they work on real-world projects, gain practical experience, and receive guidance to start earning.</p>"
                        "<p>The Earning Centre helps students build their careers through freelancing, employment, and starting their own businesses.</p>",
                        quote('To help students turn their education and professional skills into real earning opportunities and become <span class="accent">financially independent.</span>', "Wise Earning Centre Outcome", "Our goal for every student", "fa-bullseye")),
                  div=("about", "b"))
    provide = blk(sec_head("What We Provide", 'Support at Every <span class="accent">Step</span>') + cards([
        ("fa-diagram-project", "Real-World Projects", "Practical experience through real-world projects"),
        ("fa-user-tie", "Professional Guidance", "Guidance from experienced professionals"),
        ("fa-laptop-house", "Freelancing &amp; Client Work", "Freelancing and client work opportunities"),
        ("fa-briefcase", "Job &amp; Career Support", "Job and career support", ("Placement", P["placement"])),
        ("fa-rocket", "Business Startup Mentorship", "Business startup guidance and mentorship", ("Incubation Centre", P["incubation"])),
        ("fa-handshake", "Industry Networking", "Industry connections and professional networking")], 3, True), div=("eco", "b"))
    body = about_c + provide + blk(sec_head("Our Earning Pathway", 'From Education to <span class="accent">Self-Earning</span>') + steps(PATHWAY), sid="pathway") \
        + programs_block() + cta("Earning Blocks", "Different Skills. Different Opportunities.", "One Goal: Self-Earning. Explore the earning blocks at the Wise-Teck Earning Centre.", ("Our Earning Blocks", P["blocks"]), ("Apply Now", P["contact"]))
    return page("centre", "Wise-Teck Earning Centre | From Skills to Self-Earning", "Wise-Teck Earning Centre — practical projects, guidance and earning opportunities.", hero, body)


def blocks():
    hero = page_hero("blocks", [HOME_CRUMB, ("Earning Centre", P["centre"]), ("Our Earning Blocks", "")], "OUR EARNING BLOCKS",
                     'Different Skills. Different Opportunities. <span class="accent">One Goal: Self-Earning.</span>',
                     "Wise-Teck Earning Centre has different earning blocks where students use their skills to work on real projects and explore earning opportunities.",
                     btn("Explore Blocks", "#blocks", "navy") + '<a class="btn btn-ghost" href="#how"><span class="play"><i class="fa-solid fa-gears"></i></span>How It Works</a>',
                     orb("fa-cubes", [("fa-code", "Software &amp; Web"), ("fa-cart-shopping", "E-Commerce &amp; Dehleze"), ("fa-pen-nib", "Digital &amp; Creative"), ("fa-laptop-house", "Freelancing"), ("fa-brain", "AI &amp; Data"), ("fa-rocket", "Entrepreneurship")]))
    B = [(img("06", 0), "Software &amp; Web Development", "Students develop websites, software, and online solutions for businesses and clients."),
         (img("06", 2), "E-Commerce &amp; Dehleze", "Students learn online selling, product management, and order handling through Dehleze, Wise-Teck's multi-vendor e-commerce platform."),
         (img("06", 3), "Digital Marketing &amp; Creative Services", "Students work on graphic design, video editing, social media management, content creation, and digital marketing projects."),
         (img("06", 5), "Freelancing &amp; Remote Services", "Students learn how to find online clients, create freelance profiles, write proposals, and complete projects."),
         (img("06", 4), "AI, Data Analytics &amp; Business Solutions", "Students use AI, Power BI, data analysis, and other digital tools to work on business projects."),
         (img("10", 0) or img("04", 6), "Entrepreneurship &amp; Business Incubation", "Students receive guidance to develop business ideas, start small businesses, and create their own earning opportunities.")]
    cardsh = "".join(f'<article class="blockc reveal d{i % 3}"><div class="ph"><img src="{s}" alt="" loading="lazy"/><span class="n"><b>{i + 1:02d}</b>EARNING BLOCK</span></div><div class="bd"><h3>{t}</h3><p>{d}</p></div></article>' for i, (s, t, d) in enumerate(B))
    body = blk(sec_head("Six Earning Blocks", 'Choose Your <span class="accent">Earning Block</span>', "Students join an earning block according to their skills and interests.") + f'<div class="blocks">{cardsh}</div>', sid="blocks", div=("about", "b")) \
        + blk(sec_head("How Earning Blocks Work", 'From Skills to <span class="accent">Self-Earning</span>', "Skills Development &rarr; Earning Block Selection &rarr; Practical Projects &rarr; Client Work &rarr; Self-Earning") + steps(BLOCK_STEPS)
              + '<p class="glass note reveal">Students join an earning block according to their <b>skills and interests</b>.</p>', sid="how", div=("eco", "b")) \
        + cta("Wise-Teck Earning Centre", "Ready to Start Earning?", "Pick the earning block that matches your skills and interests.", ("Apply Now", P["contact"]), ("About the Earning Centre", P["centre"]))
    return page("blocks", "Our Earning Blocks | Wise-Teck", "Six earning blocks at the Wise-Teck Earning Centre.", hero, body)


# =====================================================================================  SERVICES
def service_page(key, crumb, eyebrow, title, lead, visual, body, cta_args):
    hero = page_hero(key, [HOME_CRUMB, ("Services", P["home"] + "#services"), (crumb, "")], eyebrow, title, lead,
                     btn("Get in Touch", P["contact"], "navy") + '<a class="btn btn-ghost" href="#details"><span class="play"><i class="fa-solid fa-arrow-down"></i></span>Learn More</a>', visual)
    return page(key, f"{crumb} | Wise-Teck", lead, hero, body + cta(*cta_args))


def corporate():
    body = blk(split('<span class="kicker left">Corporate Services</span><h2>Technology Services for <span class="accent">Businesses</span></h2>'
                     "<p>Wise-Teck provides IT, software development, digital marketing, and other technology services to companies and businesses.</p>"
                     "<p>Through industry partnerships, Wise-Teck builds connections with companies, software houses, and industry experts to create more work and earning opportunities for students.</p>",
                     media(img("01", 14), "Corporate collaboration meeting")), sid="details", div=("about", "b")) \
        + blk(sec_head("What We Offer", 'Our Corporate <span class="accent">Services</span>') + cards([
            ("fa-server", "IT Services", "IT services for companies and businesses."),
            ("fa-code", "Software Development", "Websites, software, and online solutions for businesses and clients."),
            ("fa-bullhorn", "Digital Marketing", "Digital marketing, social media and creative services."),
            ("fa-microchip", "Other Technology Services", "Other technology services, including AI, data analytics and business solutions.")], 4), div=("eco", "b")) \
        + blk(placeholder("Service Details &amp; Past Clients", "Add service packages, process, industries served and client examples — to be supplied by Wise-Teck."), "tight")
    return service_page("corporate", "Corporate Technology Services", "CORPORATE TECHNOLOGY SERVICES", 'Technology Services, <span class="accent">Delivered</span>',
                        "IT, software development, digital marketing, and other technology services for companies and businesses.",
                        orb("fa-laptop-code", [("fa-server", "IT<br/>Services"), ("fa-code", "Software<br/>Development"), ("fa-bullhorn", "Digital<br/>Marketing"), ("fa-handshake", "Industry<br/>Partnerships")]),
                        body, ("Partner With Us", "Work With Wise-Teck", "Technology services for your business, and real projects for skilled students.", ("Contact Us", P["contact"]), ("Earning Blocks", P["blocks"])))


def incubation():
    body = blk(split('<span class="kicker left">About the Centre</span><h2>Supporting Emerging <span class="accent">Entrepreneurs</span></h2>'
                     "<p>Wise-Teck, a project of Wise Education Society, is a professional skills development, business incubation, and earning platform dedicated to transforming knowledge and skills into practical economic opportunities.</p>"
                     "<p>Its core focus is to develop a skilled workforce, support emerging entrepreneurs, and enable individuals to build sustainable careers through employment, freelancing, and independent businesses.</p>",
                     quote('Transforming Learning into Earning through Technology, Innovation and <span class="accent">Entrepreneurship.</span>', "Wise-Teck", "Turning Students into Self-Earning Individuals.", "fa-rocket")),
               sid="details", div=("about", "b")) \
        + blk(sec_head("How We Support You", 'From Idea to <span class="accent">Your Own Business</span>') + cards([
            ("fa-lightbulb", "Business Idea Development", "Students receive guidance to develop their business ideas."),
            ("fa-user-tie", "Startup Guidance &amp; Mentorship", "Business startup guidance and mentorship to help students start small businesses."),
            ("fa-chalkboard-user", "Guidance from Experienced Professionals", "Wise-Teck connects students with industry professionals, real-world projects and entrepreneurial opportunities."),
            ("fa-handshake", "Industry Connections &amp; Networking", "Connections with companies, software houses, and industry experts to create more work and earning opportunities."),
            ("fa-coins", "Student Loan Support", "Help for eligible students to get loans to start their own businesses.", ("Student Loan Scheme", P["loan"])),
            ("fa-diagram-project", "Practical Projects &amp; Client Work", "Practical experience through real-world projects, freelancing and client work opportunities.")], 3, True), div=("eco", "b")) \
        + blk(sec_head("How It Works", 'Your Path to <span class="accent">Self-Earning</span>') + steps(BLOCK_STEPS)
              + '<p class="glass note reveal"><b>Entrepreneurship &amp; Business Incubation</b> is one of the earning blocks at the Wise-Teck Earning Centre. Students join an earning block according to their skills and interests.</p>') \
        + programs_block(None, "Open to Students from All Three WISE Programs")
    return service_page("incubation", "Business Incubation Centre", "BUSINESS INCUBATION CENTRE", 'Turning Business Ideas into <span class="accent">Real Businesses</span>',
                        "Wise-Teck helps students turn their business ideas into real businesses through guidance and support.",
                        orb("fa-rocket", [("fa-lightbulb", "Business<br/>Ideas"), ("fa-user-tie", "Startup<br/>Mentorship"), ("fa-handshake", "Industry<br/>Networking"), ("fa-coins", "Student Loan<br/>Support")]),
                        body, ("Our Outcome", "Become Financially Independent", "To help students turn their education and professional skills into real earning opportunities and become financially independent.", ("Share Your Business Idea", P["contact"]), ("Student Loan Scheme", P["loan"])))


def loan():
    body = blk(split('<span class="kicker left">Student Loan Support</span><h2>Funding to Start <span class="accent">Your Own Business</span></h2>'
                     "<p>Wise-Teck helps eligible students get loans to start their own businesses.</p>"
                     "<p>Loan support works alongside the Business Incubation Centre, which helps students turn their business ideas into real businesses through guidance and support.</p>"
                     + btn("Business Incubation Centre", P["incubation"], "purple"),
                     media(img("10", 0) or img("04", 6), "Young entrepreneurs working on a business")), sid="details", div=("about", "b")) \
        + blk(sec_head("How It Connects", 'Part of the <span class="accent">Self-Earning</span> Journey') + cards([
            ("fa-lightbulb", "Develop Your Idea", "Students receive guidance to develop business ideas.", ("Incubation Centre", P["incubation"])),
            ("fa-coins", "Get Loan Support", "Eligible students get help to obtain loans to start their own businesses."),
            ("fa-store", "Start Your Business", "Start small businesses and create your own earning opportunities.")]), div=("eco", "b")) \
        + blk(placeholder("Eligibility, Loan Amounts &amp; Application Process", "Add who is eligible, loan limits, partner institutions, required documents and the step-by-step application process — to be supplied by Wise-Teck."), "tight")
    return service_page("loan", "Student Loan Scheme", "STUDENT LOAN SCHEME", 'Student Loan <span class="accent">Support</span>',
                        "Helping eligible students get loans to start their own businesses.",
                        photo(img("10", 0) or img("04", 6), "Young entrepreneurs", ("fa-coins", "For eligible students")),
                        body, ("Student Loan Scheme", "Have a Business Idea?", "Talk to us about loan support and the Business Incubation Centre.", ("Contact Us", P["contact"]), ("Incubation Centre", P["incubation"])))


def placement():
    hero = page_hero("placement", [HOME_CRUMB, ("Placement", "")], "JOB PLACEMENT", 'Jobs, Internships &amp; <span class="accent">Earning Opportunities</span>',
                     "Helping students and graduates find jobs, internships, and earning opportunities.",
                     btn("Get Career Support", P["contact"], "navy") + '<a class="btn btn-ghost" href="#details"><span class="play"><i class="fa-solid fa-arrow-down"></i></span>Learn More</a>',
                     photo(img("08", 1) or img("01", 14), "Graduate at work", ("fa-briefcase", "Job and career support")))
    body = blk(split('<span class="kicker left">Placement Department</span><h2>From Skills to <span class="accent">Careers</span></h2>'
                     "<p>Wise-Teck helps students and graduates find jobs, internships, and earning opportunities.</p>"
                     "<p>Through industry partnerships, Wise-Teck builds connections with companies, software houses, and industry experts to create more work and earning opportunities for students.</p>",
                     checklist("Career Support Includes", ["Job and career support", "Internship opportunities", "Industry connections and professional networking", "Freelancing and client work opportunities", "Guidance from experienced professionals"])),
               sid="details", div=("about", "b")) \
        + blk(sec_head("Career Pathways", 'Three Ways to <span class="accent">Earn</span>', "The Earning Centre helps students build their careers through freelancing, employment, and starting their own businesses.") + cards([
            ("fa-briefcase", "Employment", "Find jobs and internships with industry partners."),
            ("fa-laptop-house", "Freelancing", "Find online clients, create freelance profiles, write proposals, and complete projects.", ("Earning Blocks", P["blocks"])),
            ("fa-rocket", "Own Business", "Start small businesses and create your own earning opportunities.", ("Incubation Centre", P["incubation"]))]), div=("eco", "b")) \
        + blk(placeholder("Hiring Partners &amp; Placement Process", "Add hiring partners, placement process and results — to be supplied by Wise-Teck."), "tight") \
        + cta("Placement Department", "Ready for Your Next Step?", "Get help finding jobs, internships and earning opportunities.", ("Contact Placement", P["contact"]), ("Earning Centre", P["centre"]))
    return page("placement", "Job Placement & Career Services | Wise-Teck", "Helping students and graduates find jobs, internships, and earning opportunities.", hero, body)


def stories():
    hero = page_hero("stories", [HOME_CRUMB, ("About", P["about"]), ("Success Stories", "")], "SUCCESS STORIES", 'Stories From Our <span class="accent">Learners</span>',
                     "Students who turned professional skills into real earning opportunities.",
                     btn("Start Your Story", P["contact"], "navy"), orb(None, [("fa-laptop-code", "Web<br/>Development"), ("fa-bullhorn", "Digital<br/>Marketing"), ("fa-laptop-house", "Freelancing"), ("fa-chart-line", "Self-Earning")]))

    def story(src, name, prog, text):
        return f'<div class="story reveal"><img src="{src}" alt="{name}"/><div><div class="q">&ldquo;</div><blockquote>{text}</blockquote><b>{name}</b><small>{prog}</small></div></div>'
    body = blk(sec_head("Success Stories", 'Real Skills, <span class="accent">Real Earning</span>') + '<div class="tgrid">'
               + story(img("01", 12), "Aima Asif", "Web Development", "The hands-on training and project work helped me gain real experience and start my freelancing journey during my studies.")
               + story(img("01", 13), "Noshaba", "Digital Marketing", "The practical skills and guidance at Wise-Teck gave me the confidence to work on real projects and earn independently.")
               + "</div>", div=("about", "b")) \
        + blk(placeholder("More Success Stories", "Add more learner stories (name, program, earning result, photo) — to be supplied by Wise-Teck."), "tight") \
        + cta("Your Turn", "Write Your Own Success Story", "Learn professional skills and start earning through the Wise-Teck Earning Centre.", ("Apply Now", P["contact"]), ("Explore Programs", P["home"] + "#programs"))
    return page("stories", "Success Stories | Wise-Teck", "Success stories from Wise-Teck learners.", hero, body)


def contact():
    hero = page_hero("contact", [HOME_CRUMB, ("Contact", "")], "CONTACT &amp; ADMISSIONS", 'Let&rsquo;s Start Your <span class="accent">Journey</span>',
                     "Questions about programs, courses, services or partnerships? Get in touch with Wise-Teck.",
                     btn("Call +92 300 8410868", "tel:+923008410868", "navy", "fa-phone"),
                     photo(img("02", 0) or img("01", 0), "Wise-Teck Earning Centre, 48-Main Gulberg, Lahore", ("fa-location-dot", "48-Main Gulberg, Lahore")))
    opts = "".join(f"<option>{t}</option>" for t in ["Wise Support Hub", "Wise College", "Professional Paid Courses", "Earning Centre", "Business Incubation", "Student Loan Scheme", "Corporate Services", "Placement", "Partnership", "Other"])
    body = blk(f'''<div class="contact-grid">
      <div class="cinfo">
        <div class="ci reveal"><span><i class="fa-solid fa-phone"></i></span><div><b>Phone</b><a href="tel:+923008410868">+92 300 8410868</a></div></div>
        <div class="ci reveal d1"><span><i class="fa-solid fa-envelope"></i></span><div><b>Email</b><a href="mailto:info@wise-teck.org">info@wise-teck.org</a></div></div>
        <div class="ci reveal d2"><span><i class="fa-solid fa-location-dot"></i></span><div><b>Address</b><p>48-Main Gulberg, Lahore</p></div></div>
        <div class="ci reveal d3"><span><i class="fa-solid fa-building-columns"></i></span><div><b>Wise-Teck</b><p>A project of Wise Education Society &middot; Registered with Registrar Firms, Lahore</p></div></div>
      </div>
      <form class="glass form reveal d1" onsubmit="event.preventDefault();this.querySelector('.btn').innerHTML='Thank you &mdash; we will contact you soon';">
        <h3>Send Us a Message</h3>
        <label>Full Name<input required placeholder="Your name"/></label>
        <label>Phone<input required placeholder="+92 ..."/></label>
        <label class="full">Email<input type="email" placeholder="you@example.com"/></label>
        <label class="full">I&rsquo;m interested in<select>{opts}</select></label>
        <label class="full">Message<textarea placeholder="How can we help?"></textarea></label>
        <button class="btn btn-gold" type="submit">Send Message <i class="fa-solid fa-paper-plane"></i></button>
      </form>
    </div>''', sid="details", div=("about", "b")) + '<div style="height:90px"></div>'
    return page("contact", "Contact & Admissions | Wise-Teck", "Contact Wise-Teck — phone, email and address.", hero, body)


BUILDERS = {"home": home, "about": about, "hub": hub, "college": college, "courses": courses,
            "centre": centre, "blocks": blocks, "corporate": corporate, "incubation": incubation, "loan": loan,
            "placement": placement, "stories": stories, "contact": contact}


def main():
    for key, fn in BUILDERS.items():
        html = fn()
        (ROOT / P[key]).write_text(html, encoding="utf-8")
        print(f"{P[key]:32s} {len(html) // 1024:4d} KB")


if __name__ == "__main__":
    main()
