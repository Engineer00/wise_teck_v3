---
name: new-section-layout
description: Add a new section type (layout) to the Wise-Teck site so a new page design becomes editable in the admin. Use when a new page or block design does not fit the existing 22 layouts.
---
1. Check the existing layouts first (`Section.LAYOUTS` in core/models.py, guide in core/layouts.py). Reuse one if it can show the design; only add a layout for a genuinely new structure.
2. Add the choice to `Section.LAYOUTS`. Store content in existing Section/Item fields where they fit; add a field only if none fits (then `makemigrations core` + `migrate`).
3. Create `templates/sections/<layout>.html`. Open general blocks with `{% include "sections/_open.html" %}`, use `sections/_head.html` for the heading and `partials/buttons.html` for buttons. All words come from fields; no inline styles.
4. Style it only in `static/css/wise-teck.css`, inside `@layer site`, using existing tokens (add a token to the top `:root` block if a new value is truly needed).
5. Add the layout to `GUIDE` in core/layouts.py: which fields it uses, their labels in that layout's terms, and what its cards are. If the section should show the editor's extra details (label + value rows), include `sections/_details.html` in the template and set `details=` (where the table appears) in its GUIDE entry; a test checks the two match.
6. If it needs seed content, add it in `seed_content.py`.
7. Verify: `py -3.13 manage.py test core` (the every-layout test renders it), open it in the admin (fields shown/hidden correctly), and screenshot it on a home and an inner page with `?static`.
