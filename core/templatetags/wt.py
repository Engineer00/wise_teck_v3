"""Template helpers for the Wise-Teck v3 templates.

Text conventions (also explained in the admin help texts):
  hl      title + "words to colour"  -> words wrapped in <span class="accent">
  br      "Skills|Development"       -> Skills<br/>Development
  nobr    "Skills|Development"       -> Skills Development
  rich    **bold**                   -> <b>bold</b>   (inline text)
  paras   blank line = new paragraph, **bold** kept
"""

import re

from django import template
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from core import images, motifs, theme

register = template.Library()

_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)


def _rich(text):
    return _BOLD.sub(r"<b>\1</b>", escape(text or ""))


@register.filter
def hl(title, words):
    title = escape(title or "")
    words = (words or "").strip()
    if words:
        w = escape(words)
        if w in title:
            title = title.replace(w, f'<span class="accent">{w}</span>', 1)
    return mark_safe(title)


@register.filter
def br(text):
    return mark_safe(escape(text or "").replace("|", "<br/>"))


@register.filter
def nobr(text):
    return mark_safe(escape(text or "").replace("|", " "))


@register.filter
def rich(text):
    return mark_safe(_rich(text))


@register.filter
def paras(text):
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text or "") if b.strip()]
    return mark_safe("".join(f"<p>{_rich(b).replace(chr(10), '<br/>')}</p>" for b in blocks))


@register.filter
def mod(n, k):
    try:
        return int(n) % int(k)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0


@register.filter
def num2(n):
    try:
        return f"{int(n):02d}"
    except (TypeError, ValueError):
        return n


@register.filter
def longest(values):
    """True when any stat value is long text (switches the stat row to its text style)."""
    return any(len(v.title or "") > 10 for v in values)


@register.simple_tag(takes_context=True)
def motif(context, kind):
    return mark_safe(theme.recolor_markup(motifs.motif(kind), context.get("theme")) if kind else "")


@register.filter
def themed(colour, scheme):
    """A default palette colour in the active colour scheme."""
    return theme.recolor(colour, scheme) if scheme else colour


@register.simple_tag
def wave(sym, h, cls):
    return mark_safe(
        f'<svg class="{cls}" viewBox="0 0 1440 {h}" preserveAspectRatio="none" aria-hidden="true" '
        f'data-wave="{sym}"></svg>'
    )


def _page_of(url):
    url = (url or "").split("#", 1)[0]
    return url if url.startswith("/") else None


@register.filter
def nav_on(item, path):
    """True when this menu item (or one of its drop-down links) points to the current page."""
    if _page_of(item.url) == path and (path != "/" or item.url == "/"):
        return True
    return any(_page_of(c.url) == path and path != "/" for c in item.children.all())


@register.filter
def same_page(url, path):
    return _page_of(url) == path


@register.simple_tag
def srcset(url, slot):
    """srcset + sizes for an uploaded photo (WebP copies, core/images.py); nothing for links, SVG or GIF."""
    value = images.srcset(url)
    return format_html(' srcset="{}" sizes="{}"', value, images.DRAWN[slot]) if value else ""
