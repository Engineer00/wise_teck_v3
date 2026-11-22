"""Forms for the Wise-Teck admin panel (ported from the original site's panel).

Every form is built from its model; StyledForm gives each widget the panel's classes, so new model
fields appear in the panel automatically.
"""

from django import forms
from django.forms import inlineformset_factory, modelform_factory

from .. import theme
from ..models import (
    BlogPost,
    ContactMessage,
    Course,
    Detail,
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

try:
    from PIL import Image as PilImage
except Exception:  # Pillow is optional for this check
    PilImage = None


class StyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            field.full = isinstance(w, forms.Textarea)
            if isinstance(w, forms.CheckboxInput):
                w.attrs.setdefault("class", "ap-check")
            elif isinstance(w, forms.ClearableFileInput):
                w.attrs.setdefault("class", "ap-file")
            elif isinstance(w, forms.Textarea):
                w.attrs.setdefault("class", "ap-input ap-textarea")
                w.attrs.setdefault("rows", 4)
            else:
                w.attrs.setdefault("class", "ap-input")


def styled(model, fields, widgets=None, base=StyledForm):
    return modelform_factory(model, form=base, fields=fields, widgets=widgets or {})


def date_picker(field):
    field.widget = forms.DateTimeInput(attrs={"class": "ap-input", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
    field.input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]


class BlogBase(StyledForm):
    """Date-and-time pickers for 'Go live at' and the blog's display date."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("published_at", "publish_at"):
            if name in self.fields:
                date_picker(self.fields[name])


# ----------------------------------------------------------------- content from the original site
SuccessStoryForm = styled(
    SuccessStory,
    (
        "title",
        "slug",
        "client_name",
        "category",
        "short_description",
        "description",
        "image",
        "image_url",
        "display_order",
        "is_featured",
        "is_active",
        "publish_at",
    ),
    widgets={
        "slug": forms.TextInput(attrs={"placeholder": "Auto-generated if blank"}),
        "description": forms.Textarea(attrs={"rows": 10}),
    },
    base=BlogBase,
)

TeamMemberForm = styled(
    TeamMember,
    ("name", "designation", "service", "display_order", "short_description", "description", "image", "is_active"),
)


BlogPostForm = styled(
    BlogPost,
    (
        "title",
        "slug",
        "author",
        "category",
        "published_at",
        "short_description",
        "content",
        "featured_image",
        "is_featured",
        "is_active",
        "publish_at",
    ),
    widgets={
        "slug": forms.TextInput(attrs={"placeholder": "Auto-generated if blank"}),
        "content": forms.Textarea(attrs={"rows": 18}),
    },
    base=BlogBase,
)


class ServiceBase(StyledForm):
    """Same check as the original panel: the icon may be an SVG, otherwise it must be a real image."""

    def clean_icon_file(self):
        f = self.cleaned_data.get("icon_file")
        if not f or f is False or not hasattr(f, "content_type"):
            return f
        if f.name.lower().endswith((".svg", ".svgz")) or PilImage is None:
            return f
        try:
            PilImage.open(f).verify()
            f.seek(0)
        except Exception:
            raise forms.ValidationError("Upload an SVG or a valid image file.") from None
        return f


ServiceForm = styled(
    Service,
    ("name", "short_description", "image", "icon_file", "icon", "link_url", "display_order", "is_active"),
    base=ServiceBase,
)

CourseForm = styled(
    Course,
    (
        "name",
        "short_description",
        "icon",
        "duration",
        "fee",
        "schedule",
        "start_date",
        "link_url",
        "display_order",
        "is_active",
    ),
    widgets={"start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")},
)

ContactMessageForm = styled(ContactMessage, ("name", "email", "phone", "interest", "message", "page", "is_read"))

# ----------------------------------------------------------------- website structure (v2)
RESERVED_SLUGS = {
    "admin",
    "adminpanel",
    "django-admin",
    "static",
    "media",
    "preview",
    "robots-txt",
    "sitemap-xml",
    "sitemap",
    "robots",
    "api",
    "login",
    "logout",
    "success-stories-detail",
}


class PageBase(StyledForm):
    """Live pages: address and Published. Drafts: no address (they use the live page's), plus 'Go live at'."""

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip().lower()
        if slug in RESERVED_SLUGS:
            raise forms.ValidationError("This address is used by the system. Please choose another one.")
        return slug

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.is_draft:
            for name in ("slug", "is_active"):
                self.fields.pop(name, None)
            date_picker(self.fields["publish_at"])
        else:
            self.fields.pop("publish_at", None)


PageForm = styled(
    Page,
    (
        "title",
        "slug",
        "meta_description",
        "is_active",
        "publish_at",
        "share_title",
        "share_description",
        "share_image",
        "noindex",
        "canonical_url",
    ),
    base=PageBase,
    widgets={
        "meta_description": forms.Textarea(attrs={"rows": 2, "maxlength": 300}),
        "share_description": forms.Textarea(attrs={"rows": 2, "maxlength": 300}),
    },
)

RedirectForm = styled(Redirect, ("old_path", "new_path", "permanent", "is_active"))

SECTION_FIELDS = (
    "page",
    "order",
    "layout",
    "is_active",
    "anchor",
    "spacing",
    "divider_after",
    "motif",
    "crumbs",
    "eyebrow",
    "title",
    "highlight",
    "lined",
    "subtitle",
    "body",
    "note",
    "list_title",
    "list_items",
    "button_label",
    "button_url",
    "button_style",
    "button_icon",
    "button2_label",
    "button2_url",
    "button2_style",
    "button2_icon",
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
    "quote_text",
    "quote_highlight",
    "quote_author",
    "quote_role",
    "quote_icon",
    "center_small",
    "center_big",
    "center_url",
    "columns",
    "numbered",
    "item_label",
    "sub_title",
    "feed_limit",
    "form_title",
    "form_fields",
)
SectionForm = styled(
    Section,
    SECTION_FIELDS,
    widgets={
        "subtitle": forms.Textarea(attrs={"rows": 2}),
        "crumbs": forms.Textarea(attrs={"rows": 3}),
        "quote_text": forms.Textarea(attrs={"rows": 2}),
        "note": forms.Textarea(attrs={"rows": 2}),
        "form_fields": forms.Textarea(attrs={"rows": 5}),
        "body": forms.Textarea(attrs={"rows": 6}),
    },
)

ItemFormSet = inlineformset_factory(
    Section,
    Item,
    form=StyledForm,
    extra=1,
    can_delete=True,
    fields=(
        "group",
        "order",
        "is_active",
        "icon",
        "title",
        "subtitle",
        "text",
        "bullets",
        "image",
        "image_url",
        "link_label",
        "link_url",
        "logo_html",
    ),
    widgets={
        "text": forms.Textarea(attrs={"rows": 3}),
        "bullets": forms.Textarea(attrs={"rows": 3}),
        "logo_html": forms.Textarea(attrs={"rows": 2}),
    },
)

# extra details: label + value rows the editor adds to a section (shown as a small table where the layout has one)
DetailFormSet = inlineformset_factory(
    Section, Detail, form=StyledForm, extra=2, can_delete=True, fields=("label", "value", "order")
)

ProgramForm = styled(Program, ("title", "text", "icon", "link_url", "order", "is_active"))


class NavBase(StyledForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = NavItem.objects.filter(parent__isnull=True)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        self.fields["parent"].queryset = qs
        self.fields["parent"].empty_label = "— Top menu item —"


NavItemForm = styled(NavItem, ("label", "url", "parent", "order", "is_active"), base=NavBase)

FooterColumnForm = styled(FooterColumn, ("title", "order"))
FooterLinkFormSet = inlineformset_factory(
    FooterColumn, FooterLink, form=StyledForm, extra=2, can_delete=True, fields=("label", "url", "order")
)


class SiteSettingsBase(StyledForm):
    """Site Settings: colour pickers for the custom scheme, and a check that the colours keep text readable."""

    COLOURS = ("color_primary", "color_accent", "color_dark")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.COLOURS:
            self.fields[name].widget = forms.TextInput(attrs={"type": "color", "class": "ap-input ap-color"})

    def clean(self):
        data = super().clean()
        if data.get("color_scheme") != theme.CUSTOM:
            return data
        colours = [data.get(n) or "" for n in self.COLOURS]
        bad = [n for n, v in zip(self.COLOURS, colours, strict=True) if not theme.HEX.match(v)]
        for name in bad:
            self.add_error(name, "Choose a colour.")
        if not bad:
            for problem in theme.check_contrast(*colours):
                self.add_error("color_scheme", problem)
        return data


SiteSettingsForm = styled(SiteSettings, "__all__", base=SiteSettingsBase)
