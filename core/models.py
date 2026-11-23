"""Every word, link and picture on the Wise-Teck v3 site lives in these tables and is editable in /admin/.

    Page -> Section (one block of the page, drawn by its layout template) -> Item (cards, steps, tags, stats ...)

Shared content: SiteSettings (logo, contact details, footer text), NavItem (menu), FooterColumn/FooterLink,
Program (the three-program strip used on many pages), SuccessStory, BlogPost, TeamMember, Service, Course.
Section extras: Detail (label + value rows an editor adds to a section, shown as a small table).
Inbox: ContactMessage (the contact form).

Text conventions used by the templates (see core/templatetags/wt.py):
  * Titles: "Words in the title to colour" (highlight) turns those words gold/violet.
  * Short labels (titles of tags / features): a "|" makes a line break, e.g. "Skills|Development".
  * Long text: a blank line starts a new paragraph, **double stars** make text bold.
"""

import re

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.functional import cached_property

from . import theme

ICON_HELP = "Font Awesome icon name, e.g. fa-users or fa-graduation-cap (see fontawesome.com/icons, free solid set)."
BUTTON_STYLES = [
    ("gold", "Gold"),
    ("navy", "Navy"),
    ("purple", "Purple"),
    ("ghost", "Ghost (round icon + text)"),
    ("outline-light", "Outline (on dark)"),
]


def image_src(file_field, url=""):
    """URL of an uploaded image, else the pasted link, else ''."""
    try:
        if file_field:
            return file_field.url
    except ValueError:
        pass
    return url or ""


def safe_svg(upload):
    """Refuse SVG files that carry scripts or event handlers (an SVG opened on its own runs them)."""
    if not upload.name.lower().endswith(".svg"):
        return
    upload.seek(0)
    text = upload.read().decode("utf8", "ignore").lower()
    upload.seek(0)
    if "<script" in text or "javascript:" in text or re.search(r"\son[a-z]+\s*=", text) or "<foreignobject" in text:
        raise ValidationError("This SVG contains scripts. Export it again as a plain drawing, or upload a PNG.")


