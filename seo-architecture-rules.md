# BDMNL SEO Architecture Rules
## Canonical Source of Truth for All Page Generation
*Version 1.0 | 2026-05-20 | BDMNL-2.0 repo*

---

## 1. Domain and Canonical Policy

### 1a. Current State (Confirmed from Live Source)

All framework pages in `pages/` use:
- `<link rel="canonical" href="https://bdmnl.nl/[slug]/">`
- `<meta property="og:url" content="https://bdmnl.nl/[slug]/">`
- JSON-LD `"url": "https://www.bdmnl.nl"` for the business entity
- Sitemap at `seo.bdmnl.nl` with entries using `https://seo.bdmnl.nl/[slug]/`

This creates a domain mismatch: canonical tags say `bdmnl.nl`, sitemap says `seo.bdmnl.nl`.

### 1b. Canonical Domain Decision (RULE)

**All framework pages canonicalize to `https://bdmnl.nl/[slug]/` — no www, no subdomain.**

This is already correct in all 20 framework pages. Do not change it.

Rationale:
- `bdmnl.nl` = primary business domain
- `seo.bdmnl.nl` = Netlify deploy subdomain, NOT the canonical domain
- `www.bdmnl.nl` = live Webflow site used for nav links, NOT used for canonical tags on SEO pages

All new pages must follow this pattern:
```html
<link rel="canonical" href="https://bdmnl.nl/[slug]/">
<meta property="og:url" content="https://bdmnl.nl/[slug]/">
```

### 1c. www vs non-www (Three Separate Conventions — All Correct)

- Nav/footer links in header: `https://www.bdmnl.nl/...` → points to live Webflow site (CORRECT)
- Canonical tags on framework pages: `https://bdmnl.nl/[slug]/` → no www (CORRECT)
- JSON-LD business entity url: `https://www.bdmnl.nl` → main site entity (CORRECT)

These three intentionally use different www conventions. Do not homogenize them.

### 1d. Sitemap Domain Risk

Sitemap at `seo.bdmnl.nl/sitemap.xml` uses `https://seo.bdmnl.nl/[slug]/` as URL base.
Canonical tags use `https://bdmnl.nl/[slug]/`.

Risk level: MEDIUM. Google treats sitemap URLs as hints, not directives. The HTML canonical is authoritative. However, Google may treat `seo.bdmnl.nl` as a separate domain and divide crawl budget.

Recommended fix (future): Update sitemap.xml base URL from `seo.bdmnl.nl` to `bdmnl.nl`. Requires confirmation that both domains point to the same Netlify deploy. Do not change until confirmed with client.

### 1e. Netlify QA URL (RULE)

`meek-bublanina-442e19.netlify.app` is the QA preview URL. It is NOT canonical.
- Never link to QA URLs from production pages
- Never set QA URL as canonical
- Only use this URL for verification purposes

---

## 2. Internal Linking Rules

### 2a. Current Internal Link Structure (Confirmed)

Each framework page currently contains:
- Header nav: 6 links to `www.bdmnl.nl/[section]/`
- Breadcrumb: Home > Service hub > Current page (3 levels, with schema markup)
- CTA buttons: All point to `https://www.bdmnl.nl/contact/`
- Footer: Navigatie, Diensten, Kennisbank, Contact — all `www.bdmnl.nl/...`
- Breadcrumb parent: Relative path e.g. `/website-laten-maken/` or `/seo/`
- Cross-links to other framework pages: NONE currently (this is the isolation gap to fix)

### 2b. Breadcrumb Parent Hub Links (RULE)

The breadcrumb uses relative paths to service hub pages. Use these mappings:

| Service | Breadcrumb Parent Label | Breadcrumb Parent HREF |
|---|---|---|
| website-laten-maken | Website laten maken | /website-laten-maken/ |
| seo-bureau | SEO bureau | /seo/ |
| webshop-laten-maken | Webshop laten maken | /webshop-laten-maken/ |
| webdesign | Webdesign | /webdesign/ |
| online-marketing | Online marketing | /online-marketing/ |
| social-media-beheer | Social media beheer | /social-media/ |

