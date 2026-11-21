"""
Wise-Teck admin panel — full CRUD for all site models.

Ported from the original site's custom panel (same screens and styling) and extended with the
v2 website structure: pages, sections with their cards, menu, footer and site settings.
"""

from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from .. import seo_audit, stats, throttle, versioning
from ..layouts import ALWAYS, GUIDE
from ..models import (
    BlogPost,
    ContactMessage,
    FooterColumn,
    NavItem,
    Page,
    Program,
    Redirect,
    Revision,
    Section,
    Service,
    SiteSettings,
    SuccessStory,
    TeamMember,
)
from ..permissions import staff_required
from ..seo import base_url
from . import forms as F

YES_NO = [(True, "Yes"), (False, "No")]
LIVE_OR_DRAFT = [(True, "Live pages"), (False, "Drafts")]


def page_choices():
    return [(p.pk, str(p)) for p in Page.objects.all()]


# ---------------------------------------------------------------------------
# Resource registry — mirrors Django admin list/search/filter capabilities
# ---------------------------------------------------------------------------

RESOURCES = {
    # --- Website -----------------------------------------------------------
    "pages": {
        "group": "Website",
        "model": Page,
        "form": F.PageForm,
        "label": "Pages",
        "singular": "Page",
        "icon": "file",
        "list_fields": [
            ("__str__", "Title"),
            ("address", "Address"),
            ("section_count", "Sections"),
            ("status", "Status"),
        ],
        "search_fields": ["title", "slug", "meta_description"],
        "filter_fields": [
            ("draft_of__isnull", "Type", LIVE_OR_DRAFT),
            ("is_active", "Published", YES_NO),
            ("noindex", "Hidden from search", YES_NO),
        ],
        "children": "sections",
        "fieldsets": [
            ("Page", ["title", "slug", "meta_description", "is_active", "publish_at"]),
            ("Link previews (WhatsApp, Facebook, LinkedIn, X)", ["share_title", "share_description", "share_image"]),
            ("Search engines (advanced)", ["noindex", "canonical_url"]),
        ],
    },
    "sections": {
        "group": "Website",
        "model": Section,
        "form": F.SectionForm,
        "formset": F.ItemFormSet,
        "formset_label": "Cards / items in this section",
        "label": "Sections",
        "singular": "Section",
        "icon": "layers",
        "list_fields": [
            ("page", "Page"),
            ("order", "Order"),
            ("layout", "Layout"),
            ("title", "Title"),
            ("is_active", "Show"),
        ],
        "search_fields": ["title", "eyebrow", "subtitle", "body", "page__title"],
        "filter_fields": [
            ("page", "Page", page_choices),
            ("layout", "Layout", Section.LAYOUTS),
            ("is_active", "Show", YES_NO),
        ],
        "fieldsets": [
            ("Placement", ["page", "order", "layout", "is_active", "anchor", "spacing", "divider_after", "motif"]),
            ("Heading", ["crumbs", "eyebrow", "title", "highlight", "lined", "subtitle"]),
            ("Text", ["body", "note", "list_title", "list_items"]),
            (
                "Buttons",
                [
                    "button_label",
                    "button_url",
                    "button_style",
                    "button_icon",
                    "button2_label",
                    "button2_url",
                    "button2_style",
                    "button2_icon",
                ],
            ),
            (
                "Visual",
                [
                    "visual",
                    "image",
                    "image_url",
                    "image_alt",
                    "image2",
                    "image2_url",
                    "image_side",
                    "badge_icon",
                    "badge_text",
                    "stats_style",
                ],
            ),
            ("Quote", ["quote_text", "quote_highlight", "quote_author", "quote_role", "quote_icon"]),
            ("Centre label / pill", ["center_small", "center_big", "center_url"]),
            ("Cards", ["columns", "numbered", "item_label", "sub_title", "feed_limit"]),
            ("Contact form", ["form_title", "form_fields"]),
        ],
        "prefill": ["page"],
    },
    "menu": {
        "group": "Website",
        "model": NavItem,
        "form": F.NavItemForm,
        "label": "Menu",
        "singular": "Menu Link",
        "icon": "menu",
        "list_fields": [("__str__", "Link"), ("url", "Goes to"), ("order", "Order"), ("is_active", "Show")],
        "search_fields": ["label", "url"],
        "filter_fields": [("is_active", "Show", YES_NO)],
        "ordering": ["parent__order", "parent_id", "order", "id"],
    },
    "programs": {
        "group": "Website",
        "model": Program,
        "form": F.ProgramForm,
        "label": "Programs",
        "singular": "Program",
        "icon": "cap",
        "list_fields": [("title", "Program"), ("link_url", "Page"), ("order", "Order"), ("is_active", "Show")],
        "search_fields": ["title", "text"],
        "filter_fields": [("is_active", "Show", YES_NO)],
    },
    "footer": {
        "group": "Website",
        "model": FooterColumn,
        "form": F.FooterColumnForm,
        "formset": F.FooterLinkFormSet,
        "formset_label": "Links in this column",
        "label": "Footer",
        "singular": "Footer Column",
        "icon": "columns",
        "list_fields": [("title", "Column"), ("link_count", "Links"), ("order", "Order")],
        "search_fields": ["title", "links__label"],
        "filter_fields": [],
    },
    "site-settings": {
        "group": "Website",
        "model": SiteSettings,
        "form": F.SiteSettingsForm,
        "label": "Site Settings",
        "singular": "Site Settings",
        "icon": "settings",
        "singleton": True,
        "fieldsets": [
            ("Logo", ["site_name", "logo", "favicon"]),
            ("Colour scheme", ["color_scheme", "color_primary", "color_accent", "color_dark"]),
            ("Announcement bar", ["announcement", "announcement_label", "announcement_url"]),
            ("Top bar and contact", ["topbar_text", "phone", "email", "address", "registration"]),
            ("Header button", ["apply_label", "apply_url"]),
            ("Footer", ["footer_text", "footer_contact_title", "copyright"]),
            ("Social links", ["facebook", "instagram", "linkedin", "youtube"]),
            ("Contact form", ["notify_email", "contact_success", "contact_error"]),
            ("Page not found (404)", ["notfound_title", "notfound_highlight", "notfound_text", "notfound_button"]),
            (
                "Search engines and statistics",
                [
                    "seo_name",
                    "site_url",
                    "meta_description",
                    "seo_suffix",
                    "share_image",
                    "city",
                    "country_code",
                    "google_verification",
                    "ga_id",
                    "trend_keywords",
                    "robots_extra",
                ],
            ),
            ("3D coin colours (optional)", ["coin_base_color", "coin_ring_color", "coin_ring2_color"]),
        ],
    },
    "redirects": {
        "group": "Website",
        "model": Redirect,
        "form": F.RedirectForm,
        "label": "Redirects",
        "singular": "Redirect",
        "icon": "redirect",
        "list_fields": [
            ("old_path", "Old address"),
            ("new_path", "New address"),
            ("permanent", "Permanent"),
            ("hits", "Visits"),
            ("is_active", "Active"),
        ],
        "search_fields": ["old_path", "new_path"],
        "filter_fields": [("is_active", "Active", YES_NO)],
    },
    # --- Content (from the original site) ------------------------------------
    "success-stories": {
        "group": "Content",
        "model": SuccessStory,
        "form": F.SuccessStoryForm,
        "label": "Success Stories",
        "singular": "Success Story",
        "icon": "trophy",
        "list_fields": [
            ("title", "Title"),
            ("client_name", "Student"),
            ("category", "Category"),
            ("is_featured", "Featured"),
            ("is_active", "Published"),
            ("publish_at", "Go live at"),
        ],
        "search_fields": ["title", "client_name", "short_description", "category"],
        "filter_fields": [("is_active", "Published", YES_NO), ("is_featured", "Featured", YES_NO)],
    },
    "team": {
        "group": "Content",
        "model": TeamMember,
        "form": F.TeamMemberForm,
        "label": "Team",
        "singular": "Team Member",
        "icon": "users",
        "list_fields": [
            ("name", "Name"),
            ("designation", "Designation"),
            ("service", "Department"),
            ("display_order", "Order"),
            ("is_active", "Show"),
        ],
        "search_fields": ["name", "designation", "short_description", "service"],
        "filter_fields": [("is_active", "Show", YES_NO)],
    },
    "blogs": {
        "group": "Content",
        "model": BlogPost,
        "form": F.BlogPostForm,
        "label": "Blogs",
        "singular": "Blog Post",
        "icon": "book",
        "list_fields": [
            ("title", "Title"),
            ("author", "Author"),
            ("category", "Category"),
            ("is_featured", "Featured"),
            ("is_active", "Published"),
            ("publish_at", "Go live at"),
            ("published_at", "Date shown"),
        ],
        "search_fields": ["title", "short_description", "content", "author", "category"],
        "filter_fields": [("is_active", "Published", YES_NO), ("is_featured", "Featured", YES_NO)],
    },
    "services": {
        "group": "Content",
        "model": Service,
        "form": F.ServiceForm,
        "label": "Services",
        "singular": "Service",
        "icon": "briefcase",
        "list_fields": [("name", "Name"), ("display_order", "Order"), ("is_active", "Show"), ("created_at", "Created")],
        "search_fields": ["name", "short_description"],
        "filter_fields": [("is_active", "Show", YES_NO)],
    },
    # --- Inbox -----------------------------------------------------------------
    "messages": {
        "group": "Inbox",
        "model": ContactMessage,
        "form": F.ContactMessageForm,
        "label": "Messages",
        "singular": "Message",
        "icon": "mail",
        "can_add": False,
        "no_history": True,
        "list_fields": [
            ("name", "Name"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("interest", "Interested in"),
            ("is_read", "Read"),
            ("created_at", "Received"),
        ],
        "search_fields": ["name", "email", "message", "phone", "interest"],
        "filter_fields": [("is_read", "Read", YES_NO)],
    },
}


def get_resource(slug):
    resource = RESOURCES.get(slug)
    if not resource:
        raise Http404("Unknown resource")
    return resource


def resource_url(slug):
    meta = RESOURCES[slug]
    if meta.get("singleton"):
        return reverse("adminpanel_change", kwargs={"resource": slug, "pk": SiteSettings.load().pk})
    return reverse("adminpanel_list", kwargs={"resource": slug})


def nav_items(active=None):
    items = [
        {
            "key": "dashboard",
            "label": "Dashboard",
            "icon": "home",
            "url": reverse("adminpanel_dashboard"),
            "active": active == "dashboard",
        }
    ]
    group = None
    for slug, meta in RESOURCES.items():
        if meta["group"] != group:
            group = meta["group"]
            items.append({"heading": group})
        item = {
            "key": slug,
            "label": meta["label"],
            "icon": meta["icon"],
            "url": resource_url(slug),
            "active": active == slug,
        }
        if not meta.get("singleton"):
            item["count"] = (
                ContactMessage.objects.filter(is_read=False).count()
                if slug == "messages"
                else meta["model"].objects.count()
            )
        items.append(item)
    return items


def format_cell(obj, field_name):
    if field_name == "__str__":
        return {"type": "text", "value": str(obj)}
    if field_name == "status" and isinstance(obj, Page):
        if obj.is_draft:
            when = f" · goes live {timezone.localtime(obj.publish_at):%b %d, %H:%M}" if obj.publish_at else ""
            return {"type": "text", "value": f"Draft of “{obj.draft_of.title}”{when}"}
        return {"type": "text", "value": "Live" if obj.is_active else "Unpublished"}
    if field_name == "address" and isinstance(obj, Page):
        return {"type": "text", "value": "—" if obj.is_draft else obj.get_absolute_url()}
    if field_name == "section_count":
        return {"type": "text", "value": obj.sections.count()}
    if field_name == "link_count":
        return {"type": "text", "value": obj.links.count()}
    display = getattr(obj, f"get_{field_name}_display", None)
    value = display() if callable(display) else getattr(obj, field_name, None)
    if isinstance(value, bool):
        return {"type": "bool", "value": value}
    if hasattr(value, "strftime"):
        return {"type": "text", "value": value.strftime("%b %d, %Y %H:%M")}
    return {"type": "text", "value": value if value not in (None, "") else "—"}


def form_groups(meta, form):
    """Fields grouped under headings (fieldsets), or one untitled group."""
    if not meta.get("fieldsets"):
        return [(None, list(form))]
    return [(title, [form[n] for n in names if n in form.fields]) for title, names in meta["fieldsets"]]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class AdminLoginView(View):
    template_name = "adminpanel/login.html"

    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("adminpanel_dashboard")
        return render(request, self.template_name, {"next": request.GET.get("next", "")})

    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next") or ""
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = ""
        context = {"username": username, "next": next_url}
        if throttle.blocked("login", request):  # password guessing: wait before trying again
            context["error"] = f"Too many attempts. Please wait {throttle.minutes('login')} minutes and try again."
            return render(request, self.template_name, context, status=429)
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            throttle.clear("login", request)
            login(request, user)
            return redirect(next_url or reverse("adminpanel_dashboard"))
        throttle.hit("login", request)
        context["error"] = "Invalid credentials or insufficient permissions."
        return render(request, self.template_name, context)


@staff_required
def admin_logout(request):
    logout(request)
    return redirect("adminpanel_login")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


# Summary cards on the dashboard: what an editor acts on. Everything else has its count in the sidebar.
DASHBOARD_CARDS = {
    "messages": "Messages",
    "pages": "Pages",
    "blogs": "Blogs",
    "success-stories": "Stories",
    "team": "Team",
    "services": "Services",
}


def _google_tools(site, base):
    """Links to the Google tools that matter for this site, filled in with its address and keywords."""
    keywords = [k.strip() for k in site.trend_keywords.split(",") if k.strip()][:5]
    geo = (site.country_code or "").upper()
    home = quote(base + "/", safe="")
    return {
        "sitemap": f"{base}/sitemap.xml",
        "search_console": f"https://search.google.com/search-console?resource_id={home}",
        "analytics": "https://analytics.google.com/analytics/web/" if site.ga_id else "",
        "trends": (
            f"https://trends.google.com/trends/explore?date=today%2012-m&geo={geo}&q="
            + ",".join(quote(k) for k in keywords)
        )
        if keywords
        else "",
        "searches": [(k, f"https://www.google.com/search?q={quote(k)}&gl={geo.lower()}") for k in keywords],
        "pagespeed": f"https://pagespeed.web.dev/analysis?url={home}",
        "rich_results": f"https://search.google.com/test/rich-results?url={home}",
        "business": "https://business.google.com/",
    }


@staff_required
def dashboard(request):
    site = SiteSettings.load()
    cards = []
    for slug in DASHBOARD_CARDS:
        meta = RESOURCES[slug]
        model = meta["model"]
        extra = {}
        if slug == "messages":
            extra["unread"] = model.objects.filter(is_read=False).count()
        elif any(f.name == "is_active" for f in model._meta.fields):
            extra["active"] = model.objects.filter(is_active=True).count()
        cards.append(
            {
                "slug": slug,
                "label": DASHBOARD_CARDS[slug],
                "icon": meta["icon"],
                "total": model.objects.count(),
                "extra": extra,
                "url": resource_url(slug),
            }
        )

    return render(
        request,
        "adminpanel/dashboard.html",
        {
            "nav_items": nav_items("dashboard"),
            "page_title": "Dashboard",
            "stats": cards,
            "visitors": stats.summary(),
            "seo": seo_audit.audit(),
            "google": _google_tools(site, base_url(request, site)),
            "ga_id": site.ga_id,
            "recent_contacts": ContactMessage.objects.all()[:6],
            "recent_blogs": BlogPost.objects.all()[:5],
            "settings_url": resource_url("site-settings"),
            "drafts": Page.objects.drafts().select_related("draft_of").order_by("publish_at", "-updated_at")[:8],
            "scheduled_items": (
                list(BlogPost.objects.filter(is_active=True, publish_at__gt=timezone.now()))
                + list(SuccessStory.objects.filter(is_active=True, publish_at__gt=timezone.now()))
            ),
            "recent_changes": Revision.objects.select_related("user")[:8],
        },
    )


# ---------------------------------------------------------------------------
# Generic CRUD
# ---------------------------------------------------------------------------


@staff_required
def resource_list(request, resource):
    meta = get_resource(resource)
    if meta.get("singleton"):
        return redirect(resource_url(resource))
    qs = meta["model"].objects.all()
    if meta.get("ordering"):
        qs = qs.order_by(*meta["ordering"])

    q = request.GET.get("q", "").strip()
    if q and meta["search_fields"]:
        query = Q()
        for field in meta["search_fields"]:
            query |= Q(**{f"{field}__icontains": q})
        qs = qs.filter(query).distinct()

    active_filters = {}
    filters = []
    for field_name, label, choices in meta.get("filter_fields", []):
        choices = choices() if callable(choices) else choices
        raw = request.GET.get(field_name, "")
        valid = {str(v) for v, _ in choices}
        if raw in valid:
            value = (
                {"True": True, "False": False}.get(raw, raw) if all(isinstance(v, bool) for v, _ in choices) else raw
            )
            qs = qs.filter(**{field_name: value})
            active_filters[field_name] = raw
        filters.append(
            {
                "name": field_name,
                "label": label,
                "options": [{"value": str(v), "text": t, "selected": raw == str(v)} for v, t in choices],
                "current": active_filters.get(field_name),
            }
        )

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("p"))  # "page" is the Sections filter
    rows = [{"obj": obj, "cells": [format_cell(obj, name) for name, _ in meta["list_fields"]]} for obj in page]

    return render(
        request,
        "adminpanel/list.html",
        {
            "nav_items": nav_items(resource),
            "page_title": meta["label"],
            "resource": resource,
            "meta": meta,
            "rows": rows,
            "page_obj": page,
            "q": q,
            "active_filters": active_filters,
            "filters": filters,
            "total_count": paginator.count,
            "can_add": meta.get("can_add", True),
        },
    )


