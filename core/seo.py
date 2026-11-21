"""Search-engine and link-preview data for every page: title, description, canonical address, robots,
Open Graph / X cards and JSON-LD structured data (organisation, website, breadcrumbs, articles).

Views build a `seo` dict with these helpers; templates/partials/seo.html prints it in <head>.
"""

import json

from django.templatetags.static import static
from django.utils.safestring import mark_safe

from .models import SiteSettings


def base_url(request, site=None):
    site = site or SiteSettings.load()
    if site.site_url.strip():
        return site.site_url.strip().rstrip("/")
    return f"{request.scheme}://{request.get_host()}"


def absolute(base, url):
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    return base + (url if url.startswith("/") else "/" + url)


def ld_json(data):
    """JSON-LD that is safe inside <script> (no closing tags can break out)."""
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return mark_safe(text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))


TITLE_MAX = 60  # characters Google shows; the brand suffix is left off when it would not fit


def _title(site, title):
    suffix = site.seo_suffix
    if suffix and not title.endswith(suffix.strip()) and len(title + suffix) <= TITLE_MAX:
        return title + suffix
    return title


def detail_title(site, title):
    """The <title> of a blog post or story page: '<title> | <organisation>' when that fits."""
    if site.seo_name and not site.seo_suffix:
        branded = f"{title} | {site.seo_name}"
        return branded if len(branded) <= TITLE_MAX else title
    return _title(site, title)


def clip(text, limit=160):
    """Search results show about 155-160 characters: cut longer descriptions at a word, with an ellipsis."""
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,.;:-") + "…"


def _default_image(site):
    return site.share_image.url if site.share_image else static("img/share-default.jpg")  # 1200 x 630


def organization(site, base):
    logo = absolute(base, site.logo.url if site.logo else static("img/wise-teck-logo-512.png"))
    org = {
        "@type": "EducationalOrganization",
        "@id": base + "/#organization",
        "name": site.seo_name or site.site_name,
        "url": base + "/",
        "logo": logo,
    }
    if site.phone:
        org["telephone"] = site.phone
    if site.email:
        org["email"] = site.email
    if site.address:
        addr = {"@type": "PostalAddress", "streetAddress": site.address}
        if site.city:
            addr["addressLocality"] = site.city
        if site.country_code:
            addr["addressCountry"] = site.country_code.upper()
        org["address"] = addr
    same = [u for _, u, _, _ in site.socials if u.startswith("http")]
    if same:
        org["sameAs"] = same
    if site.registration:
        org["description"] = site.registration
    return org


def website(site, base):
    return {
        "@type": "WebSite",
        "@id": base + "/#website",
        "name": site.seo_name or site.site_name,
        "url": base + "/",
        "publisher": {"@id": base + "/#organization"},
        "inLanguage": "en",
    }


def breadcrumbs(base, crumbs, canonical):
    """crumbs: [(label, url), ...]; the last one is the current page."""
    items = []
    for n, (label, url) in enumerate(crumbs, 1):
        items.append(
            {
                "@type": "ListItem",
                "position": n,
                "name": label,
                "item": canonical if n == len(crumbs) else absolute(base, url or "/"),
            }
        )
    return {"@type": "BreadcrumbList", "itemListElement": items}


def _pack(seo, graph):
    seo["jsonld"] = ld_json({"@context": "https://schema.org", "@graph": graph}) if graph else ""
    return seo


