# SEO recovery quality report

Generated: 2026-05-19

## What changed in this pass

- No new pages were created; the sitemap remains at 128 URLs.
- Canonicals were audited against the live `seo.bdmnl.nl` path for every generated page.
- Index/noindex strategy was reviewed and documented; no aggressive noindex changes were applied.
- Internal crawl paths were strengthened through same-city and content-support linking in the generator.
- Duplicate metadata risks on known legacy/cluster URL pairs were cleaned in the generator.
- Breadcrumb schema was reviewed to avoid pointing at non-existing category URLs.

## Validation result

- HTML pages: 128
- Sitemap URLs: 128
- Index recommendations: {'index': 122, 'index-monitor': 6}
- Priority authority pages below score threshold: 0

## Topical cluster structure

- blog: 5 pages
- online-marketing: 19 pages
- reclamebureau: 15 pages
- seo: 6 pages
- seo-bureau: 21 pages
- social-media: 5 pages
- social-media-beheer: 16 pages
- support: 9 pages
- webdesign: 17 pages
- website-laten-maken: 15 pages

## Canonical and indexing notes

- All generated pages are self-canonical to `https://seo.bdmnl.nl/...`.
- All generated pages remain indexable for now because validation is clean and pages are in the recovery sitemap.
- Known historical overlap pairs are monitored rather than noindexed because they may still recover legacy search demand.

### Monitor legacy overlap pairs

- /online-marketing-middelburg/ overlaps with /online-marketing/online-marketing-middelburg/
- /seo/seo-bureau-rotterdam/ overlaps with /seo-bureau-rotterdam/
- /social-media/social-media-beheer-brielle/ overlaps with /social-media-beheer-brielle/

## Lowest quality scores to improve next

- /blog/content-marketing/ — score 82 — thin_content
- /blog/hoe-kun-je-een-eigen-blog-beginnen/ — score 82 — thin_content
- /blog/hoe-vaak-moet-je-je-website-updaten/ — score 82 — thin_content
- /blog/professionele-website-hosting-betrouwbaar-en-snel/ — score 82 — thin_content
- /blog/wordpress-waarom-is-dat-zo-populair/ — score 82 — thin_content
- /kennisbank/webdesign/ — score 82 — thin_content
- /online-marketing-middelburg/ — score 100 — monitor_overlap_with:/online-marketing/online-marketing-middelburg/
- /seo/seo-bureau-rotterdam/ — score 100 — monitor_overlap_with:/seo-bureau-rotterdam/
- /social-media/social-media-beheer-brielle/ — score 100 — monitor_overlap_with:/social-media-beheer-brielle/

## City page uniqueness notes

- Priority authority pages now include local market/scenario sections for Brielle, Rotterdam, Spijkenisse, Hellevoetsluis, Dordrecht, Goes, Middelburg and Breda.
- Non-priority cities still use fallback local context and should be upgraded gradually, city by city, before any further scaling.
- Priority city/service authority pages reviewed: 24.

## Remaining risks

- Some historical recovery URLs intentionally overlap newer cluster URLs; keep monitoring Search Console before deciding on redirects or noindex.
- Non-priority city pages are stable but less locally distinctive than the eight priority locations.
- Blog/support recovery pages are useful for internal linking but are not yet deep authority articles.

## Recommended next step

Use Search Console performance data to choose one cluster at a time for deeper manual copy improvements, starting with the highest-value overlap or priority-city pages rather than creating new URLs.