def _render_form(request, resource, meta, form, formset, obj):
    is_create = obj is None
    children = None
    if obj is not None and meta.get("children") == "sections":
        children = obj.sections.order_by("order", "id")
    tracked = obj is not None and not meta.get("no_history")
    root = versioning.history_root(obj) if tracked else None
    return render(
        request,
        "adminpanel/form.html",
        {
            "nav_items": nav_items(resource),
            "page_title": (
                f"Add {meta['singular']}"
                if is_create
                else meta["singular"]
                if meta.get("singleton")
                else f"Edit {meta['singular']}"
            ),
            "resource": resource,
            "meta": meta,
            "form": form,
            "groups": form_groups(meta, form),
            "formset": formset,
            "object": obj,
            "is_create": is_create,
            "children": children,
            "view_url": obj.get_absolute_url() if obj is not None and hasattr(obj, "get_absolute_url") else "",
            "back_url": (
                reverse("adminpanel_change", kwargs={"resource": "pages", "pk": obj.page_id})
                if isinstance(obj, Section)
                else ""
            ),
            "layout_guide": {"always": ALWAYS, "layouts": GUIDE} if resource == "sections" else None,
            # drafts, scheduling and version history
            "history": list(versioning.history(root)[:30]) if root is not None else None,
            "history_root": root,
            "history_is_page": isinstance(root, Page),
            "drafts": list(obj.drafts.all()) if isinstance(obj, Page) and not obj.is_draft else [],
            "page_url": (
                reverse("adminpanel_change", kwargs={"resource": "pages", "pk": root.pk})
                if isinstance(root, Page) and not isinstance(obj, Page)
                else ""
            ),
        },
    )


