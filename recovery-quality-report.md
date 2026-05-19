# SEO recovery quality report

Generated: 2026-05-19

## What changed in this pass

- Controlled first-batch expansion is active; the sitemap now contains 221 URLs.
- Canonicals were audited against the live `seo.bdmnl.nl` path for every generated page.
- Index/noindex strategy was reviewed and documented; no aggressive noindex changes were applied.
- Internal crawl paths were strengthened through same-city and content-support linking in the generator.
- Duplicate metadata risks on known legacy/cluster URL pairs were cleaned in the generator.
- Breadcrumb schema was reviewed to avoid pointing at non-existing category URLs.

## Validation result

- HTML pages: 221
- Sitemap URLs: 221
- Index recommendations: {'index': 215, 'index-monitor': 6}
- Priority authority pages below score threshold: 0

## Topical cluster structure

- blog: 4 pages
- branding-design: 20 pages
- hosting: 21 pages
- online-marketing: 30 pages
- reclamebureau: 15 pages
- seo: 6 pages
- seo-bureau: 21 pages
- social-media: 5 pages
- social-media-beheer: 27 pages
- support: 9 pages
- webdesign: 17 pages
- webshop-laten-maken: 20 pages
- website-laten-maken: 26 pages

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

- Existing and first-batch city/service pages now use the premium editorial recovery template.
- First-batch cities have local market context through the generator; deeper manual copy should still happen cluster by cluster.
- Priority city/service authority pages reviewed: 24.

## Remaining risks

- Some historical recovery URLs intentionally overlap newer cluster URLs; keep monitoring Search Console before deciding on redirects or noindex.
- New first-batch pages are structurally unique by city/service, but should be monitored in Search Console before additional scaling.
- Blog/support recovery pages are useful for internal linking but are not yet deep authority articles.

## Recommended next step

Review the 20-city first batch in Search Console and approve one service cluster at a time for the next controlled expansion wave.
