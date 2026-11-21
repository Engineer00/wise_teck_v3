"""Drafts, scheduled publishing and version history.

* Version history: before anything is changed in the admin panel, a copy of it is saved as a Revision.
  A page's copy includes all its sections and their cards, so a whole page can be restored at once.
* Drafts: "Create draft" copies a live page (with its sections and cards) into a private draft page.
  It is edited with the normal forms, previewed at /preview/page/<id>/, then published or discarded.
* Scheduled publishing: a draft with "Go live at" replaces its live page at that time. Due drafts are
  published on the next page view, and by `manage.py publish_scheduled` (run it from cron for exact timing).
  Blog posts and success stories have their own "Go live at" and stay hidden until then.
"""

import json
import uuid

from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.utils import timezone

from .models import FooterColumn, Item, Page, Revision, Section

KEEP_PER_OBJECT = 60  # oldest revisions beyond this are removed
PAGE_FIELDS_SKIP = {"id", "slug", "draft_of", "publish_at", "created_at", "updated_at"}
CHILDREN = {FooterColumn: ("links", "column")}  # simple objects saved together with their child rows


# ------------------------------------------------------------------------------------------ copies
def _fields(obj, skip=()):
    out = {}
    for f in obj._meta.concrete_fields:
        if f.name in skip or f.primary_key:
            continue
        v = getattr(obj, f.attname)
        if isinstance(f, models.FileField):
            v = v.name if v else ""
        out[f.attname] = v
    return json.loads(json.dumps(out, cls=DjangoJSONEncoder))


def _apply(obj, data, skip=()):
    for f in obj._meta.concrete_fields:
        if f.primary_key or f.name in skip or f.attname not in data:
            continue
        if isinstance(f, (models.DateTimeField, models.DateField)) and getattr(f, "auto_now", False):
            continue
        setattr(obj, f.attname, f.to_python(data[f.attname]) if data[f.attname] is not None else None)


def page_snapshot(page):
    return {
        "page": _fields(page, PAGE_FIELDS_SKIP),
        "sections": [
            dict(_fields(s, {"page"}), items=[_fields(i, {"section"}) for i in s.items.all()])
            for s in page.sections.all().order_by("order", "id")
        ],
    }


def snapshot(obj):
    if isinstance(obj, Page):
        return page_snapshot(obj)
    data = {"fields": _fields(obj)}
    if type(obj) in CHILDREN:
        rel, fk = CHILDREN[type(obj)]
        data["children"] = [_fields(c, {fk}) for c in getattr(obj, rel).all()]
    return data


def _fill_page(page, data):
    """Replace a page's sections and cards with those in data."""
    page.sections.all().delete()
    for sd in data["sections"]:
        sd = dict(sd)
        items = sd.pop("items", [])
        sec = Section(page=page)
        _apply(sec, sd, {"page"})
        sec.page = page
        sec.save()
        for idata in items:
            it = Item(section=sec)
            _apply(it, idata, {"section"})
            it.section = sec
            it.save()


# ------------------------------------------------------------------------------------------ history
def record(obj, reason, user=None, data=None):
    """Save how obj looks now (or the given data) as a revision."""
    if obj is None or obj.pk is None:
        return None
    rev = Revision.objects.create(
        content_type=ContentType.objects.get_for_model(type(obj)),
        object_id=obj.pk,
        object_repr=str(obj)[:300],
        reason=reason[:120],
        data=data if data is not None else snapshot(obj),
        user=user if getattr(user, "is_authenticated", False) else None,
    )
    old = Revision.objects.filter(content_type=rev.content_type, object_id=obj.pk).values_list("pk", flat=True)[
        KEEP_PER_OBJECT:
    ]
    Revision.objects.filter(pk__in=list(old)).delete()
    return rev


def history(obj):
    if obj is None or obj.pk is None:
        return Revision.objects.none()
    return Revision.objects.filter(
        content_type=ContentType.objects.get_for_model(type(obj)), object_id=obj.pk
    ).select_related("user")