def _who(request):
    return request.user if request.user.is_authenticated else None


def _save(request, resource, meta, obj=None):
    form = meta["form"](
        request.POST or None,
        request.FILES or None,
        instance=obj,
        initial={k: request.GET[k] for k in meta.get("prefill", []) if k in request.GET} if obj is None else None,
    )
    formset = None
    if meta.get("formset"):
        formset = meta["formset"](request.POST or None, request.FILES or None, instance=obj or meta["model"]())
    if request.method == "POST" and form.is_valid() and (formset is None or formset.is_valid()):
        target = obj if obj is not None else (form.cleaned_data.get("page") if resource == "sections" else None)
        label = f"{meta['singular'].lower()} “{obj}”" if obj is not None else f"new {meta['singular'].lower()}"
        tracker = (
            None
            if meta.get("no_history")
            else versioning.Tracker(target, f"Before editing {label}"[:120], _who(request))
        )
        with transaction.atomic():
            saved = form.save()
            if formset is not None:
                formset.instance = saved
                formset.save()
            if tracker:
                tracker.done()
        verb = "created" if obj is None else "updated"
        messages.success(request, f"{meta['singular']} {verb} successfully.")
        return redirect("adminpanel_change", resource=resource, pk=saved.pk)
    return _render_form(request, resource, meta, form, formset, obj)