RULE: Never use `www.bdmnl.nl/diensten/[service]/` as the breadcrumb parent. Must be a same-domain hub path.

### 2c. Same-City Cross-Links (RULE — Phase D Onward)

When a city has 2+ framework pages, each page must link to the other service pages in that city.

Add a "Meer diensten in [city]" section in the page body (after main content, before FAQ).

RULE: Only link to framework pages that exist in `pages/`. Never link to old recovery pages.
RULE: Do not add a same-city link before the target page has been created and verified live.

Geographic clusters and their same-city link targets:

| City | Services with framework pages currently |
|---|---|
| Brielle | website ✅, seo ✅, webdesign ✅ |
| Spijkenisse | website ✅, seo ✅, webshop ✅ |
| Hellevoetsluis | website ✅, seo ✅ |
| Rotterdam | website ✅, seo ✅, webshop ✅, webdesign ✅ |
| Delft | website ✅, seo ✅, online-marketing ✅ |
| Leiden | website ✅, seo ✅ |
| Dordrecht | website ✅, seo ✅ |
| Breda | website ✅ |

Cross-links should be added to existing pages when a city cluster reaches 3+ pages.

Future template token: `{{SAME_CITY_LINKS}}` — Cat populates the link HTML, Claude adds token to master-template.

### 2d. Same-Service Nearby-City Cross-Links (RULE — Phase D Onward)

Each page should link to 2-3 geographically nearby cities offering the same service.

Geographic link clusters per service:

| City | Nearby city link targets (same service) |
|---|---|
| Brielle | Spijkenisse, Hellevoetsluis, Rotterdam |
| Spijkenisse | Brielle, Hellevoetsluis, Rotterdam |
| Hellevoetsluis | Brielle, Spijkenisse, Rotterdam |
| Rotterdam | Brielle, Spijkenisse, Delft |
| Delft | Rotterdam, Leiden, Den Haag |
| Leiden | Delft, Rotterdam, Den Haag |
| Dordrecht | Rotterdam, Breda, Gorinchem |
| Breda | Dordrecht, Rotterdam, Tilburg |
| Middelburg | Goes, Vlissingen, Zierikzee |
| Goes | Middelburg, Vlissingen, Zierikzee |

RULE: Only add nearby-city links when both the source and target page exist as framework pages.

Future template token: `{{NEARBY_CITY_LINKS}}` — Cat populates, Claude adds to template.

### 2e. Service Hub Links (RULE)

The breadcrumb parent link already provides the upward hub link. No additional hub links needed until dedicated framework hub pages exist.

When framework hub pages are created (e.g. `/website-laten-maken/` as a real framework page), all city pages for that service must link to the hub.

### 2f. Bulldog Media and BDMNL Entity Links (RULE)

- Van Bulldog Media naar BDMNL: always use full absolute URL `https://www.bdmnl.nl/van-bulldog-media-naar-bdmnl/`
- BDMNL business entity: link as `https://www.bdmnl.nl/` — not seo.bdmnl.nl
- Footer already handles entity links correctly — do not duplicate in page body

### 2g. Link Count Rules per Page

| Link type | Min | Max | Notes |
|---|---|---|---|
| Header nav links | 6 | 6 | Fixed in template |
| Footer links | ~12 | ~16 | Fixed in template |
| CTA buttons | 2 | 4 | All to bdmnl.nl/contact/ |
| Breadcrumb | 3 levels | 3 levels | Home > Service > Page |
| Same-city cross-links | 0 | 4 | Only real framework pages |
| Same-service nearby-city links | 0 | 3 | Only real framework pages |
| External links (non-bdmnl) | 0 | 2 | Avoid unless needed |
| nofollow links | 0 | 0 | Never use on internal links |