def page_seo(request, page, sections, preview=False, paged=None):
    site = SiteSettings.load()
    base = base_url(request, site)
    live = page.draft_of or page
    canonical = page.canonical_url.strip() or absolute(base, live.get_absolute_url())
    canonical = absolute(base, canonical)
    hero = next((s for s in sections if s.is_hero), None)
    image = page.share_image.url if page.share_image else ""
    if not image:
        image = next((s.img for s in sections if s.img), "") or _default_image(site)
    description = page.meta_description or site.meta_description
    title = page.title
    prev_url = next_url = ""
    if paged is not None and paged.paginator.num_pages > 1:
        n, url = paged.number, canonical.split("?")[0]
        if n > 1:
            canonical, title = f"{url}?page={n}", f"{page.title} – Page {n}"
            description = f"Page {n} of {paged.paginator.num_pages}. {description}"
        if paged.has_previous():
            prev_url = url if paged.previous_page_number() == 1 else f"{url}?page={paged.previous_page_number()}"
        if paged.has_next():
            next_url = f"{url}?page={paged.next_page_number()}"
    description = clip(description)
    seo = {
        "title": _title(site, title),
        "description": description,
        "canonical": canonical,
        "prev": prev_url,
        "next": next_url,
        "noindex": preview or page.noindex or page.is_draft or not page.is_active,
        "og_type": "website",
        "og_title": page.share_title or page.title,
        "og_description": page.share_description or description,
        "image": absolute(base, image),
        "site_name": site.seo_name or site.site_name,
        "google": site.google_verification,
    }
    graph = []
    if live.slug == "home":
        graph += [organization(site, base), website(site, base)]
    crumbs = hero.crumb_list if hero is not None and hero.layout == "page_hero" else []
    if len(crumbs) > 1:
        graph.append(breadcrumbs(base, crumbs, canonical))
    graph.append(
        {
            "@type": "WebPage",
            "@id": canonical,
            "url": canonical,
            "name": page.title,
            "description": description,
            "isPartOf": {"@id": base + "/#website"},
            "inLanguage": "en",
        }
    )
    return _pack(seo, graph)


def detail_seo(request, kind, obj, title, description, image, parent=None, parent_label=""):
    site = SiteSettings.load()
    base = base_url(request, site)
    canonical = absolute(base, obj.get_absolute_url())
    img = absolute(base, image or _default_image(site))
    seo = {
        "title": detail_title(site, title),
        "description": clip(description or site.meta_description),
        "canonical": canonical,
        "noindex": False,
        "og_type": "article",
        "og_title": title,
        "og_description": description or site.meta_description,
        "image": img,
        "site_name": site.seo_name or site.site_name,
        "google": site.google_verification,
    }
    crumbs = [("Home", "/")]
    if parent is not None:
        crumbs.append((parent_label or parent.title, parent.get_absolute_url()))
    crumbs.append((title, obj.get_absolute_url()))
    art = {
        "@type": "BlogPosting" if kind == "blog" else "Article",
        "@id": canonical + "#article",
        "headline": title[:110],
        "description": description,
        "image": [img],
        "url": canonical,
        "mainEntityOfPage": canonical,
        "publisher": {
            "@type": "Organization",
            "name": site.seo_name or site.site_name,
            "logo": {"@type": "ImageObject", "url": absolute(base, static("img/wise-teck-logo-512.png"))},
        },
        "inLanguage": "en",
    }
    published = (
        getattr(obj, "published_at", None) or getattr(obj, "publish_at", None) or getattr(obj, "created_at", None)
    )
    if published:
        art["datePublished"] = published.isoformat()
    if getattr(obj, "updated_at", None):
        art["dateModified"] = obj.updated_at.isoformat()
    author = getattr(obj, "author", "") or ""
    art["author"] = (
        {"@type": "Person", "name": author}
        if author
        else {"@type": "Organization", "name": site.seo_name or site.site_name}
    )
    return _pack(seo, [breadcrumbs(base, crumbs, canonical), art])


def plain_seo(request, title, noindex=True):
    """Pages that are not content (404, errors)."""
    site = SiteSettings.load()
    return {
        "title": _title(site, title),
        "description": site.meta_description,
        "canonical": "",
        "noindex": noindex,
        "og_type": "website",
        "og_title": title,
        "og_description": site.meta_description,
        "image": absolute(base_url(request, site), _default_image(site)),
        "site_name": site.seo_name or site.site_name,
        "google": "",
        "jsonld": "",
    }
