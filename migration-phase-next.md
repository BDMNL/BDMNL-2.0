# BDMNL Migration Phase Next
## Status Report & Roadmap
*Generated: 2026-05-20 | BDMNL-2.0 repo | Netlify: meek-bublanina-442e19.netlify.app*

---

## 1. Executive Summary

| Metric | Count |
|---|---|
| Framework pages live (pages/) | 20 |
| Framework pages with 200! rewrite | 20 |
| Framework pages with canonical -> bdmnl.nl | 20 |
| Root conflict stubs already done | 2 |
| Root conflict stubs still needed | 14 |
| Old recovery/orange pages (total, non-framework) | 125 |
| Services with NO framework replacement yet | 4 |
| Sitemap SEO issues | 4 |
| Pages missing images | 19 (Cat task) |

---

## 2. Framework Pages - Current Live Status

All 20 framework pages are live, framework-first, and protected by 200! rewrites.
No landing.css loaded on any framework page. All canonicals point to bdmnl.nl.

| URL | Canonical | Framework | Images | Root Stub |
|---|---|---|---|---|
| /website-laten-maken-rotterdam/ | bdmnl.nl | YES | 3 | done |
| /seo-bureau-rotterdam/ | bdmnl.nl | YES | 0 | done |
| /webshop-laten-maken-spijkenisse/ | bdmnl.nl | YES | 0 | N/A |
| /webdesign-brielle/ | bdmnl.nl | YES | 0 | N/A |
| /webdesign-rotterdam/ | bdmnl.nl | YES | 0 | N/A |
| /online-marketing-delft/ | bdmnl.nl | YES | 0 | N/A |
| /website-laten-maken-brielle/ | bdmnl.nl | YES | 0 | needs stub |
| /website-laten-maken-spijkenisse/ | bdmnl.nl | YES | 0 | needs stub |
| /website-laten-maken-hellevoetsluis/ | bdmnl.nl | YES | 0 | needs stub |
| /website-laten-maken-delft/ | bdmnl.nl | YES | 0 | needs stub |
| /website-laten-maken-leiden/ | bdmnl.nl | YES | 0 | needs stub |
| /website-laten-maken-dordrecht/ | bdmnl.nl | YES | 0 | needs stub |
| /website-laten-maken-breda/ | bdmnl.nl | YES | 0 | needs stub |
| /seo-bureau-brielle/ | bdmnl.nl | YES | 0 | needs stub |
| /seo-bureau-spijkenisse/ | bdmnl.nl | YES | 0 | needs stub |
| /seo-bureau-hellevoetsluis/ | bdmnl.nl | YES | 0 | needs stub |
| /seo-bureau-delft/ | bdmnl.nl | YES | 0 | needs stub |
| /seo-bureau-leiden/ | bdmnl.nl | YES | 0 | needs stub |
| /seo-bureau-dordrecht/ | bdmnl.nl | YES | 0 | needs stub |
| /webshop-laten-maken-rotterdam/ | bdmnl.nl | YES | 0 | needs stub |

NOTE: Images missing on 19 pages = Cat task (YAML + content update per page).
NOTE: Root stubs on 14 pages are safety measure. The 200! rewrites already prevent recovery pages from serving.

---

## 3. Root Conflict Files - Deprecation Status

### Already Deprecated (safe stubs in place) - 2 pages
- website-laten-maken-rotterdam/index.html (commit c29aa28)
- seo-bureau-rotterdam/index.html (commit a4044d5)

### Needs Deprecation Stub - 14 pages
These root-level recovery files (20-24KB old orange HTML) are SHADOWED by 200! rewrites.
Netlify never serves them. Stubs needed for safety and to prevent future accidents.

Priority order for stubbing:
1. seo-bureau-brielle (24KB recovery, HIGH)
2. seo-bureau-delft (24KB recovery, HIGH)
3. seo-bureau-dordrecht (24KB recovery, HIGH)
4. seo-bureau-hellevoetsluis (24KB recovery, HIGH)
5. seo-bureau-leiden (24KB recovery, HIGH)
6. seo-bureau-spijkenisse (24KB recovery, HIGH)
7. webshop-laten-maken-rotterdam (24KB recovery, HIGH)
8. website-laten-maken-brielle (20KB recovery, HIGH)
9. website-laten-maken-breda (24KB recovery, HIGH)
10. website-laten-maken-delft (24KB recovery, HIGH)
11. website-laten-maken-dordrecht (24KB recovery, HIGH)
12. website-laten-maken-hellevoetsluis (24KB recovery, HIGH)
13. website-laten-maken-leiden (24KB recovery, HIGH)
14. website-laten-maken-spijkenisse (24KB recovery, HIGH)

Use the standard deprecation stub format:
<!DOCTYPE html>
<html lang="nl">
<!--
  DEPRECATED - This root-level file is no longer the source of truth.
  Framework version: pages/[slug]/index.html
  Netlify _redirects 200! rewrite routes /[slug]/ to pages/[slug]/
  This file exists only as a safety fallback - DO NOT EDIT HERE.
  Edit via YAML: content/[yaml-file].yaml