def history_root(obj):
    """What a change to obj is recorded against: sections and cards belong to their page."""
    if isinstance(obj, Section):
        return obj.page
    if isinstance(obj, Item):
        return obj.section.page
    return obj


class Tracker:
    """Use around a change: records the 'before' copy only if something actually changed."""

    def __init__(self, obj, reason, user):
        root = history_root(obj) if obj is not None and obj.pk else None
        # read it fresh from the database: a validated form has already put the NEW values on the object in memory
        self.root = type(root).objects.filter(pk=root.pk).first() if root is not None else None
        self.reason, self.user = reason, user
        self.before = snapshot(self.root) if self.root is not None else None

    def done(self):
        if self.root is None:
            return
        try:
            self.root.refresh_from_db()
        except type(self.root).DoesNotExist:  # it was deleted: keep the copy
            record_deleted(self.root, self.before, self.reason, self.user)
            return
        if snapshot(self.root) != self.before:
            record(self.root, self.reason, self.user, data=self.before)


def record_deleted(obj, data, reason, user):
    Revision.objects.create(
        content_type=ContentType.objects.get_for_model(type(obj)),
        object_id=obj.pk,
        object_repr=str(obj)[:300],
        reason=reason[:120],
        data=data,
        user=user if getattr(user, "is_authenticated", False) else None,
    )


@transaction.atomic
def restore(revision, user=None):
    """Put the object back the way it was in this revision. The current state is kept as a revision first."""
    model = revision.content_type.model_class()
    obj = model.objects.filter(pk=revision.object_id).first()
    if obj is None:
        raise ValueError("This item no longer exists, so it cannot be restored.")
    record(obj, f"Before restoring the version of {timezone.localtime(revision.created_at):%b %d, %Y %H:%M}", user)
    data = revision.data
    if isinstance(obj, Page):
        _apply(obj, data["page"], PAGE_FIELDS_SKIP)
        obj.save()
        _fill_page(obj, data)
    else:
        _apply(obj, data["fields"], {"created_at", "updated_at"})
        obj.save()
        if type(obj) in CHILDREN and "children" in data:
            rel, fk = CHILDREN[type(obj)]
            child_model = getattr(obj, rel).model
            getattr(obj, rel).all().delete()
            for cd in data["children"]:
                c = child_model(**{fk: obj})
                _apply(c, cd, {fk})
                setattr(c, fk, obj)
                c.save()
    return obj


# ------------------------------------------------------------------------------------------ drafts
@transaction.atomic
def create_draft(page, user=None, data=None, title_note=""):
    """A private copy of a live page (or of a saved version of it) to edit and publish later."""
    live = page.draft_of or page
    draft = Page.objects.create(
        slug=f"draft-{uuid.uuid4().hex[:10]}",
        title=live.title,
        meta_description=live.meta_description,
        is_active=False,
        draft_of=live,
    )
    src = data or page_snapshot(page)
    if data:
        _apply(draft, data["page"], PAGE_FIELDS_SKIP | {"is_active"})
        draft.save()
    _fill_page(draft, src)
    return draft


@transaction.atomic
def publish_draft(draft, user=None, scheduled=False):
    """Replace the live page's content with the draft, keep the old live page in history, remove the draft."""
    live = draft.draft_of
    if live is None:
        raise ValueError("Not a draft.")
    record(live, "Before publishing a scheduled draft" if scheduled else "Before publishing a draft", user)
    data = page_snapshot(draft)
    data["page"]["is_active"] = live.is_active  # publishing a draft never unpublishes the live page
    _apply(live, data["page"], PAGE_FIELDS_SKIP)
    live.save()
    _fill_page(live, data)
    draft.delete()
    return live


def publish_due():
    """Publish every draft whose 'Go live at' time has passed. Returns the live pages that changed."""
    done = []
    for draft in Page.objects.drafts().filter(publish_at__lte=timezone.now()).select_related("draft_of"):
        done.append(publish_draft(draft, scheduled=True))
    return done
