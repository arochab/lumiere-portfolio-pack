# GitHub Pages Quick Guide

## Recommended repo structure
- /site/index.html
- /exports/screenshots/*.png
- /docs/*.md
- /data (optional; keep data in Drive locally, don’t publish unless you want)

## Steps
1. Create a new GitHub repo: `lumiere-powerbi-portfolio`
2. Commit folders: `site/`, `exports/screenshots/`, `docs/`
3. Settings → Pages:
   - Source: Deploy from a branch
   - Branch: main, folder: `/site`
4. Replace image paths in `site/index.html` to match your screenshots.

Tip: keep screenshots < 1.5MB each for fast load.