-->
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=/[slug]/">
  <link rel="canonical" href="https://bdmnl.nl/[slug]/">
  <title>[Page Title] - BDMNL</title>
</head>
<body>
  <p>Redirecting to <a href="/[slug]/">/[slug]/</a></p>
</body>
</html>

---

## 4. Sitemap Audit - Issues Found

Sitemap.xml hosted at seo.bdmnl.nl, 237 URLs. Issues found:

### 4a. Wrong canonical paths in sitemap (old nested paths - should be flat)
These 3 pages are listed under old nested paths, but 301! redirects make flat URLs canonical:

| Sitemap Entry (WRONG) | Should Be |
|---|---|
| /webdesign/webdesign-brielle/ | /webdesign-brielle/ |
| /webdesign/webdesign-rotterdam/ | /webdesign-rotterdam/ |
| /online-marketing/online-marketing-delft/ | /online-marketing-delft/ |

Risk: Google may index old paths and split crawl budget between old and new.
Fix: Update sitemap.xml with flat canonical paths.

### 4b. Missing from sitemap - 1 page
- /webshop-laten-maken-spijkenisse/ not in sitemap at all
Fix: Add entry to sitemap.xml.

### 4c. Duplicate sitemap entry - 1 page
- /seo-bureau-rotterdam/ appears twice:
  - https://seo.bdmnl.nl/seo/seo-bureau-rotterdam/ (old path - REMOVE)
  - https://seo.bdmnl.nl/seo-bureau-rotterdam/ (correct - KEEP)
Fix: Remove duplicate old path entry.

### 4d. Sitemap domain mismatch - NEEDS CLARIFICATION
- Sitemap uses seo.bdmnl.nl as base domain
- Framework canonical tags point to bdmnl.nl (no subdomain)
- Risk: If these are different domains/deploys, canonical mismatch can harm rankings.
- Action: Confirm with client whether seo.bdmnl.nl = bdmnl.nl (same Netlify deploy).
  If yes: update sitemap base URL to bdmnl.nl.
  If no: major issue - all canonicals and sitemap must match the SAME primary domain.

---

## 5. Redirect Audit - Current _redirects State

### 200! Rewrites (framework-first) - 20 rules, all verified:
All 20 framework pages have working 200! rewrites routing clean URLs to pages/ subfolder.
Routing confirmed: all pages return HTTP 200 and render framework HTML.

