# ⚠️ DEPRECATED — OLD RECOVERY SYSTEM

> Do not edit. Do not use for QA. Replaced by the /framework master-template workflow.

---

## What is deprecated

The following files and folders belong to the **OLD recovery system** and must not be touched, edited, or used as references going forward:

- `seo.bdmnl.nl` recovery pages (external old deploy)
- All root-level city/service folders (e.g. `/seo-bureau-rotterdam/`, `/website-laten-maken-rotterdam/`)
- `assets/css/landing.css`
- `assets/css/premium-example.css`
- `assets/css/bdmnl-design-system.css`
- Recovery templates (any template not under `/framework/`)
- Old orange page templates
- Webflow-exported files

---

## The APPROVED new system

All new SEO landing pages are generated from the locked framework:

| File | Role |
|---|---|
| `framework/master-template.html` | Single source of truth — DO NOT redesign |
| `framework/design-tokens.css` | Locked CSS — DO NOT edit |
| `pages/[slug]/index.html` | Generated output — overwrite via YAML only |
| `content/[city]-[service].yaml` | Content tokens per page |
| `_redirects` | Clean URL routing |

---

## Do not test these URLs

- `seo.bdmnl.nl/*` — old recovery system
- Any root-level city folder served directly

## Test ONLY these framework URLs (Netlify main deploy)

- `/webdesign-brielle/`
- `/seo-bureau-rotterdam/`
- `/online-marketing-delft/`
- `/webshop-laten-maken-spijkenisse/`
- `/website-laten-maken-rotterdam/`

---

*Last updated: 2026-05-20 — Framework v1.1*
