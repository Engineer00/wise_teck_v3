import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_page

from . import seo as seo_data
from . import throttle, versioning
from .forms import ContactForm
from .models import BlogPost, Detail, Item, Page, Revision, Section, SiteSettings, SuccessStory
from .permissions import staff_required

log = logging.getLogger(__name__)


def notify_new_message(msg):
    """Email the addresses in Site settings → 'Send contact form alerts to'."""
    to = [a.strip() for a in SiteSettings.load().notify_email.split(",") if a.strip()]
    if not to:
        return
    body = (
        f"Name: {msg.name}\nEmail: {msg.email}\nPhone: {msg.phone}\n"
        f"Interested in: {msg.interest}\nSent from: {msg.page}\n\nMessage:\n{msg.message}\n"
    )
    try:
        send_mail(f"New contact message: {msg.name}", body, settings.DEFAULT_FROM_EMAIL, to)
    except Exception:  # the message is saved either way; never show a mail error to the visitor
        log.exception("Could not send the contact form alert")


def _sections(page):
    return list(page.sections.all())


def _paginate(request, sections):
    """Split the page's blog / story list into numbered pages (?page=2). Returns the page object or None."""
    current = None
    raw = request.GET.get("page")
    for s in sections:
        if not s.paginated:
            continue
        paginator = Paginator(s.feed_queryset(), s.per_page)
        if raw is None:
            s.page_obj = paginator.page(1)
        else:
            try:
                s.page_obj = paginator.page(raw)
            except (EmptyPage, PageNotAnInteger):
                raise Http404("No such page") from None
        current = current or s.page_obj
    return current


def _page_qs():
    sections_qs = Section.objects.filter(is_active=True).prefetch_related(
        Prefetch("items", queryset=Item.objects.order_by("order", "id")),
        Prefetch("details", queryset=Detail.objects.order_by("order", "id")),
    )
    return Page.objects.prefetch_related(Prefetch("sections", queryset=sections_qs))


def _render_page(request, obj, extra=None):
    sections = _sections(obj)
    _paginate(request, sections)
    return render(
        request,
        "page.html",
        {
            "page": obj,
            "sections": sections,
            "form": None,
            "is_home": (obj.draft_of or obj).slug == "home",
            "uses_three": any(s.uses_three for s in sections),
            "seo": seo_data.page_seo(request, obj, sections, preview=True),
            **(extra or {}),
        },
    )


def page(request, slug="home"):
    versioning.publish_due()  # scheduled drafts go live on the first visit after their time
    obj = get_object_or_404(_page_qs().live(), slug=slug, is_active=True)
    sections = _sections(obj)
    if request.GET.get("page") == "1":  # page 1 has one address: the page itself
        return redirect(obj.get_absolute_url(), permanent=True)
    paged = _paginate(request, sections)
    form = None
    if any(s.layout == "contact" for s in sections):
        if request.method == "POST":
            form = ContactForm(request.POST)
            if throttle.blocked("contact", request):
                form.add_error(
                    None, "Thank you, we already have your messages. Please wait a few minutes before sending more."
                )
            elif form.is_valid():
                throttle.hit("contact", request)
                msg = form.save(commit=False)
                msg.page = request.path
                msg.save()
                notify_new_message(msg)
                messages.success(request, SiteSettings.load().contact_success)
                return redirect(f"{request.path}#contact-form")
        else:
            form = ContactForm(initial={"interest": request.GET.get("interest", "")})
    return render(
        request,
        "page.html",
        {
            "page": obj,
            "sections": sections,
            "form": form,
            "is_home": obj.slug == "home",
            "uses_three": any(s.uses_three for s in sections),
            "seo": seo_data.page_seo(request, obj, sections, paged=paged),
        },
    )


def _list_page(slug):
    """The list page (Blog / Success stories): breadcrumb parent and its call-to-action band."""
    parent = Page.objects.live().filter(slug=slug, is_active=True).first()
    secs = list(parent.sections.filter(is_active=True)) if parent else []
    cta = [s for s in secs if s.layout == "cta"][:1]
    label = next(
        (s.crumb_list[-1][0] for s in secs if s.layout == "page_hero" and s.crumb_list), parent.title if parent else ""
    )
    return parent, label, cta


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost.objects.live(), slug=slug)
    parent, label, cta = _list_page("blog")
    more = BlogPost.objects.live().exclude(pk=post.pk)[:3]
    return render(
        request,
        "detail.html",
        {
            "kind": "blog",
            "obj": post,
            "parent": parent,
            "parent_label": label or "Blog",
            "cta": cta,
            "more": more,
            "more_title": "More Articles",
            "title": post.title,
            "eyebrow": post.category,
            "image": post.img,
            "description": post.short_description,
            "meta": [
                x for x in [post.published_at.strftime("%b %d, %Y") if post.published_at else "", post.author] if x
            ],
            "seo": seo_data.detail_seo(
                request, "blog", post, post.title, post.short_description, post.img, parent, label or "Blog"
            ),
        },
    )


