"""What each section layout shows, and which fields it uses.

The admin panel uses this to show only the fields a layout needs (with labels in that layout's terms)
and to explain what the cards/items under a section are. The templates in templates/sections/ are the
source of truth; keep this in step when a template changes.
"""
ALWAYS = ["page", "order", "layout", "is_active", "anchor", "spacing", "divider_after", "motif"]

HEAD = {"eyebrow": "Small label above the title", "title": "Title", "highlight": "Words in the title to colour",
        "lined": "Line under the title", "subtitle": "Text under the title"}
BTN1 = {"button_label": "Button text", "button_url": "Button link", "button_style": "Button style", "button_icon": "Button icon"}
BTN2 = {"button2_label": "Second button text", "button2_url": "Second button link", "button2_style": "Second button style",
        "button2_icon": "Second button icon"}
PHOTO = {"image": "Photo", "image_url": "…or photo link", "image_alt": "Photo description"}


def _(help, fields, items=None, item_help=""):
    return {"help": help, "fields": fields, "items": items or {}, "item_help": item_help}


GUIDE = {
    "home_hero": _("Top of the home page: heading, two buttons and the 3D coin with up to four tags (six = hexagon).",
                   {**HEAD, "subtitle": "Intro text", **BTN1, **BTN2},
                   {"group": "List", "icon": "Icon", "title": "Tag text"},
                   "Cards with List = “3D coin tags”: one per tag around the coin."),
    "page_hero": _("Top of an inner page: breadcrumb, heading, facts, buttons, and a photo (with badge or stats) or the 3D coin.",
                   {"crumbs": "Breadcrumb", **HEAD, "subtitle": "Intro text", **BTN1, **BTN2, "visual": "Visual (photo or 3D coin)",
                    **PHOTO, "image2": "Second (small) photo", "image2_url": "…or second photo link",
                    "badge_icon": "Photo badge icon", "badge_text": "Photo badge text", "stats_style": "Hero stats style"},
                   {"group": "List", "icon": "Icon", "title": "Text / value", "subtitle": "Stat label"},
                   "List “Hero facts” = chips under the intro. “Hero stats” = boxes under the photo (title = value, "
                   "subtitle = label; the badge is hidden when stats are shown). “3D coin tags” = tags when Visual is 3D coin."),
    "home_about": _("Home · About block: label, title, text, button and a framed photo.",
                    {**HEAD, "body": "Text", **BTN1, **PHOTO}),
    "home_ecosystem": _("Home · Ecosystem: circle diagram with the logo in the middle, program bubbles, and a card with a checklist.",
                        {**HEAD, "center_small": "Centre label (small line)", "center_big": "Centre label (big line)",
                         "center_url": "Centre label link", "list_title": "Card title", "body": "Card text",
                         "list_items": "Card checklist (one per line)", "button_label": "Card link text", "button_url": "Card link"},
                        {"icon": "Icon", "title": "Bubble text", "link_url": "Bubble link"},
                        "One card per bubble around the circle."),
    "home_programs": _("Home · Program cards with arrows between them and the “Move to …” pill below.",
                       {**HEAD, "item_label": "Link text on each card", "center_small": "Pill small line",
                        "center_big": "Pill text", "center_url": "Pill link", "button_icon": "Pill icon"},
                       {"icon": "Icon", "title": "Program name", "bullets": "Lines (one per line)", "image": "Photo",
                        "image_url": "…or photo link", "link_url": "Link", "link_label": "Link text (optional)"},
                       "One card per program."),
    "home_services": _("Home · Service buttons, a second heading, then photo tiles.",
                       {**HEAD, "sub_title": "Heading above the photo tiles"},
                       {"group": "List", "icon": "Icon (service buttons)", "title": "Text", "image": "Photo (tiles)",
                        "image_url": "…or photo link", "link_url": "Link"},
                       "List “Main list” = service buttons. List “Second list” = photo tiles."),
    "home_weekend": _("Home · Weekend courses banner: photo, label, title, text, button and feature icons.",
                      {**HEAD, **BTN1, **PHOTO}, {"icon": "Icon", "title": "Feature text"}, "One card per feature icon."),
    "home_stories": _("Home · Success stories slider. Stories come from Content → Success Stories.",
                      {"title": "Title", "highlight": "Words in the title to colour", "feed_limit": "How many stories (0 = all)",
                       "item_label": "Full-story link text"}),
    "home_partners": _("Home · Corporate collaborations (text + photo) and collaborator cards.",
                       {**HEAD, **BTN1, **PHOTO, "sub_title": "Collaborators heading"},
                       {"icon": "Icon (if no logo)", "title": "Name", "subtitle": "Line under the name", "image": "Logo image",
                        "image_url": "…or logo link", "logo_html": "Logo (HTML, advanced)", "link_url": "Link (makes it a call-to-action card)"},
                       "One card per collaborator."),
    "split": _("Text on one side; a quote card, photo or checklist on the other.",
               {"eyebrow": "Small label", "title": "Title", "highlight": "Words in the title to colour", "body": "Text",
                **BTN1, **BTN2, "visual": "Other side shows", "image_side": "Other side position", **PHOTO,
                "quote_text": "Quote", "quote_highlight": "Words in the quote to colour", "quote_author": "Quote name",
                "quote_role": "Line under the name", "quote_icon": "Quote icon", "list_title": "Checklist title",
                "list_items": "Checklist (one per line)"}),
    "cards": _("Heading and a grid of icon cards.",
               {**HEAD, "columns": "Cards per row", "numbered": "Number the cards", "item_label": "Default link text",
                "note": "Note box under the cards"},
               {"icon": "Icon", "title": "Title", "text": "Text", "link_label": "Link text", "link_url": "Link"},
               "One card each."),
    "steps": _("Heading and numbered steps joined by a line (e.g. the earning pathway).",
               {**HEAD, "item_label": "Step label (e.g. Step)", "note": "Note box under the steps"},
               {"icon": "Icon", "title": "Title", "text": "Text (optional)"}, "One card per step."),
    "program_strip": _("Heading and the three program cards. The cards come from Website → Programs "
                       "(edit them once, every page updates).",
                       {**HEAD, "item_label": "Link text on each card", "note": "Note box under the cards"}),
    "earning_blocks": _("Heading and numbered photo cards (earning blocks).",
                        {**HEAD, "item_label": "Label after the number", "note": "Note box under the cards"},
                        {"title": "Title", "text": "Text", "image": "Photo", "image_url": "…or photo link",
                         "link_label": "Link text", "link_url": "Link"}, "One card each."),
    "story_grid": _("Heading and a grid of success stories (from Content → Success Stories).",
                    {**HEAD, "feed_limit": "Stories per page (0 = 8)", "item_label": "Full-story link text"}),
    "placeholder": _("A clearly marked notice for content still to come.", {"title": "Title", "body": "Text"}),
    "cta": _("Purple call-to-action band with two buttons.", {**HEAD, "subtitle": "Text", **BTN1, **BTN2}),
    "contact": _("Contact details and the contact form (messages arrive in Inbox → Messages).",
                 {"form_title": "Form title", "form_fields": "Form labels", "list_items": "“Interested in” options (one per line)",
                  "button_label": "Send button text", "button_icon": "Send button icon"},
                 {"icon": "Icon", "title": "Label", "text": "Value", "link_url": "Link (tel:, mailto: …)"},
                 "One card per contact detail."),
    "blog_list": _("Heading and blog post cards (from Content → Blogs).",
                   {**HEAD, "feed_limit": "Posts per page (0 = 9)", "item_label": "Link text"}),
    "team": _("Heading and team member cards (from Content → Team).", {**HEAD, "feed_limit": "How many (0 = all)"}),
    "services_feed": _("Heading and service cards (from Content → Services).",
                       {**HEAD, "columns": "Cards per row", "feed_limit": "How many (0 = all)", "item_label": "Link text"}),
}
