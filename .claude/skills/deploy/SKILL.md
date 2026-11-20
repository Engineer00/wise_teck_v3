---
name: deploy
description: Deploy or update the Wise-Teck Django site on the Namecheap VPS (159.198.43.141), next to dehleze.store.
disable-model-invocation: true
---
1. Locally: tests pass (`py -3.13 manage.py test core`), work committed and pushed, `main` fast-forwarded.
2. The user runs server commands in PuTTY; give them the exact commands from DEPLOY.md one step at a time and ask for the output before the next step.
3. Never edit or remove anything of dehleze.store (`/etc/nginx/sites-available/dehleze`, its folders, its database). Only add `wiseteck` files. Always `nginx -t` before `systemctl reload nginx`.
4. First deploy: DEPLOY.md sections 1–9 in order. Update: the "Updating later" block (git pull, pip install, migrate, collectstatic, restart).
5. Never run `seed_content --reset` on the server (it replaces the client's edits).
6. Finish by checking: the site and /admin/ load over HTTPS, https://dehleze.store still works, /sitemap.xml and /robots.txt open.