# ---------------------------------------------------------------------------------------------- site-wide
class SiteSettings(models.Model):
    site_name = models.CharField(
        "Site name",
        max_length=80,
        default="WISE-TECK",
        help_text="Read out for the logo by screen readers; also used by search engines.",
    )
    logo = models.ImageField(
        "Round logo",
        upload_to="site/",
        blank=True,
        help_text="Optional. Leave empty to use the built-in round Wise-Teck logo.",
    )
    favicon = models.ImageField(
        "Browser tab icon", upload_to="site/", blank=True, help_text="Optional. Leave empty to use the built-in icon."
    )
    topbar_text = models.CharField("Top bar text", max_length=160, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    email = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=200, blank=True)
    registration = models.CharField("Registration line", max_length=200, blank=True)
    apply_label = models.CharField("Header button text", max_length=40, default="Apply Now")
    apply_url = models.CharField("Header button link", max_length=300, default="/contact/")
    footer_text = models.TextField("Footer tagline", blank=True)
    footer_contact_title = models.CharField(
        "Footer contact heading",
        max_length=60,
        blank=True,
        help_text="Optional heading above the phone / email / address in the footer.",
    )
    facebook = models.CharField(max_length=300, blank=True, default="#")
    instagram = models.CharField(max_length=300, blank=True, default="#")
    linkedin = models.CharField(max_length=300, blank=True, default="#")
    youtube = models.CharField(max_length=300, blank=True, default="#")
    copyright = models.CharField(
        "Copyright line", max_length=200, blank=True, help_text="Optional line at the very bottom of the footer."
    )
    meta_description = models.CharField("Default SEO description", max_length=300, blank=True)
    # search engines
    site_url = models.CharField(
        "Main web address",
        max_length=200,
        blank=True,
        help_text="e.g. https://wiseteck.dev — used for canonical links, the sitemap and sharing. "
        "Empty = the address the visitor used.",
    )
    seo_name = models.CharField("Organisation name (search engines)", max_length=120, default="Wise-Teck")
    seo_suffix = models.CharField(
        "Added after page titles",
        max_length=60,
        blank=True,
        help_text="Optional, e.g. ' | Wise-Teck'. Leave empty when page titles already include it.",
    )
    share_image = models.ImageField(
        "Default sharing image",
        upload_to="site/",
        blank=True,
        help_text="Shown when a page is shared on WhatsApp, Facebook, LinkedIn or X and the page "
        "has no image of its own. Best size 1200 × 630.",
    )
    city = models.CharField(max_length=80, blank=True, default="Lahore")
    country_code = models.CharField(
        "Country code", max_length=2, blank=True, default="PK", help_text="Two letters, e.g. PK."
    )
    google_verification = models.CharField(
        "Google Search Console code",
        max_length=120,
        blank=True,
        help_text='Only the content="…" value of Google\'s verification meta tag.',
    )
    robots_extra = models.TextField(
        "Extra robots.txt rules",
        blank=True,
        help_text="Optional lines added to robots.txt. The admin, previews and the sitemap link are handled "
        "automatically.",
    )
    coin_base_color = models.CharField(
        "3D coin base colour",
        max_length=7,
        blank=True,
        help_text="Optional, e.g. #ffffff. Empty = the design's default.",
    )
    coin_ring_color = models.CharField("3D coin ring colour (lower)", max_length=7, blank=True)
    coin_ring2_color = models.CharField("3D coin ring colour (upper)", max_length=7, blank=True)
    # colour scheme (see core/theme.py): every colour on the site follows these three
    color_scheme = models.CharField(
        "Colour scheme",
        max_length=20,
        blank=True,
        default="",
        choices=theme.CHOICES,
        help_text="Every colour on the website follows the scheme: buttons, backgrounds, "
        "waves, footer and the 3D coin.",
    )
    color_primary = models.CharField(
        "Primary colour",
        max_length=7,
        blank=True,
        default=theme.DEFAULT["primary"],
        help_text="Buttons, links, highlights and the light page backgrounds.",
    )
    color_accent = models.CharField(
        "Accent colour",
        max_length=7,
        blank=True,
        default=theme.DEFAULT["accent"],
        help_text="The call-to-action buttons (gold by default).",
    )
    color_dark = models.CharField(
        "Dark colour",
        max_length=7,
        blank=True,
        default=theme.DEFAULT["dark"],
        help_text="Top bar, footer and headings.",
    )
    notify_email = models.CharField(
        "Send contact form alerts to",
        max_length=300,
        blank=True,
        help_text="Email address(es) that get an alert for every new message. "
        "Separate several with commas. Leave empty for no alerts.",
    )
    contact_success = models.CharField(
        "Message shown after the form is sent", max_length=300, default="Thank you — we will contact you soon."
    )
    contact_error = models.CharField(
        "Message shown when a field needs fixing", max_length=300, default="Please check the highlighted fields."
    )
    # announcement bar (top of every page)
    announcement = models.CharField(
        "Announcement",
        max_length=200,
        blank=True,
        help_text="Optional thin bar at the very top of every page, e.g. “Admissions open for "
        "the Spring batch”. Leave empty to hide the bar.",
    )
    announcement_label = models.CharField(
        "Announcement link text", max_length=40, blank=True, help_text="Optional, e.g. Apply now."
    )
    announcement_url = models.CharField(
        "Announcement link",
        max_length=300,
        blank=True,
        help_text="Optional, e.g. /contact/ or a full https:// address.",
    )
    # page not found (404)
    notfound_title = models.CharField("Title", max_length=120, default="Page Not Found")
    notfound_highlight = models.CharField(
        "Words in the title to colour", max_length=120, blank=True, default="Not Found"
    )
    notfound_text = models.CharField(
        "Text", max_length=300, default="The page you are looking for has moved or no longer exists."
    )
    notfound_button = models.CharField("Button text", max_length=40, default="Back to Home")
    # visitor statistics
    ga_id = models.CharField(
        "Google Analytics ID",
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(r"^G-[A-Z0-9]{4,15}$", "Use the Measurement ID from Google Analytics, e.g. G-AB12CD34EF.")
        ],
        help_text="Optional. Google Analytics → Admin → Data streams → your website → Measurement ID "
        "(starts with G-). Leave empty for no tracking.",
    )
    trend_keywords = models.CharField(
        "Keywords to watch",
        max_length=300,
        blank=True,
        default="IT courses Lahore, freelancing course, digital marketing course",
        help_text="Search terms people use to find you, separated by commas. The dashboard "
        "opens them in Google Trends and Google Search.",
    )

    class Meta:
        verbose_name = verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def phone_link(self):
        return "tel:" + "".join(c for c in self.phone if c.isdigit() or c == "+")

    @property
    def logo_src(self):
        return image_src(self.logo)

    @property
    def favicon_src(self):
        return image_src(self.favicon)

    @property
    def socials(self):
        return [
            (name, url, label, icon)
            for name, url, label, icon in [
                ("facebook", self.facebook, "Facebook", "fa-facebook-f"),
                ("instagram", self.instagram, "Instagram", "fa-instagram"),
                ("linkedin", self.linkedin, "LinkedIn", "fa-linkedin-in"),
                ("youtube", self.youtube, "YouTube", "fa-youtube"),
            ]
            if url and url.strip() not in ("#", "")
        ]