RULE: Never link to a page that does not yet exist as a live framework page in `pages/`.
RULE: Never use `rel="nofollow"` on internal bdmnl.nl links.
RULE: Never link to old recovery pages, root-level stubs, or QA URLs.

---

## 3. Sitemap Policy

### 3a. Which Framework Pages Must Appear

Every page in `pages/` with a 200! rewrite in `_redirects` must have exactly ONE entry in sitemap.xml.

Current count: 20 framework pages, all 20 are in sitemap after the last session's fix ✅.

### 3b. Sitemap Entry Format (RULE)

```xml
<url>
  <loc>https://seo.bdmnl.nl/[slug]/</loc>
  <lastmod>YYYY-MM-DD</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

- Use `lastmod` = date page was last committed
- Use `priority 0.8` for all framework SEO landing pages
- Use `priority 0.9` for the homepage

NOTE: When domain strategy is confirmed (seo.bdmnl.nl vs bdmnl.nl), update all `<loc>` to use `bdmnl.nl` base.

### 3c. Sitemap URL Rules (RULE)

- Always use flat paths: `/[slug]/` — NEVER nested paths like `/webdesign/webdesign-[city]/`
- One entry per page — no duplicates
- Sitemap URL must match the canonical href in the page HTML
- Old recovery pages that have been stubbed: URL stays in sitemap (now serves framework content via 200! rewrite)
- Old nested paths that have been 301'd: remove from sitemap, add flat path entry

### 3d. Sitemap Maintenance Rule (RULE)

After every batch of new framework pages is committed:
1. Add sitemap entries in the same commit session
2. Claude handles sitemap updates — Cat does not edit sitemap.xml
3. Never let sitemap fall more than one session behind

### 3e. Deprecated Pages in Sitemap

When a recovery page root file gets a deprecation stub, the URL itself remains the same. The sitemap entry is still valid — it now points to the URL that serves the framework page via 200! rewrite.

Do NOT remove these entries from the sitemap.

---

## 4. Redirect Policy

### 4a. Framework-First Rewrite — 200! Rule (RULE)

Every framework page in `pages/[slug]/` must have a 200! rewrite BEFORE going live:

```
/[slug]/*    /pages/[slug]/:splat    200!
```

This transparently serves the `pages/` version at the clean URL. The root-level old recovery file is completely shadowed.

RULE: Claude adds this to `_redirects` when a new framework page is created.
RULE: Cat does not edit `_redirects`.

Current state: All 20 framework pages have 200! rewrites ✅.

### 4b. Root Conflict Resolution — Deprecation Stub Rule (RULE)

When a framework page replaces a root-level recovery page:
1. 200! rewrite must exist (serves framework version)
2. Root-level `[slug]/index.html` must be replaced with a deprecation stub

Current state: 16 of 16 framework pages with root conflicts have stubs ✅.

Deprecation stub format:
```html
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
```

RULE: Never delete root-level folders outright. Only replace index.html with a stub.

### 4c. URL Mismatch Redirects — 301! Rule (RULE)

When an old recovery page lived at a nested path, add a 301 redirect when creating the flat framework page:

```
/old/nested/path/*    /flat-canonical-path/:splat    301!
```

Known nested path patterns and flat equivalents:

| Old nested pattern | New flat canonical |
|---|---|
| /webdesign/webdesign-[city]/ | /webdesign-[city]/ |
| /online-marketing/online-marketing-[city]/ | /online-marketing-[city]/ |
| /social-media/social-media-beheer-[city]/ | /social-media-beheer-[city]/ |
| /seo/seo-bureau-[city]/ | /seo-bureau-[city]/ |

Active 301! rules (all verified):
- `/webdesign/webdesign-brielle/*` → `/webdesign-brielle/:splat`
- `/webdesign/webdesign-rotterdam/*` → `/webdesign-rotterdam/:splat`
- `/online-marketing/online-marketing-delft/*` → `/online-marketing-delft/:splat`

RULE: Flat URLs are always canonical. Nested paths are always legacy. 301s are permanent.

### 4d. _redirects Rule Order (RULE)

- 200! rewrites must appear BEFORE any 301! rules for the same URL prefix
- More specific rules before more general rules
- Do not reorder existing rules

Template block for each new framework page (Claude adds this):
```
# [service]-[city]: framework page rewrite
/[slug]/*    /pages/[slug]/:splat    200!
```

If the old page was at a nested path, also add:
```
# [slug]: old nested path 301 redirect
/[old-nested-path]/*    /[slug]/:splat    301!
```

---

## 5. Cat Production Rules

### 5a. What Cat Does

Cat is responsible for:
- Creating YAML files in `content/` for each new page
- Generating HTML page files in `pages/[slug]/index.html`
- Populating all `{{TOKEN}}` values from the master template
- Writing FAQ content, headings, body copy, image alt text
- Setting breadcrumb parent label and href per service type
- Populating same-city and same-service links (once tokens are in template)

### 5b. YAML File Naming Convention (RULE)

```
content/[city]-[service].yaml
```

| Service | YAML suffix | Example |
|---|---|---|
| website-laten-maken | -website.yaml | brielle-website.yaml |
| seo-bureau | -seo.yaml | brielle-seo.yaml |
| webdesign | -webdesign.yaml | brielle-webdesign.yaml |
| webshop-laten-maken | -webshop.yaml | brielle-webshop.yaml |
| online-marketing | -online-marketing.yaml | brielle-online-marketing.yaml |
| social-media-beheer | -social-media.yaml | brielle-social-media.yaml |

### 5c. Required YAML Fields (All Must Be Present)

```yaml
slug: [service]-[city]
city: [City Display Name]
service: [Service Display Name]
h1: "..."
meta_title: "..."              # max 60 chars
meta_desc: "..."               # max 155 chars
meta_canonical: "https://bdmnl.nl/[slug]/"
breadcrumb_parent: "[Label]"
breadcrumb_parent_href: "/[hub]/"
intro_p1: "..."
intro_p2: "..."
section_1_h2: "..."
section_1_p: "..."
section_2_h2: "..."
section_2_p: "..."
section_3_h2: "..."
section_3_p: "..."
cta_headline: "..."
cta_subtext: "..."
cta_button: "..."
cta_href: "https://www.bdmnl.nl/contact/"
faq_1_q: "..."
faq_1_a: "..."
faq_2_q: "..."
faq_2_a: "..."
faq_3_q: "..."
faq_3_a: "..."
faq_4_q: "..."
faq_4_a: "..."
faq_5_q: "..."
faq_5_a: "..."
schema_service_name: "..."
schema_area_served: "[City]"
images:
  - src: "https://..."
    alt: "..."
  - src: "https://..."
    alt: "..."
  - src: "https://..."
    alt: "..."
```

RULE: Every field must be present. No YAML field may be left blank or missing.
RULE: `cta_href` is always `https://www.bdmnl.nl/contact/` — never change this.
RULE: `meta_canonical` must always be `https://bdmnl.nl/[slug]/` — never seo.bdmnl.nl, never www.

### 5d. Template Tokens — All Must Be Replaced (RULE)

The following tokens exist in master-template.html. Every single one must be replaced in the generated page. No `{{TOKEN}}` may remain in committed HTML output:

```
{{CITY}}                   From yaml.city
{{SERVICE}}                From yaml.service
{{H1}}                     From yaml.h1
{{META_TITLE}}             From yaml.meta_title
{{META_DESC}}              From yaml.meta_desc
{{META_CANONICAL}}         From yaml.meta_canonical (bdmnl.nl/[slug]/)
{{INTRO_P1}}               From yaml.intro_p1
{{INTRO_P2}}               From yaml.intro_p2
{{SECTION_1_H2}}           From yaml.section_1_h2
{{SECTION_1_P}}            From yaml.section_1_p
{{SECTION_2_H2}}           From yaml.section_2_h2
{{SECTION_2_P}}            From yaml.section_2_p
{{SECTION_3_H2}}           From yaml.section_3_h2
{{SECTION_3_P}}            From yaml.section_3_p
{{CTA_HEADLINE}}           From yaml.cta_headline
{{CTA_SUBTEXT}}            From yaml.cta_subtext
{{CTA_BUTTON}}             From yaml.cta_button
{{CTA_HREF}}               Always https://www.bdmnl.nl/contact/
{{FAQ_1_Q}} - {{FAQ_5_Q}}  From yaml.faq_*_q
{{FAQ_1_A}} - {{FAQ_5_A}}  From yaml.faq_*_a
{{BREADCRUMB_PARENT}}      From yaml.breadcrumb_parent
{{BREADCRUMB_PARENT_HREF}} From yaml.breadcrumb_parent_href
{{SCHEMA_SERVICE_NAME}}    From yaml.schema_service_name
{{SCHEMA_AREA_SERVED}}     From yaml.schema_area_served
{{IMAGE_1_SRC}}            From yaml.images[0].src
{{IMAGE_1_ALT}}            From yaml.images[0].alt
{{IMAGE_2_SRC}}            From yaml.images[1].src
{{IMAGE_2_ALT}}            From yaml.images[1].alt
{{IMAGE_3_SRC}}            From yaml.images[2].src
{{IMAGE_3_ALT}}            From yaml.images[2].alt
```

### 5e. Encoding Rules — Dutch Special Characters (CRITICAL)

Always use HTML entities in generated HTML. Never use raw UTF-8 characters:

| Character | HTML Entity |
|---|---|
| — (em dash) | `&mdash;` |
| é | `&eacute;` |
| ë | `&euml;` |
| ' left quote | `&lsquo;` |
| ' right quote/apostrophe | `&rsquo;` |
| … ellipsis | `&hellip;` |
| ä | `&auml;` |
| ö | `&ouml;` |
| ü | `&uuml;` |

Garbled sequences that indicate encoding failure:
- `\u00e2\u0080\u0094` should be `&mdash;`
- `\u00c3\u00a9` should be `&eacute;`
- `\u00c3\u00ab` should be `&euml;`
- `\u00e2\u0080\u0098` should be `&lsquo;`
- `\u00e2\u0080\u0099` should be `&rsquo;`

RULE: If garbled sequences appear in output, fix before committing.

### 5f. CTA Link Rule (ABSOLUTE — No Exceptions)

Every CTA button, "Neem contact op" link, and "Gratis gesprek" call to action must point to:
`https://www.bdmnl.nl/contact/`

This is the only valid CTA destination. No relative paths. No other contact pages. No exceptions.

### 5g. What Cat May NOT Touch (RULE)

Cat must never modify these files:
- `framework/master-template.html`
- `framework/design-tokens.css`
- `assets/css/landing.css`
- `assets/css/bdmnl-design-system.css`
- `_redirects`
- `sitemap.xml`
- `robots.txt`
- Root-level stub files (e.g. `seo-bureau-brielle/index.html`)
- Any file in `data/`
- `migration-phase-next.md`
- `seo-architecture-rules.md`

### 5h. What Cat Must Do After Generating a Page

After Cat commits a new `pages/[slug]/index.html`:

1. Notify Claude of the new slug
2. Claude adds 200! rewrite to `_redirects`
3. Claude adds 301! redirect if old page was at a nested path
4. Claude adds entry to `sitemap.xml`
5. Claude adds deprecation stub if a root recovery folder exists at that slug
6. Both Cat and Claude verify the page live on Netlify QA (`meek-bublanina-442e19.netlify.app`)

### 5i. Post-Generation Verification Checklist

Cat verifies before considering a page done:
- [ ] No `{{TOKEN}}` remains unreplaced
- [ ] `<link rel="canonical">` = `https://bdmnl.nl/[slug]/`
- [ ] `<meta property="og:url">` = `https://bdmnl.nl/[slug]/`
- [ ] All 3 images present with real src URLs (not placeholder divs)
- [ ] No `landing.css` referenced
- [ ] No raw UTF-8 Dutch characters — HTML entities only
- [ ] All CTAs point to `https://www.bdmnl.nl/contact/`
- [ ] Breadcrumb parent href is a real path (see 2b table)
- [ ] Basic HTML validity (no unclosed tags)
- [ ] JSON-LD block present with `@type: LocalBusiness`

Claude verifies after adding redirects:
- [ ] Page returns HTTP 200 on Netlify QA
- [ ] 301! redirect works (if applicable) — old path lands on flat path
- [ ] Sitemap contains the new entry
- [ ] No duplicate sitemap entries

---

## 6. Next Cluster Recommendation (Next 20 Pages)

### 6a. Priority Factors

1. Brielle = home city of BDMNL — highest brand authority, most internal link value
2. Complete a city cluster before moving on — maximizes cross-link density
3. Commercial value order: website > webshop > seo > webdesign > online-marketing
4. Geographic clusters: complete islands/regions before moving far away

### 6b. Recommended Next 20 Pages

**Cluster 1 — Brielle: complete the city (2 pages)**

| # | URL | YAML | Current gap |
|---|---|---|---|
| 1 | /webshop-laten-maken-brielle/ | brielle-webshop.yaml | No framework page |
| 2 | /online-marketing-brielle/ | brielle-online-marketing.yaml | No framework page |

After this: Brielle will have 5 services complete.
Cross-links can then be activated on all 5 Brielle pages.

**Cluster 2 — Spijkenisse: complete the cluster (2 pages)**

| # | URL | YAML | Current gap |
|---|---|---|---|
| 3 | /webdesign-spijkenisse/ | spijkenisse-webdesign.yaml | No framework page |
| 4 | /online-marketing-spijkenisse/ | spijkenisse-online-marketing.yaml | No framework page |

After this: Spijkenisse has 5 services complete.

**Cluster 3 — Hellevoetsluis: expand (3 pages)**

| # | URL | YAML | Current gap |
|---|---|---|---|
| 5 | /webdesign-hellevoetsluis/ | hellevoetsluis-webdesign.yaml | No framework page |
| 6 | /webshop-laten-maken-hellevoetsluis/ | hellevoetsluis-webshop.yaml | No framework page |
| 7 | /online-marketing-hellevoetsluis/ | hellevoetsluis-online-marketing.yaml | No framework page |

**Cluster 4 — Rotterdam: expand commercial hub (2 pages)**

| # | URL | YAML | Current gap |
|---|---|---|---|
| 8 | /online-marketing-rotterdam/ | rotterdam-online-marketing.yaml | No framework page |
| 9 | /webshop-laten-maken-delft/ | delft-webshop.yaml | No framework page (Delft cluster) |

**Cluster 5 — Delft/Leiden: expand South Holland (4 pages)**

| # | URL | YAML | Current gap |
|---|---|---|---|
| 10 | /webdesign-delft/ | delft-webdesign.yaml | No framework page |
| 11 | /webdesign-leiden/ | leiden-webdesign.yaml | No framework page |
| 12 | /webshop-laten-maken-leiden/ | leiden-webshop.yaml | No framework page |
| 13 | /online-marketing-leiden/ | leiden-online-marketing.yaml | No framework page |

**Cluster 6 — Dordrecht: expand (3 pages)**

| # | URL | YAML | Current gap |
|---|---|---|---|
| 14 | /webdesign-dordrecht/ | dordrecht-webdesign.yaml | No framework page |
| 15 | /webshop-laten-maken-dordrecht/ | dordrecht-webshop.yaml | No framework page |
| 16 | /online-marketing-dordrecht/ | dordrecht-online-marketing.yaml | No framework page |

**Cluster 7 — Breda: expand (4 pages)**

| # | URL | YAML | Current gap |
|---|---|---|---|
| 17 | /seo-bureau-breda/ | breda-seo.yaml | No framework page |
| 18 | /webdesign-breda/ | breda-webdesign.yaml | No framework page |
| 19 | /webshop-laten-maken-breda/ | breda-webshop.yaml | No framework page |
| 20 | /online-marketing-breda/ | breda-online-marketing.yaml | No framework page |

### 6c. For Each New Page — Claude's Actions

For each new page committed by Cat:

1. Add to `_redirects`:
```
/[slug]/*    /pages/[slug]/:splat    200!
```

2. If old page was at nested path, add:
```
/[old-nested]/*    /[slug]/:splat    301!
```

3. Add to `sitemap.xml`:
```xml
<url>
  <loc>https://seo.bdmnl.nl/[slug]/</loc>
  <lastmod>YYYY-MM-DD</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

4. If root recovery folder exists at same slug: add deprecation stub to `[slug]/index.html`.

### 6d. Cross-Link Activation Trigger

When a city cluster reaches 3+ framework pages:
- Claude updates master-template.html to add `{{SAME_CITY_LINKS}}` token (at bottom of main content, before FAQ)
- Cat regenerates all pages in that city cluster with the new token populated
- Cat also adds `{{NEARBY_CITY_LINKS}}` token values to each page

This is a collaborative step — do not activate until template has been updated by Claude first.

---

## 7. JSON-LD Structured Data Rules

### 7a. Current State (Confirmed)

All framework pages already include a LocalBusiness JSON-LD block from the master template:

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "BDMNL",
  "description": "{{SCHEMA_SERVICE_NAME}}",
  "url": "https://www.bdmnl.nl",
  "telephone": "+31850605627",
  "email": "info@bdmnl.nl",
  "areaServed": {
    "@type": "City",
    "name": "{{SCHEMA_AREA_SERVED}}"
  }
}
```

### 7b. Schema Token Values (RULE)

- `{{SCHEMA_SERVICE_NAME}}`: descriptive phrase, e.g. "Website laten maken in Brielle door BDMNL"
- `{{SCHEMA_AREA_SERVED}}`: city name only, e.g. "Brielle" — no province, no country

### 7c. Future Schema Improvements (Not Required Now)

These can be added in a future template update when Claude approves:
- `"address"` block: Krammer 8, 3232 HE Brielle
- `"geo"` coordinates for the served city
- `"openingHoursSpecification"`
- BreadcrumbList schema (breadcrumb is already present via itemprop markup)

Do not add these without a template task approved by Claude.

---

## 8. robots.txt and Crawl Rules

### 8a. Rules (RULE)

- Never add `noindex` to any framework page
- Never add `Disallow: /pages/` to robots.txt
- The `/pages/` directory is transparent via 200! rewrites — Google sees `/[slug]/`
- Do not directly link to `/pages/[slug]/` anywhere — only link to `/[slug]/`
- All framework pages are crawlable by default

---

## 9. Architecture Responsibility Matrix

| Task | Claude | Cat |
|---|---|---|
| master-template.html changes | YES | NO |
| design-tokens.css changes | YES (framework tasks only) | NO |
| YAML creation and editing | NO | YES |
| pages/ HTML generation | NO | YES |
| _redirects updates | YES | NO |
| sitemap.xml updates | YES | NO |
| Deprecation stubs | YES | NO |
| robots.txt changes | YES | NO |
| landing.css | NO — never touch | NO — never touch |
| Same-city link content (YAML) | NO | YES |
| Cross-link token in template | YES | NO |
| Image URLs in YAML | NO | YES |
| Encoding fixes | BOTH | BOTH |
| QA verification on Netlify | BOTH | BOTH |
| migration-phase-next.md | YES | NO |
| seo-architecture-rules.md | YES | NO |
| data/ directory | YES | NO |

---

*End of seo-architecture-rules.md*
*Version 1.0 — 2026-05-20*
*Next review: after Brielle cluster completion (20 pages batch)*
