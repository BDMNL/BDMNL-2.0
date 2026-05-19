# BDMNL SEO recovery validation report

Generated: 2026-05-19

## Scope

- Existing recovery infrastructure preserved: templates, shared CSS/JS, generated recovery pages, sitemap and robots flow.
- Search Console export files were not present in this workspace or tracked on `origin/main`; expansion therefore uses the existing recovery URL inventory plus the requested priority services, regions and cities.
- Temporary, preview and non-commercial URLs were not generated.
- Authority upgrade applied to website laten maken, SEO bureau and webdesign pages, with priority local content for Brielle, Rotterdam, Spijkenisse, Hellevoetsluis, Dordrecht, Goes, Middelburg and Breda.

## Output files

- `recovery-audit.csv`: 221 audited URLs and coverage rows.
- `missing-pages.csv`: 166 missing-before-expansion URLs generated.
- `cluster-plan.csv`: 344 next-generation cluster rows.
- `sitemap.xml`: updated with recovery URLs on `https://seo.bdmnl.nl`.

## Coverage

- Recovery pages generated: 207
- Supporting content pages: 9
- Support pages: 4
- Total HTML pages in sitemap scope: 221
- Redirect candidates flagged: 14

## Quality checks built into generation

- Canonical URL, OG tags and Twitter metadata.
- ProfessionalService, FAQPage and BreadcrumbList schema.
- CTA blocks, FAQ sections and internal related links.
- Shared BDMNL 2.0 styling and responsive layout.
- Local city and region references in headings, body copy and FAQ answers.
- Premium authority sections with local market context, regional scenarios, visual mockups and direct CTA buttons instead of fake inline forms.

## Validation performed

- Generator completed successfully.
- HTML parser validation target: 221 generated `index.html` files.
- Sitemap XML validation target: 221 URL entries.
- Priority coverage target: 15 cities x 6 service routes.
- CSV outputs generated with audit, missing-page and cluster-plan rows.

## Deployment notes

- `robots.txt` now points to `https://seo.bdmnl.nl/sitemap.xml`.
- Sitemap URLs now match the live recovery host instead of the primary production domain.
- Cluster URLs use `website-laten-maken-[city]`, `seo-bureau-[city]` and `social-media-beheer-[city]` without deleting or overwriting historical recovery routes.