class NavItem(models.Model):
    label = models.CharField(max_length=80)
    url = models.CharField(
        max_length=300, default="#", help_text="e.g. /about/ or /about/#objectives. Use # for a drop-down heading."
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        help_text="Leave empty for a top menu item. Choose a parent to put it in that drop-down.",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("Show", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Menu item"

    def __str__(self):
        return f"{self.parent.label} › {self.label}" if self.parent_id else self.label


class FooterColumn(models.Model):
    title = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    column = models.ForeignKey(FooterColumn, related_name="links", on_delete=models.CASCADE)
    label = models.CharField(max_length=120)
    url = models.CharField(max_length=300, default="#")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


class Program(models.Model):
    """The three WISE programs. Shown as the program strip on many pages ("Programs Working Under Wise-Teck")."""

    title = models.CharField(max_length=120)
    text = models.CharField(max_length=300, blank=True)
    icon = models.CharField(max_length=60, blank=True, help_text=ICON_HELP)
    link_url = models.CharField(
        "Page", max_length=300, help_text="e.g. /wise-support-hub/. The card is highlighted on that page."
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("Show", default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------------------------- pages
class PageQuerySet(models.QuerySet):
    def live(self):
        """Real pages (not drafts)."""
        return self.filter(draft_of__isnull=True)

    def drafts(self):
        return self.filter(draft_of__isnull=False)


class Page(models.Model):
    slug = models.SlugField(unique=True, help_text="Web address. Use 'home' for the homepage.")
    title = models.CharField(
        "Page title (Google + browser tab)",
        max_length=160,
        help_text="Best 50–60 characters. Put the most important words first.",
    )
    meta_description = models.CharField(
        "SEO description",
        max_length=300,
        blank=True,
        help_text="The text under the title in Google results. Best 120–160 characters.",
    )
    share_title = models.CharField(
        "Sharing title",
        max_length=160,
        blank=True,
        help_text="Optional title for WhatsApp / Facebook / LinkedIn / X previews. Empty = page title.",
    )
    share_description = models.CharField(
        "Sharing description", max_length=300, blank=True, help_text="Optional. Empty = SEO description."
    )
    share_image = models.ImageField(
        "Sharing image",
        upload_to="share/",
        blank=True,
        help_text="Shown in link previews. Best 1200 × 630. Empty = the page's main photo, "
        "or the default sharing image in Site Settings.",
    )
    canonical_url = models.CharField(
        "Canonical address (advanced)",
        max_length=300,
        blank=True,
        help_text="Only if this page's content officially lives at another address. Normally empty.",
    )
    noindex = models.BooleanField(
        "Hide from search engines",
        default=False,
        help_text="Keeps the page out of Google and the sitemap (it still opens for visitors).",
    )
    is_active = models.BooleanField("Published", default=True)
    draft_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="drafts",
        on_delete=models.CASCADE,
        help_text="Set when this is a draft copy of a live page.",
    )
    publish_at = models.DateTimeField(
        "Go live at",
        null=True,
        blank=True,
        help_text="When this draft replaces the live page automatically. Leave empty to publish by hand.",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = PageQuerySet.as_manager()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"[Draft] {self.title}" if self.draft_of_id else self.title

    def get_absolute_url(self):
        if self.draft_of_id:
            return f"/preview/page/{self.pk}/"
        return "/" if self.slug == "home" else f"/{self.slug}/"

    @property
    def is_draft(self):
        return self.draft_of_id is not None


class Section(models.Model):
    LAYOUTS = [
        # page tops (drawn above the content, with the menu)
        ("home_hero", "Home · Hero with 3D coin"),
        ("page_hero", "Inner page · Hero banner"),
        # home page blocks
        ("home_about", "Home · About (text + photo)"),
        ("home_ecosystem", "Home · Ecosystem circle + card"),
        ("home_programs", "Home · Program cards + arrow"),
        ("home_services", "Home · Services + skill tiles"),
        ("home_weekend", "Home · Weekend courses banner"),
        ("home_stories", "Home · Success stories slider (from Success Stories)"),
        ("home_partners", "Home · Corporate + collaborators"),
        # general blocks
        ("split", "Text + quote / photo / checklist"),
        ("cards", "Icon cards"),
        ("steps", "Numbered steps (pathway)"),
        ("program_strip", "Three programs strip (from Programs)"),
        ("earning_blocks", "Photo cards (earning blocks)"),
        ("story_grid", "Success stories grid (from Success Stories)"),
        ("placeholder", "Placeholder notice"),
        ("cta", "Call-to-action band"),
        ("contact", "Contact details + form"),
        ("blog_list", "Blog posts (from Blogs)"),
        ("team", "Team members (from Team)"),
        ("services_feed", "Services (from Services)"),
        ("courses", "Courses (from Courses)"),
    ]
    HERO_LAYOUTS = ("home_hero", "page_hero")
    VISUALS = [
        ("", "None"),
        ("photo", "Photo"),
        ("orbit", "3D coin with tags"),
        ("quote", "Quote card"),
        ("checklist", "Checklist panel"),
    ]
    MOTIFS = [
        ("", "None"),
        ("eco", "Circuits"),
        ("programs", "Graduation caps"),
        ("services", "Hexagon network"),
        ("stories", "Quote marks"),
        ("collab", "Skyline + handshake"),
    ]

    page = models.ForeignKey(Page, related_name="sections", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    layout = models.CharField(max_length=30, choices=LAYOUTS)
    anchor = models.SlugField(
        "Anchor id", blank=True, help_text="Lets links jump here, e.g. 'objectives' for /about/#objectives."
    )
    is_active = models.BooleanField("Show", default=True)
    spacing = models.CharField(max_length=10, choices=[("", "Normal"), ("tight", "Tight")], blank=True)
    divider_after = models.CharField(
        "Wave divider after",
        max_length=1,
        blank=True,
        choices=[("", "None"), ("a", "Wave (crest up)"), ("b", "Wave (crest down)")],
    )
    motif = models.CharField("Background drawing", max_length=12, choices=MOTIFS, blank=True)

    # heading
    eyebrow = models.CharField("Small label above the title", max_length=200, blank=True)
    title = models.CharField(max_length=300, blank=True)
    highlight = models.CharField("Words in the title to colour", max_length=200, blank=True)
    lined = models.BooleanField("Line under the title", default=False)
    subtitle = models.TextField("Text under the title", blank=True)
    crumbs = models.TextField(
        "Breadcrumb",
        blank=True,
        help_text="Hero only. One per line: Label | /link/. The last line is this page (no link needed).",
    )
    # text
    body = models.TextField("Text", blank=True, help_text="Blank line = new paragraph. **double stars** = bold.")
    note = models.TextField(
        "Note box", blank=True, help_text="Shown in a glass box under the block. **double stars** = bold."
    )
    list_title = models.CharField(max_length=200, blank=True)
    list_items = models.TextField("List", blank=True, help_text="One item per line.")
    # buttons
    button_label = models.CharField(max_length=80, blank=True)
    button_url = models.CharField(max_length=300, blank=True)
    button_style = models.CharField(max_length=15, choices=BUTTON_STYLES, default="gold")
    button_icon = models.CharField(max_length=60, blank=True, help_text="Optional. " + ICON_HELP + " Default: arrow.")
    button2_label = models.CharField(max_length=80, blank=True)
    button2_url = models.CharField(max_length=300, blank=True)
    button2_style = models.CharField(max_length=15, choices=BUTTON_STYLES, default="ghost")
    button2_icon = models.CharField(max_length=60, blank=True, help_text="Optional. " + ICON_HELP)
    # visual
    visual = models.CharField(
        "Visual",
        max_length=10,
        choices=VISUALS,
        blank=True,
        help_text="Hero: photo or 3D coin. Text block: quote, photo or checklist.",
    )
    image = models.ImageField("Photo", upload_to="sections/", blank=True)
    image_url = models.CharField("…or photo link", max_length=500, blank=True)
    image_alt = models.CharField("Photo description", max_length=200, blank=True)
    image2 = models.ImageField(
        "Second photo",
        upload_to="sections/",
        blank=True,
        help_text="Hero with stats: the smaller photo beside the main one.",
    )
    image2_url = models.CharField("…or second photo link", max_length=500, blank=True)
    image_side = models.CharField(
        "Visual side", max_length=5, choices=[("right", "Right"), ("left", "Left")], default="right"
    )
    badge_icon = models.CharField("Photo badge icon", max_length=60, blank=True, help_text=ICON_HELP)
    badge_text = models.CharField("Photo badge text", max_length=200, blank=True)
    stats_style = models.CharField(
        "Hero stats style",
        max_length=8,
        blank=True,
        choices=[("", "Automatic"), ("number", "Big numbers"), ("text", "Text (smaller)")],
    )
    quote_text = models.TextField("Quote", blank=True)
    quote_highlight = models.CharField("Words in the quote to colour", max_length=200, blank=True)
    quote_author = models.CharField("Quote name", max_length=120, blank=True)
    quote_role = models.CharField("Quote line under the name", max_length=200, blank=True)
    quote_icon = models.CharField("Quote icon", max_length=60, blank=True, help_text=ICON_HELP)
    center_small = models.CharField("Centre label (small)", max_length=80, blank=True)
    center_big = models.CharField("Centre label (big)", max_length=80, blank=True)
    center_url = models.CharField("Centre label link", max_length=300, blank=True)
    # cards / lists
    columns = models.PositiveSmallIntegerField("Cards per row", choices=[(2, "2"), (3, "3"), (4, "4")], default=3)
    numbered = models.BooleanField("Number the cards", default=False)
    item_label = models.CharField(
        "Label on each card",
        max_length=80,
        blank=True,
        help_text="e.g. 'Read More' (link text), 'Step' (step label), 'EARNING BLOCK'.",
    )
    sub_title = models.CharField(
        "Second heading",
        max_length=200,
        blank=True,
        help_text="Heading above the second list (e.g. skill tiles, collaborators).",
    )
    feed_limit = models.PositiveIntegerField(
        "How many to show",
        default=0,
        help_text="Team / Services / home stories: 0 shows all. Blog list and story grid: cards per page "
        "(0 = 9 posts / 8 stories per page).",
    )
    # contact form
    form_title = models.CharField(max_length=120, blank=True)
    form_fields = models.TextField(
        "Form labels",
        blank=True,
        help_text="Five lines: Label | placeholder — for Name, Phone, Email, Interest, Message.",
    )

    class Meta:
        ordering = ["page", "order", "id"]

    def __str__(self):
        return f"{self.page.slug} · {self.order:02d} · {self.title or self.eyebrow or self.get_layout_display()}"

    # ---- helpers used by the templates
    @property
    def is_hero(self):
        return self.layout in self.HERO_LAYOUTS

    def _group(self, g):
        return [i for i in self.items.all() if i.is_active and i.group == g]

    @property
    def main_items(self):
        return self._group("")

    @property
    def second_items(self):
        return self._group("second")

    @property
    def facts(self):
        return self._group("facts")

    @property
    def stats(self):
        return self._group("stats")

    @property
    def tags(self):
        return self._group("tags")

    @property
    def list_lines(self):
        return [line.strip() for line in self.list_items.splitlines() if line.strip()]

    @property
    def crumb_list(self):
        out = []
        for line in self.crumbs.splitlines():
            if line.strip():
                label, _, url = line.partition("|")
                out.append((label.strip(), url.strip()))
        return out

    @property
    def form_labels(self):
        defaults = [
            ("Full Name", "Your name"),
            ("Phone", "+92 ..."),
            ("Email", "you@example.com"),
            ("I’m interested in", ""),
            ("Message", "How can we help?"),
        ]
        lines = [line for line in self.form_fields.splitlines() if line.strip()]
        out = []
        for n, d in enumerate(defaults):
            if n < len(lines):
                label, _, ph = lines[n].partition("|")
                out.append((label.strip(), ph.strip()))
            else:
                out.append(d)
        return out

    @property
    def img(self):
        return image_src(self.image, self.image_url)

    @property
    def img2(self):
        return image_src(self.image2, self.image2_url)

    PAGINATED = {"blog_list": 9, "story_grid": 8}  # list layouts with page numbers: default cards per page

    @property
    def paginated(self):
        return self.layout in self.PAGINATED

    @property
    def per_page(self):
        return self.feed_limit or self.PAGINATED.get(self.layout, 0)

    def feed_queryset(self):
        model = {
            "home_stories": SuccessStory,
            "story_grid": SuccessStory,
            "blog_list": BlogPost,
            "team": TeamMember,
            "services_feed": Service,
            "courses": Course,
        }.get(self.layout)
        if not model:
            return None
        return model.objects.live() if hasattr(model.objects, "live") else model.objects.filter(is_active=True)

    @property
    def feed(self):
        if getattr(self, "page_obj", None) is not None:  # set by the page view for paginated lists
            return list(self.page_obj.object_list)
        qs = self.feed_queryset()
        if qs is None:
            return []
        return list(qs[: self.feed_limit] if self.feed_limit else qs)

    COURSE_FACT_ICONS = (
        "fa-clock",
        "fa-tag",
        "fa-calendar-week",
        "fa-calendar-check",
    )  # duration, fee, schedule, start

    @property
    def course_labels(self):
        """Courses section: the labels on each card, from "List" (one per line), in the order of COURSE_FACT_ICONS."""
        lines = self.list_lines
        defaults = ["Duration", "Fee", "Schedule", "Next start"]
        return [lines[n] if n < len(lines) else label for n, label in enumerate(defaults)]

    @cached_property
    def course_cards(self):
        """Courses section: every shown course with its filled-in facts as (icon, label, value) rows."""
        if self.layout != "courses":
            return []
        cards = []
        for c in self.feed:
            start = date_format(c.next_start, "j M Y") if c.next_start else ""
            values = (c.duration, c.fee, c.schedule, start)
            facts = zip(self.COURSE_FACT_ICONS, self.course_labels, values, strict=True)
            cards.append((c, [(icon, label, value) for icon, label, value in facts if value]))
        return cards

    @property
    def is_empty(self):
        """A list section with nothing to show is left out of the page, together with its wave."""
        return self.layout == "courses" and not self.course_cards

    @property
    def extra_details(self):
        return list(self.details.all())

    @property
    def story_slides(self):
        """Home slider: one slide per story, each showing that story and the next one."""
        s = self.feed
        if len(s) < 2:
            return [s] if s else []
        return [(s[k], s[(k + 1) % len(s)]) for k in range(len(s))]

    @property
    def orbit(self):
        """3D coin tags: six or more = evenly around the ring (hexagon), otherwise the four corner tags."""
        t = self.tags
        if len(t) >= 6:
            return {
                "six": True,
                "spokes": [-90 + 60 * i for i in range(6)],
                "tags": [{"item": x, "angle": -90 + 60 * i, "top": i == 0} for i, x in enumerate(t[:6])],
            }
        return {
            "six": False,
            "spokes": [-90, 0, 90, 180],
            "tags": [{"item": x, "n": i + 1} for i, x in enumerate(t[:4])],
        }

    @property
    def uses_three(self):
        return self.layout == "home_hero" or (self.layout == "page_hero" and self.visual == "orbit")


class Item(models.Model):
    GROUPS = [
        ("", "Main list"),
        ("second", "Second list"),
        ("facts", "Hero facts (chips)"),
        ("stats", "Hero stats (under the photo)"),
        ("tags", "3D coin tags"),
    ]

    section = models.ForeignKey(Section, related_name="items", on_delete=models.CASCADE)
    group = models.CharField("List", max_length=10, choices=GROUPS, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("Show", default=True)
    icon = models.CharField(max_length=60, blank=True, help_text=ICON_HELP)
    title = models.CharField(
        max_length=200, blank=True, help_text='A "|" makes a line break where the design allows it.'
    )
    subtitle = models.CharField(max_length=300, blank=True)
    text = models.TextField(blank=True)
    bullets = models.TextField(blank=True, help_text="One per line.")
    image = models.ImageField(upload_to="items/", blank=True)
    image_url = models.CharField("…or image link", max_length=500, blank=True)
    link_label = models.CharField(max_length=80, blank=True)
    link_url = models.CharField(max_length=300, blank=True)
    logo_html = models.TextField(
        "Logo (HTML, advanced)",
        blank=True,
        help_text="Collaborator cards: the logo markup. Leave empty to use the image or icon.",
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or self.subtitle or f"Item {self.pk}"

    @property
    def bullet_lines(self):
        return [line.strip() for line in self.bullets.splitlines() if line.strip()]

    @property
    def img(self):
        return image_src(self.image, self.image_url)


class Detail(models.Model):
    """Extra details an editor adds to a section without a developer (like a custom field): label + value rows,
    e.g. "Fee | Rs 15,000". Shown as a small table in the layouts built for it (core/layouts.py, details=...)."""

    section = models.ForeignKey(Section, related_name="details", on_delete=models.CASCADE)
    label = models.CharField(max_length=80)
    value = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "extra detail"

    def __str__(self):
        return f"{self.label}: {self.value}"


# ---------------------------------------------------------------------------------------------- inbox
class ContactMessage(models.Model):
    """Messages sent from the Contact page form. Read and mark them in /admin/."""

    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    interest = models.CharField("Interested in", max_length=120, blank=True)
    message = models.TextField(blank=True)
    page = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField("Read", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact message"

    def __str__(self):
        return f"{self.name} <{self.email or self.phone}>"


# ---------------------------------------------------------------------------------------------- content feeds
def unique_slug(obj, text):
    from django.utils.text import slugify

    base = slugify(text)[:200] or "item"
    slug, n = base, 1
    while type(obj).objects.filter(slug=slug).exclude(pk=obj.pk).exists():
        slug, n = f"{base}-{n}", n + 1
    return slug


class LiveQuerySet(models.QuerySet):
    def live(self):
        """Published and past their 'go live at' time."""
        from django.db.models import Q
        from django.utils import timezone

        return self.filter(is_active=True).filter(Q(publish_at__isnull=True) | Q(publish_at__lte=timezone.now()))


GO_LIVE_HELP = "Optional. Keep it hidden until this date and time (it must also be Published)."


class SuccessStory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, unique=True, blank=True, help_text="Web address. Filled in automatically if left empty."
    )
    client_name = models.CharField("Student name", max_length=255, blank=True)
    category = models.CharField(
        "Program / skill", max_length=128, blank=True, help_text="Shown under the name, e.g. Web Development."
    )
    short_description = models.TextField("Quote", blank=True, help_text="Shown on the card in quotation marks.")
    description = models.TextField(
        "Full story", blank=True, help_text="Optional. Blank line = new paragraph. Gives the story its own page."
    )
    image = models.ImageField(upload_to="stories/", blank=True)
    image_url = models.CharField("…or image link", max_length=500, blank=True)
    is_featured = models.BooleanField("Featured", default=False)
    display_order = models.PositiveIntegerField("Order", default=0)
    is_active = models.BooleanField("Published", default=True)
    publish_at = models.DateTimeField("Go live at", null=True, blank=True, help_text=GO_LIVE_HELP)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LiveQuerySet.as_manager()

    class Meta:
        ordering = ["display_order", "-is_featured", "-created_at"]
        verbose_name_plural = "Success stories"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title or self.client_name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/success-stories/{self.slug}/"

    @property
    def img(self):
        return image_src(self.image, self.image_url)


class TeamMember(models.Model):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255, blank=True)
    short_description = models.CharField(max_length=512, blank=True, help_text="Shown on the card.")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="team/", blank=True)
    service = models.CharField("Department", max_length=255, blank=True)
    is_active = models.BooleanField("Show", default=True)
    display_order = models.PositiveIntegerField("Order", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Team member"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and self.display_order == 0:
            last = TeamMember.objects.aggregate(m=models.Max("display_order"))["m"] or 0
            self.display_order = last + 1
        super().save(*args, **kwargs)

    @property
    def img(self):
        return image_src(self.image)


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, unique=True, blank=True, help_text="Web address. Filled in automatically if left empty."
    )
    short_description = models.CharField(
        max_length=512, blank=True, help_text="Shown on the card and in search results."
    )
    content = models.TextField(blank=True, help_text="The article. HTML is allowed (<p>, <h2>, <ul>, <strong> …).")
    featured_image = models.ImageField(upload_to="blog/", blank=True)
    author = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=128, blank=True)
    is_featured = models.BooleanField("Featured", default=False)
    is_active = models.BooleanField("Published", default=True)
    published_at = models.DateTimeField("Date shown on the post", blank=True, null=True)
    publish_at = models.DateTimeField("Go live at", null=True, blank=True, help_text=GO_LIVE_HELP)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LiveQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Blog post"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/blog/{self.slug}/"

    @property
    def img(self):
        return image_src(self.featured_image)


class Service(models.Model):
    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=512, blank=True)
    image = models.ImageField("Photo", upload_to="services/", blank=True)
    icon_file = models.FileField(
        "Icon (SVG or image)",
        upload_to="services/icons/",
        blank=True,
        validators=[FileExtensionValidator(["svg", "png", "jpg", "jpeg", "webp"]), safe_svg],
    )
    icon = models.CharField("…or Font Awesome icon", max_length=60, blank=True, help_text=ICON_HELP)
    link_url = models.CharField("Link", max_length=300, blank=True, help_text="Where the card goes, e.g. /contact/")
    display_order = models.PositiveIntegerField("Order", default=0)
    is_active = models.BooleanField("Show", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    @property
    def img(self):
        return image_src(self.image)


class Course(models.Model):
    """Professional paid courses: one card each in a "Courses" section (the Professional Paid Courses page)."""

    name = models.CharField("Course name", max_length=200)
    short_description = models.CharField("What students learn", max_length=300, blank=True)
    icon = models.CharField(max_length=60, blank=True, help_text=ICON_HELP)
    duration = models.CharField(max_length=80, blank=True, help_text="e.g. 3 months (12 weekends)")
    fee = models.CharField(
        max_length=80, blank=True, help_text="Written as visitors should read it, e.g. Rs 15,000 or Rs 5,000 a month"
    )
    schedule = models.CharField(
        "Weekend schedule", max_length=120, blank=True, help_text="e.g. Saturday & Sunday, 10 am – 1 pm"
    )
    start_date = models.DateField(
        "Next start date", null=True, blank=True, help_text="Hidden on the site once this date has passed."
    )
    link_url = models.CharField(
        "Link", max_length=300, blank=True, help_text="Leave empty to use the section's card link (the enquiry form)."
    )
    display_order = models.PositiveIntegerField("Order", default=0)
    is_active = models.BooleanField("Show", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    @property
    def next_start(self):
        """The start date while it is still ahead (today counts), else None."""
        if self.start_date and self.start_date >= timezone.localdate():
            return self.start_date
        return None


# ---------------------------------------------------------------------------------------------- redirects
class Redirect(models.Model):
    """Old web addresses that should send visitors (and Google) to a new one, so existing links keep working."""

    old_path = models.CharField(
        "Old address",
        max_length=300,
        unique=True,
        help_text="The path only, starting with /, e.g. /about.html or /explore-ecosystem/",
    )
    new_path = models.CharField("New address", max_length=300, help_text="e.g. /about/ or a full https:// link")
    permanent = models.BooleanField(
        "Permanent (301)",
        default=True,
        help_text="Keep ticked for moved pages; Google then moves the old address's ranking to the new one.",
    )
    is_active = models.BooleanField("Active", default=True)
    hits = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["old_path"]

    def __str__(self):
        return f"{self.old_path} → {self.new_path}"


# ---------------------------------------------------------------------------------------------- version history
class Revision(models.Model):
    """A saved copy of something as it was before a change (a page includes all its sections and cards)."""

    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    object_repr = models.CharField("What", max_length=300)
    reason = models.CharField(max_length=120)
    data = models.JSONField()
    user = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["content_type", "object_id", "-created_at"])]

    def __str__(self):
        return f"{self.object_repr} · {self.reason} · {self.created_at:%b %d, %Y %H:%M}"


# --------------------------------------------------------------------------------------- visitor statistics
class DailyVisit(models.Model):
    """Page views per day, page, source and device type (core/stats.py). No cookies, nothing personal stored."""

    day = models.DateField(db_index=True)
    path = models.CharField(max_length=255)
    source = models.CharField(max_length=120, blank=True, help_text="Referring site, e.g. Google; empty = direct.")
    device = models.CharField(max_length=10)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["day", "path", "source", "device"], name="unique_daily_visit")]

    def __str__(self):
        return f"{self.day} {self.path} ({self.views})"


class DailyVisitor(models.Model):
    """One row per visitor per day, for visitor counts: a salted one-way hash, never an IP address or a cookie."""

    day = models.DateField(db_index=True)
    key = models.CharField(max_length=32)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["day", "key"], name="unique_daily_visitor")]

    def __str__(self):
        return f"{self.day} {self.key[:8]}"


class Attempt(models.Model):
    """One failed login or sent contact message, for rate limiting (core/throttle.py). `key` is a hashed address."""

    kind = models.CharField(max_length=20)
    key = models.CharField(max_length=64)
    at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["kind", "key", "at"])]

    def __str__(self):
        return f"{self.kind} {self.at:%Y-%m-%d %H:%M}"


class LighthouseRun(models.Model):
    """One automatic Google Lighthouse check of the live site: scores, timings and issues per page, phone and
    desktop. Sent by the GitHub workflow .github/workflows/lighthouse.yml (cleaned by core/lighthouse.py)."""

    ran_at = models.DateTimeField(db_index=True)
    version = models.CharField("Lighthouse version", max_length=20, blank=True)
    report_url = models.URLField("Full reports", max_length=300, blank=True)
    results = models.JSONField(default=list)

    class Meta:
        ordering = ["-ran_at"]

    def __str__(self):
        return f"Lighthouse {self.ran_at:%Y-%m-%d %H:%M}"