### 301! Redirects (URL mismatch) - 3 rules, verified working:
- /webdesign/webdesign-brielle/* -> /webdesign-brielle/:splat (live)
- /webdesign/webdesign-rotterdam/* -> /webdesign-rotterdam/:splat (live)
- /online-marketing/online-marketing-delft/* -> /online-marketing-delft/:splat (live)

### Missing redirects (future phases):
When new framework pages replace other nested-path recovery pages (webdesign cities beyond brielle/rotterdam, online-marketing cities beyond delft), additional 301s will be needed at that time.

---

## 6. Old Recovery System - What Can Phase Out

### 6a. Fully replaced by framework (20 pages) - safe to deprecate root files
See Section 3. All 20 have 200! rewrites. Only 2 have stubs so far.

### 6b. Remaining old recovery system - 125 non-framework root dirs

Service breakdown:

| Service | Recovery Dirs | Framework Done | Remaining |
|---|---|---|---|
| website-laten-maken | ~25 root dirs | 7 done | ~18 cities left |
| seo-bureau | ~24 root dirs | 8 done | ~18 cities left |
| webshop-laten-maken | 20 root dirs | 2 done (spijkenisse, rotterdam) | 18 cities left |
| online-marketing | 4 root dirs (small cities) | 1 done (delft) | 3 remaining |
| social-media-beheer | 26 root dirs | 0 done | 26 remaining |
| hosting | 20 root dirs | 0 done | 20 remaining |
| branding-design | 20 root dirs | 0 done | 20 remaining |

### 6c. Services with ZERO framework pages yet (4 services)
- social-media-beheer: 26 cities, no framework pages
- hosting: 20 cities, no framework pages
- branding-design: 20 cities, no framework pages
- webshop-laten-maken: 18 of 20 cities have no framework pages yet

---

## 7. Internal Link Consistency

### Current state:
- All CTA buttons on all framework pages point to https://www.bdmnl.nl/contact/ (verified)
- No cross-links between framework pages (each page is standalone)
- Old recovery pages have links to old recovery system (irrelevant once deprecated)

### Recommended for Phase D:
When generating new pages, add a related-services or other-cities section using only framework-first URLs to build internal link graph.

---

## 8. SEO Risk Areas

### HIGH RISK
1. Sitemap URL mismatch: 3 pages at old nested paths. Fix: update sitemap.xml.
2. Duplicate sitemap entry for seo-bureau-rotterdam. Fix: remove /seo/seo-bureau-rotterdam/ entry.
3. Missing sitemap entry for webshop-laten-maken-spijkenisse. Fix: add to sitemap.
4. Sitemap domain (seo.bdmnl.nl) vs canonical (bdmnl.nl) mismatch - needs client confirmation.

### MEDIUM RISK
5. Images missing on 19 of 20 framework pages - impacts visual engagement signals. Cat task.
6. 14 root-level recovery files still exist at 20-24KB each. While shadowed by rewrites, should be stubbed for hygiene. Claude task.

### LOW RISK
7. Encoding issues on non-Rotterdam pages - garbled Dutch chars possible. Cat should verify on content pass.
8. No structured data (JSON-LD) on any framework page - consider LocalBusiness schema in future.
9. No internal link graph between framework pages - isolated pages have lower PageRank distribution.

---

## 9. Recommended Next Cluster Rollout

### IMMEDIATE - Claude tasks (architecture/routing/cleanup):
- [ ] Add 14 deprecation stubs for root conflict files (Section 3)
- [ ] Fix sitemap.xml: correct 3 wrong paths, add 1 missing, remove 1 duplicate
- [ ] Confirm seo.bdmnl.nl vs bdmnl.nl domain strategy with client

### PHASE D - Next Page Generation (Cat + Claude collaboration):
Cat generates YAML + pages. Claude adds _redirects rules + stubs.

Brielle cluster (home city, highest commercial priority):
1. /online-marketing-brielle/ (new framework page)
2. /webshop-laten-maken-brielle/ (new framework page)
3. /webdesign-hellevoetsluis/ (new framework page)

Rotterdam/Delta cluster:
4. /online-marketing-rotterdam/ (new framework page)
5. /webshop-laten-maken-delft/ (new framework page)
6. /webshop-laten-maken-leiden/ (new framework page)
7. /webshop-laten-maken-dordrecht/ (new framework page)

Zeeland cluster:
8. /website-laten-maken-middelburg/ (new framework page)
9. /seo-bureau-middelburg/ (new framework page)
10. /website-laten-maken-goes/ (new framework page)
11. /seo-bureau-goes/ (new framework page)

### PHASE E - Online Marketing Expansion (Cat + Claude):
- /online-marketing-spijkenisse/
- /online-marketing-leiden/
- /online-marketing-dordrecht/
- /online-marketing-middelburg/
- /online-marketing-goes/
For each: Cat creates YAML + page, Claude adds 200! rewrite to _redirects.

### PHASE F - Social Media Beheer (Cat + Claude):
- 26 city pages
- All need new framework pages from scratch
- No existing framework template for social-media-beheer yet (Cat must create YAML schema first)
- Lowest current traffic - schedule after website/seo/webshop clusters done

### PHASE G - Hosting + Branding Design (Cat + Claude):
- hosting: 20 cities
- branding-design: 20 cities
- These have old recovery pages but likely low SEO traffic
- Migrate last, or evaluate whether these services are still active for bdmnl.nl

---

## 10. Architecture Rules (Permanent Reference)

### Responsibility Boundary

Cat handles:
- YAML files (content/)
- Page generation (pages/)
- FAQ content, images, internal copy
- Image token population: {{IMAGE_N_SRC}}, {{IMAGE_N_ALT}}
- Encoding corrections on content

Claude handles:
- _redirects (200!/301! rules, routing)
- sitemap.xml updates
- Deprecation stubs (root conflict files)
- Canonical strategy
- Migration planning documents

### Never touch:
- assets/css/landing.css
- framework/master-template.html (only for approved framework tasks)
- framework/design-tokens.css (only if required for framework styling)
- assets/css/bdmnl-design-system.css
- Old recovery pages (only stub/deprecate, never edit)

### QA URL (ONLY):
meek-bublanina-442e19.netlify.app
Never use deploy-preview-* URLs for verification.

### Netlify routing hierarchy:
_redirects 200! rules -> serve pages/ version transparently (URL unchanged in browser)
_redirects 301! rules -> permanent redirect (URL changes in browser)
Root static files -> only if no redirect rule matches (shadowed by 200! rules)
pages/ static files -> served via 200! rewrites

### Deprecation stub format for root conflict files:
See Section 3 for template.

---

## 11. Commit Log (All Sessions to Date)

| Commit | File | Action |
|---|---|---|
| f94f3e8 | framework/master-template.html | Added IMAGE token blocks |
| 8d2d3ed | framework/design-tokens.css | Added .bdmnl-section__img CSS |
| bb9110d | content/rotterdam-website.yaml | Added images section |
| 3d8b5e9 | pages/website-laten-maken-rotterdam/ | Regenerated with Unsplash images |
| 70ed1de | website-laten-maken-rotterdam/ (root) | Synced with pages/ version |
| 6b9b278 | data/migration-first-20-commercial.csv | Created migration CSV |
| c29aa28 | website-laten-maken-rotterdam/ (root) | Replaced with deprecation stub |
| a4044d5 | seo-bureau-rotterdam/ (root) | Replaced with deprecation stub |
| e48a533 | _redirects | Added 3x 301! + 1x 200! rules |

---

*End of migration-phase-next.md*
*Next action: Execute IMMEDIATE items in Section 9 (14 stubs + sitemap fixes)*

