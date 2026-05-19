# BDMNL recovery UI layer report

Generated: 2026-05-19

## Scope

- Environment: `https://seo.bdmnl.nl`
- Page count preserved: 128 generated HTML pages
- Sitemap count preserved: 128 URLs
- SEO structure preserved: canonicals, robots, schema, FAQ sections, internal links and sitemap strategy
- No new bulk pages were created
- No Webflow or `www.bdmnl.nl` work was performed

## UI improvements

- Hero sections now use a more premium white/orange BDMNL visual language with subtle gradients, framed background treatment, stronger type scale and cleaner CTA grouping.
- Trust and authority sections now use refined cards, softer shadows, stronger spacing and more consistent hierarchy.
- CTA blocks now present clear conversion paths: plan a meeting, free website check and proposal/contact actions.
- Internal link sections now feel more like related expertise cards rather than technical link lists.
- Footer now has a stronger recovery-platform brand treatment, clearer contact details and quick CTAs.
- Mobile CSS now improves button sizing, hero flow, grid stacking, section spacing and readability.

## Screenshot examples

Screenshots were captured locally from the generated static recovery pages:

- `/opt/cursor/artifacts/bdmnl-recovery-ui/website-laten-maken-brielle-desktop.png`
- `/opt/cursor/artifacts/bdmnl-recovery-ui/seo-bureau-rotterdam-mobile.png`
- `/opt/cursor/artifacts/bdmnl-recovery-ui/webdesign-breda-desktop.png`

## Validation

- `python3 scripts/generate-city-pages.py`
- `python3 scripts/validate-recovery.py` -> errors=0, warnings=0
- `python3 scripts/audit-recovery-quality.py`
- `git diff --check`

## Remaining risks

- Historical overlap pairs remain monitored in `recovery-quality-report.md`.
- Non-priority city pages are stable but still use more fallback local content than the eight priority locations.
- The UI layer is intentionally CSS/component-based to preserve crawl structure; deeper content refinements should happen cluster by cluster.

## Recommended next step

Review the screenshots and choose one high-value cluster for manual copy/authority refinement before adding any more URLs.