@staff_required
def resource_create(request, resource):
    meta = get_resource(resource)
    if meta.get("singleton") or not meta.get("can_add", True):
        return redirect(resource_url(resource))
    return _save(request, resource, meta)


@staff_required
def resource_change(request, resource, pk):
    meta = get_resource(resource)
    obj = get_object_or_404(meta["model"], pk=pk)
    return _save(request, resource, meta, obj)


@staff_required
def resource_delete(request, resource, pk):
    meta = get_resource(resource)
    if meta.get("singleton"):
        return redirect(resource_url(resource))
    obj = get_object_or_404(meta["model"], pk=pk)
    if request.method == "POST":
        label = str(obj)
        back = (
            reverse("adminpanel_change", kwargs={"resource": "pages", "pk": obj.page_id})
            if isinstance(obj, Section)
            else reverse("adminpanel_list", kwargs={"resource": resource})
        )
        if isinstance(obj, Page) and obj.is_draft:
            back = reverse("adminpanel_change", kwargs={"resource": "pages", "pk": obj.draft_of_id})
        skip = meta.get("no_history") or (isinstance(obj, Page) and obj.is_draft)  # discarding a draft
        tracker = (
            None
            if skip
            else versioning.Tracker(obj, f"Before deleting {meta['singular'].lower()} “{label}”"[:120], _who(request))
        )
        with transaction.atomic():
            obj.delete()
            if tracker:
                tracker.done()
        messages.success(request, f"{meta['singular']} “{label}” deleted.")
        return redirect(back)

    return render(
        request,
        "adminpanel/delete.html",
        {
            "nav_items": nav_items(resource),
            "page_title": f"Delete {meta['singular']}",
            "resource": resource,
            "meta": meta,
            "object": obj,
        },
    )