def story_detail(request, slug):
    story = get_object_or_404(SuccessStory.objects.live(), slug=slug)
    parent, label, cta = _list_page("success-stories")
    more = SuccessStory.objects.live().exclude(pk=story.pk)[:2]
    return render(
        request,
        "detail.html",
        {
            "kind": "story",
            "obj": story,
            "parent": parent,
            "parent_label": label or "Success Stories",
            "cta": cta,
            "more": more,
            "more_title": "More Success Stories",
            "title": story.title,
            "eyebrow": story.category,
            "image": story.img,
            "description": story.short_description,
            "meta": [x for x in [story.client_name, story.category] if x],
            "seo": seo_data.detail_seo(
                request,
                "story",
                story,
                story.title,
                story.short_description,
                story.img,
                parent,
                label or "Success Stories",
            ),
        },
    )


# ------------------------------------------------------------------------------------------ previews (staff only)
@staff_required
def preview_page(request, pk):
    """A draft (or an unpublished page) exactly as visitors would see it."""
    obj = get_object_or_404(_page_qs(), pk=pk)
    if obj.is_draft:
        label = f"Draft of “{obj.draft_of.title}” · not visible to visitors"
        if obj.publish_at:
            label += f" · goes live {timezone.localtime(obj.publish_at):%b %d, %Y %H:%M}"
    else:
        label = "Live page" if obj.is_active else "Unpublished page · not visible to visitors"
    return _render_page(request, obj, {"preview": {"label": label, "back": f"/admin/pages/{obj.pk}/change/"}})


@staff_required
def preview_revision(request, pk):
    """An old version of a page, drawn from its saved copy. Nothing on the site is changed."""
    rev = get_object_or_404(Revision, pk=pk)
    live = Page.objects.filter(pk=rev.object_id).first()
    if rev.content_type.model != "page" or live is None or "sections" not in rev.data:
        return redirect("adminpanel_dashboard")
    with transaction.atomic():
        temp = versioning.create_draft(live, data=rev.data)
        response = _render_page(
            request,
            _page_qs().get(pk=temp.pk),
            {
                "preview": {
                    "label": f"Saved version · {timezone.localtime(rev.created_at):%b %d, %Y %H:%M} · {rev.reason}",
                    "back": f"/admin/pages/{live.pk}/change/#history",
                }
            },
        )
        transaction.set_rollback(True)  # the temporary copy is thrown away
    return response


# ------------------------------------------------------------------------------------------ search engines
def robots_txt(request):
    site = SiteSettings.load()
    lines = ["User-agent: *", "Disallow: /admin/", "Disallow: /adminpanel/", "Disallow: /preview/", "Allow: /", ""]
    extra = site.robots_extra.strip()
    if extra:
        lines += [extra, ""]
    lines.append(f"Sitemap: {seo_data.base_url(request, site)}/sitemap.xml")
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


@cache_page(60 * 15)
def sitemap_xml(request):
    """Every published, indexable page, blog post and full success story, with its last change date."""
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Max
    from django.utils.html import escape

    site = SiteSettings.load()
    base = seo_data.base_url(request, site)
    ct = ContentType.objects.get_for_model(Page)
    changed = dict(
        Revision.objects.filter(content_type=ct)
        .values("object_id")
        .annotate(m=Max("created_at"))
        .values_list("object_id", "m")
    )
    urls = []
    for p in Page.objects.live().filter(is_active=True, noindex=False, canonical_url=""):
        last = max([d for d in (p.updated_at, changed.get(p.pk)) if d], default=None)
        urls.append((base + p.get_absolute_url(), last, "1.0" if p.slug == "home" else "0.8"))
    for b in BlogPost.objects.live():
        urls.append((base + b.get_absolute_url(), b.updated_at, "0.6"))
    for st in SuccessStory.objects.live().exclude(description=""):
        urls.append((base + st.get_absolute_url(), st.updated_at, "0.5"))
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, last, prio in urls:
        body.append(
            f"  <url><loc>{escape(loc)}</loc>"
            + (f"<lastmod>{last.date().isoformat()}</lastmod>" if last else "")
            + f"<priority>{prio}</priority></url>"
        )
    body.append("</urlset>")
    return HttpResponse("\n".join(body) + "\n", content_type="application/xml; charset=utf-8")


def not_found(request, exception=None):
    return render(request, "404.html", {"seo": seo_data.plain_seo(request, "Page not found")}, status=404)