# ---------------------------------------------------------------------------
# Drafts, publishing, version history
# ---------------------------------------------------------------------------


def _page_admin(pk):
    return redirect("adminpanel_change", resource="pages", pk=pk)


@staff_required
def page_create_draft(request, pk):
    page = get_object_or_404(Page, pk=pk, draft_of__isnull=True)
    if request.method != "POST":
        return _page_admin(pk)
    draft = versioning.create_draft(page, _who(request))
    messages.success(
        request,
        "Draft created. Edit its sections below, preview it, then publish it when ready. "
        "Visitors still see the live page.",
    )
    return _page_admin(draft.pk)


@staff_required
def page_publish_draft(request, pk):
    draft = get_object_or_404(Page, pk=pk, draft_of__isnull=False)
    if request.method != "POST":
        return _page_admin(pk)
    live = versioning.publish_draft(draft, _who(request))
    messages.success(request, f"Draft published. “{live.title}” is now live. The previous version is in its history.")
    return _page_admin(live.pk)


@staff_required
def revision_restore(request, pk):
    rev = get_object_or_404(Revision, pk=pk)
    back = request.POST.get("back") or reverse("adminpanel_dashboard")
    if not url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}):
        back = reverse("adminpanel_dashboard")
    if request.method != "POST":
        return redirect(back)
    try:
        obj = versioning.restore(rev, _who(request))
    except ValueError as e:
        messages.error(request, str(e))
        return redirect(back)
    messages.success(
        request,
        f"Restored “{obj}” to the version of {timezone.localtime(rev.created_at):%b %d, %Y %H:%M}. "
        "The version before restoring is kept in the history.",
    )
    return redirect(back)


@staff_required
def revision_to_draft(request, pk):
    """Open an old page version as a draft, to check and adjust it before it goes live."""
    rev = get_object_or_404(Revision, pk=pk, content_type__model="page")
    page = get_object_or_404(Page, pk=rev.object_id)
    if request.method != "POST" or "sections" not in rev.data:
        return _page_admin(page.pk)
    draft = versioning.create_draft(
        page.draft_of or page,
        _who(request),
        data=rev.data,
        title_note=f"from the version of {timezone.localtime(rev.created_at):%b %d, %Y %H:%M}",
    )
    messages.success(request, "That version is now a draft. Check it, then publish it to make it live.")
    return _page_admin(draft.pk)


@staff_required
def contact_mark_read(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        contact.is_read = not contact.is_read
        contact.save(update_fields=["is_read"])
        messages.success(request, f"Marked as {'read' if contact.is_read else 'unread'}.")
    back = request.META.get("HTTP_REFERER", "")
    if not url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}):
        back = reverse("adminpanel_list", kwargs={"resource": "messages"})
    return redirect(back)
