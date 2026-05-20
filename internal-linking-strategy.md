# BDMNL Internal Linking Strategy
## Architecture & Rollout Plan
*Version 1.0 | 2026-05-20 | BDMNL-2.0 repo*

---

## 0. Purpose and Scope

This document defines the complete internal linking architecture for all BDMNL framework pages. It covers same-city linking, same-service nearby-city linking, hub page structure, link placement rules, future template tokens, rollout triggers, and SEO risks.

**This is planning only. No live pages are changed until cluster thresholds are met and the template is updated by Claude.**

---

## 1. Current Cluster State (Live Framework Pages)

From `pages/` directory as of 2026-05-20:

### By City

| City | Services live | Count | Cross-link ready? |
|---|---|---|---|
| Rotterdam | website, seo, webshop, webdesign | 4 | YES (threshold = 3) |
| Brielle | website, seo, webdesign | 3 | YES |
| Delft | website, seo, online-marketing | 3 | YES |
| Spijkenisse | website, seo, webshop | 3 | YES |
| Dordrecht | website, seo | 2 | Not yet |
| Hellevoetsluis | website, seo | 2 | Not yet |
| Leiden | website, seo | 2 | Not yet |
| Breda | website | 1 | Not yet |

### By Service

| Service | Cities live | Count | Nearby-city links ready? |
|---|---|---|---|
| website-laten-maken | brielle, spijkenisse, hellevoetsluis, rotterdam, delft, leiden, dordrecht, breda | 8 | YES |
| seo-bureau | brielle, spijkenisse, hellevoetsluis, rotterdam, delft, leiden, dordrecht | 7 | YES |
| webdesign | brielle, rotterdam | 2 | Not yet (threshold = 3) |
| webshop-laten-maken | rotterdam, spijkenisse | 2 | Not yet |
| online-marketing | delft | 1 | Not yet |

---

## 2. Same-City Linking Rules

### 2a. Concept

Every framework page in a city cluster must link to every other framework page in the same city. This creates a fully connected city graph, maximising PageRank flow within the cluster and signalling topical authority for that city.

### 2b. Activation Threshold

**Same-city links activate when a city has 3 or more live framework pages.**

| City page count | Action |
|---|---|
| 1 | No same-city links |
| 2 | No same-city links |
| 3+ | Add {{SAME_CITY_LINKS}} block to ALL pages in that city |

Currently eligible: Rotterdam, Brielle, Delft, Spijkenisse

### 2c. Link Block Format

Place a "Meer diensten in [City]" section after Section 3 content, before the FAQ block:

```html
<section class="bdmnl-section bdmnl-section--related">
  <div class="bdmnl-container">
    <h2 class="bdmnl-section__title">Meer diensten in {{CITY}}</h2>
    <ul class="bdmnl-related-links">
      {{SAME_CITY_LINKS}}
    </ul>
  </div>
</section>
```

Each link item:
```html
<li><a href="/[service]-[city]/">[Service label] [City]</a></li>
```

### 2d. Anchor Text Rules

| Service | Anchor text format |
|---|---|
| website-laten-maken | Website laten maken [City] |
| seo-bureau | SEO bureau [City] |
| webdesign | Webdesign [City] |
| webshop-laten-maken | Webshop laten maken [City] |
| online-marketing | Online marketing [City] |
| social-media-beheer | Social media beheer [City] |

RULE: Never use "klik hier", "meer info", or bare URLs as anchor text.
RULE: No duplicate anchor text on the same page.
RULE: Anchor text must differ from the page's own H1.

### 2e. Same-City Link Maps (Current)

**Rotterdam (4 pages — 3 links each):**

| Page | Links to |
|---|---|
| /website-laten-maken-rotterdam/ | SEO bureau Rotterdam, Webshop laten maken Rotterdam, Webdesign Rotterdam |
| /seo-bureau-rotterdam/ | Website laten maken Rotterdam, Webshop laten maken Rotterdam, Webdesign Rotterdam |
| /webshop-laten-maken-rotterdam/ | Website laten maken Rotterdam, SEO bureau Rotterdam, Webdesign Rotterdam |
| /webdesign-rotterdam/ | Website laten maken Rotterdam, SEO bureau Rotterdam, Webshop laten maken Rotterdam |

**Brielle (3 pages — 2 links each):**

| Page | Links to |
|---|---|
| /website-laten-maken-brielle/ | SEO bureau Brielle, Webdesign Brielle |
| /seo-bureau-brielle/ | Website laten maken Brielle, Webdesign Brielle |
| /webdesign-brielle/ | Website laten maken Brielle, SEO bureau Brielle |

*When /webshop-laten-maken-brielle/ and /online-marketing-brielle/ go live, all 5 Brielle pages update.*

**Delft (3 pages — 2 links each):**

| Page | Links to |
|---|---|
| /website-laten-maken-delft/ | SEO bureau Delft, Online marketing Delft |
| /seo-bureau-delft/ | Website laten maken Delft, Online marketing Delft |
| /online-marketing-delft/ | Website laten maken Delft, SEO bureau Delft |

**Spijkenisse (3 pages — 2 links each):**

| Page | Links to |
|---|---|
| /website-laten-maken-spijkenisse/ | SEO bureau Spijkenisse, Webshop laten maken Spijkenisse |
| /seo-bureau-spijkenisse/ | Website laten maken Spijkenisse, Webshop laten maken Spijkenisse |
| /webshop-laten-maken-spijkenisse/ | Website laten maken Spijkenisse, SEO bureau Spijkenisse |

### 2f. Update Trigger

When a new page goes live in a city already at 3+ pages, ALL existing pages in that city must be updated to include the new page as a cross-link. Cat updates the YAML; Claude does not regenerate without a Cat content update.

---

## 3. Same-Service Nearby-City Linking

### 3a. Concept

Each framework page links to 2–3 geographically nearby cities offering the same service. This builds geographic cluster signals, drives crawl discovery, and prevents city pages from being orphans.

### 3b. Activation Threshold

**Nearby-city links activate when a service has 3 or more live framework pages.**

| Pages in service | Action |
|---|---|
| 1–2 | No nearby-city links |
| 3+ | Add {{NEARBY_CITY_LINKS}} block to all pages in that service |

Currently eligible: website-laten-maken (8 cities), seo-bureau (7 cities)

### 3c. Link Block Format

Place directly below the same-city block (or after Section 3 if no same-city block):

```html
<section class="bdmnl-section bdmnl-section--nearby">
  <div class="bdmnl-container">
    <p class="bdmnl-nearby-label">{{SERVICE}} ook beschikbaar in:</p>
    <ul class="bdmnl-nearby-links">
      {{NEARBY_CITY_LINKS}}
    </ul>
  </div>
</section>
```

### 3d. Geographic Neighbor Maps

#### website-laten-maken (8 cities live)

| Page | Links to (nearest 3) |
|---|---|
| /website-laten-maken-brielle/ | Spijkenisse, Hellevoetsluis, Rotterdam |
| /website-laten-maken-spijkenisse/ | Brielle, Hellevoetsluis, Rotterdam |
| /website-laten-maken-hellevoetsluis/ | Brielle, Spijkenisse, Rotterdam |
| /website-laten-maken-rotterdam/ | Brielle, Spijkenisse, Delft |
| /website-laten-maken-delft/ | Rotterdam, Leiden, Dordrecht |
| /website-laten-maken-leiden/ | Delft, Rotterdam, Dordrecht |
| /website-laten-maken-dordrecht/ | Rotterdam, Leiden, Breda |
| /website-laten-maken-breda/ | Dordrecht, Rotterdam, Leiden |

#### seo-bureau (7 cities live)

| Page | Links to (nearest 3) |
|---|---|
| /seo-bureau-brielle/ | Spijkenisse, Hellevoetsluis, Rotterdam |
| /seo-bureau-spijkenisse/ | Brielle, Hellevoetsluis, Rotterdam |
| /seo-bureau-hellevoetsluis/ | Brielle, Spijkenisse, Rotterdam |
| /seo-bureau-rotterdam/ | Brielle, Spijkenisse, Delft |
| /seo-bureau-delft/ | Rotterdam, Leiden, Dordrecht |
| /seo-bureau-leiden/ | Delft, Rotterdam, Dordrecht |
| /seo-bureau-dordrecht/ | Rotterdam, Leiden, Breda (when live) |

#### webdesign (2 cities — NOT YET ELIGIBLE)

Add when a 3rd webdesign city is live (Spijkenisse or Hellevoetsluis recommended).

| Page | Will link to (when eligible) |
|---|---|
| /webdesign-brielle/ | Rotterdam, Spijkenisse, Hellevoetsluis |
| /webdesign-rotterdam/ | Brielle, Delft, Spijkenisse |

#### webshop-laten-maken (2 cities — NOT YET ELIGIBLE)

Add when a 3rd webshop city is live (Brielle or Hellevoetsluis recommended).

| Page | Will link to (when eligible) |
|---|---|
| /webshop-laten-maken-rotterdam/ | Spijkenisse, Brielle, Delft |
| /webshop-laten-maken-spijkenisse/ | Rotterdam, Brielle, Hellevoetsluis |

#### online-marketing (1 city — NOT YET ELIGIBLE)

Add when Rotterdam and Spijkenisse or Leiden go live for this service.

### 3e. Anchor Text Rules

Format: "[Service label] [City]" — e.g. "Website laten maken Spijkenisse"

RULE: The anchor text must include the city name.
RULE: Never link to the current page itself.
RULE: Use the exact canonical slug: /[service]-[city]/

---

## 4. Hub Page Structure

### 4a. Concept

Hub pages sit one level above city pages. They link to all city pages for a service and receive upward breadcrumb links from city pages. Until hub framework pages are built, current recovery pages serve as breadcrumb targets only.

### 4b. Planned Framework Hub Pages (Future Phase H)

| Hub URL | Service | Breadcrumb label used today | Priority |
|---|---|---|---|
| /website-laten-maken/ | Website laten maken | Website laten maken | HIGH |
| /seo/ | SEO bureau | SEO bureau | HIGH |
| /webshop-laten-maken/ | Webshop laten maken | Webshop laten maken | HIGH |
| /webdesign/ | Webdesign | Webdesign | MEDIUM |
| /online-marketing/ | Online marketing | Online marketing | MEDIUM |
| /social-media-beheer/ | Social media beheer | Social media beheer | LOW |
| /hosting/ | Hosting | Hosting | LOW |

### 4c. Hub Page Link Structure

Each hub page links to ALL live city pages for its service. City pages link back via breadcrumb only.

Hub → city (many links down)
City → hub (one link up via breadcrumb)
City ↔ city (same-city + nearby-city blocks)

Do not add extra hub links in the city page body — only the breadcrumb parent link is needed.

### 4d. Hub Page Token: {{SERVICE_HUB_LINKS}}

Used on hub pages only — NOT in the city page template. Cat generates the city list in hub YAML.

```yaml
service_hub_links:
  - href: "/website-laten-maken-rotterdam/"
    label: "Website laten maken Rotterdam"
  - href: "/website-laten-maken-brielle/"
    label: "Website laten maken Brielle"
```

Conditional rule: Omit any city not yet live as a framework page.

---

## 5. Link Placement Rules

### 5a. Link Zone Order per Page

```
[Header nav]              Fixed — links to www.bdmnl.nl sections
[Breadcrumb]              Hub parent + current page (schema markup)
[Body content]            No links by default (max 2 with editorial reason)
[Same-city block]         {{SAME_CITY_LINKS}} — eligible cities only
[Nearby-city block]       {{NEARBY_CITY_LINKS}} — eligible services only
[CTA section]             Always www.bdmnl.nl/contact/ only
[FAQ]                     No links — plain text only
[Footer]                  Fixed — links to www.bdmnl.nl
```

### 5b. Body Content Links (RULE)

RULE: Do not add cross-links inside paragraph text (SECTION_1_P through SECTION_3_P). Inline city-page links look spammy and dilute reading flow.
RULE: If a contextual link is needed, link only to www.bdmnl.nl/kennisbank/[article]/ — never to another city page from within body copy.

### 5c. CTA Links (RULE — Absolute)

Every CTA button must point to: https://www.bdmnl.nl/contact/
No exceptions. No city-specific contact pages.
Never use a CTA as a navigation link to another framework page.

### 5d. Footer Links (RULE)

Footer is for global navigation only. Do not add city-specific cross-links to the footer.

### 5e. Maximum Link Count per Page

| Zone | Links | Modifiable? |
|---|---|---|
| Header nav | 6 | NO — template fixed |
| Breadcrumb | 2 clickable | NO — template fixed |
| Body contextual | 0 (max 2 with reason) | Only exceptional cases |
| Same-city block | 0–4 | YES — Cat populates |
| Nearby-city block | 0–3 | YES — Cat populates |
| CTA buttons | 2–4 | NO — all to contact/ |
| Footer | ~12 | NO — template fixed |
| **Total max** | **~31** | Stay below 35 |

RULE: Total internal links must stay below 35. Above 35 Google may discount individual link value.
RULE: Never use rel="nofollow" on internal bdmnl.nl links.
RULE: Never link to old recovery pages, stubs, or QA URLs.

### 5f. External Link Rules

RULE: Maximum 2 external links per page.
RULE: Do not link to competitor sites.
RULE: No external links in same-city or nearby-city blocks.

---

## 6. Future Template Tokens

### 6a. {{SAME_CITY_LINKS}}

Purpose: Renders links to other framework pages in the same city.
Placement: After Section 3, before FAQ.
Activation: City has 3+ framework pages.
Empty state: Omit entire section block — never output empty ul.

YAML field:
```yaml
same_city_links:
  - href: "/seo-bureau-brielle/"
    label: "SEO bureau Brielle"
  - href: "/webdesign-brielle/"
    label: "Webdesign Brielle"
```

Conditional rule: If same_city_links is absent or empty, omit the entire section.
Minimum: 2 items — if only 1 item, omit the section.

### 6b. {{NEARBY_CITY_LINKS}}

Purpose: Renders links to same service in nearby cities.
Placement: After same-city block (or after Section 3 if no same-city block).
Activation: Service has 3+ framework pages.
Empty state: Omit entire section — never output empty ul.

YAML field:
```yaml
nearby_city_links:
  - href: "/website-laten-maken-spijkenisse/"
    label: "Website laten maken Spijkenisse"
  - href: "/website-laten-maken-hellevoetsluis/"
    label: "Website laten maken Hellevoetsluis"
  - href: "/website-laten-maken-rotterdam/"
    label: "Website laten maken Rotterdam"
```

Conditional rule: If nearby_city_links is absent or empty, omit the section.
Minimum: 2 items — if only 1 item, omit the section.

### 6c. {{SERVICE_HUB_LINKS}}

Purpose: On hub pages only — renders list of all city pages for a service.
Placement: Hub page template — NOT city page template.
Activation: When hub framework page is created (Phase H).

YAML field (hub page only):
```yaml
service_hub_links:
  - href: "/website-laten-maken-rotterdam/"
    label: "Website laten maken Rotterdam"
    city: "Rotterdam"
```

Conditional rule: Omit any city entry not yet live as a framework page.

### 6d. Token Insertion Order in master-template.html

When Claude adds tokens to the template:
```
... (Section 3 content)
{{SAME_CITY_LINKS}} section     ← after section 3
{{NEARBY_CITY_LINKS}} section   ← after same-city
CTA section
FAQ section
... (footer)
```

Same-city before nearby-city — a visitor sees local service options before geographic options.

### 6e. Required CSS (Claude adds to design-tokens.css)

```css
.bdmnl-section--related { background: var(--color-bg-light); }
.bdmnl-related-links {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0;
  margin: 0;
}
.bdmnl-related-links a { text-decoration: underline; color: var(--color-primary); }

.bdmnl-section--nearby { background: white; }
.bdmnl-nearby-links {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0;
  margin: 0;
}
.bdmnl-nearby-links a { text-decoration: underline; color: var(--color-text); }
.bdmnl-nearby-label { font-weight: 600; margin-bottom: 0.5rem; }
```

CSS must be added in the same session as the template token update.

---

## 7. Rollout Rules

### 7a. Same-City Links — Decision Tree

```
City at 3+ framework pages?
  YES → Template has {{SAME_CITY_LINKS}} token?
          YES → Cat populates YAML for all city pages → Claude verifies → DONE
          NO  → Claude adds token to template first → Cat populates
  NO  → Wait. Do nothing.
```

### 7b. Nearby-City Links — Decision Tree

```
Service at 3+ framework pages?
  YES → Template has {{NEARBY_CITY_LINKS}} token?
          YES → Cat populates YAML for all service pages → Claude verifies → DONE
          NO  → Claude adds token to template first → Cat populates
  NO  → Wait. Do nothing.
```

### 7c. Template Update Timing

Add both tokens ({{SAME_CITY_LINKS}} + {{NEARBY_CITY_LINKS}}) in ONE template update session. Do not add one at a time.

**Both thresholds are already met:**
- Same-city: Rotterdam (4), Brielle (3), Delft (3), Spijkenisse (3) — all eligible NOW
- Nearby-city: website-laten-maken (8 cities), seo-bureau (7 cities) — eligible NOW

Recommended: add tokens to template in the next template session.

### 7d. Page Regeneration After Template Update

After Claude updates the template:
1. Cat regenerates ALL 20 existing framework pages with updated template
2. For ineligible pages (city < 3 pages, service < 3 pages): YAML field is empty → section omitted
3. For eligible pages: Cat populates YAML fields with correct links per maps in Sections 2e and 3d
4. Claude verifies: no empty ul tags, all linked slugs exist in pages/, correct canonical form

### 7e. Cascade When a New Page Is Added

After Cat commits a new framework page:
1. Check same-city threshold — city now at 3+? Update ALL pages in that city.
2. Check nearby-city threshold — service now at 3+? Update ALL pages in that service.
3. Update nearby-city blocks for geographic neighbors that should now link to the new city.
4. Cat updates relevant YAML files; Claude verifies correctness.

### 7f. Priority Rollout Order (First Batch)

1. Claude adds tokens to template + CSS (next template session)
2. Cat regenerates all 20 pages — website-laten-maken nearby blocks (8 pages get 3 links each)
3. Cat adds seo-bureau nearby blocks (7 pages get 3 links each)
4. Cat adds Rotterdam same-city blocks (4 pages get 3 links each)
5. Cat adds Brielle same-city blocks (3 pages get 2 links each)
6. Cat adds Delft same-city blocks (3 pages)
7. Cat adds Spijkenisse same-city blocks (3 pages)

---

## 8. SEO Risks and Mitigations

### 8a. Over-Linking

Risk: Too many links per page dilutes PageRank per link and may trigger quality signals.
Mitigation: Hard cap at 35 total links. Same-city max 4, nearby-city max 3.
Detection: Cat must count hrefs in generated HTML body before committing. Flag if > 35.

### 8b. Duplicate Anchor Text

Risk: Same anchor text for two different links confuses Google about which destination is primary.
Mitigation: Each same-city and nearby-city link has a unique anchor (different city or service). CTAs are the only repeated anchor and they all point to the same URL — acceptable.
Detection: Cat checks no two links in the same block share anchor text.

### 8c. Keyword Cannibalization

Risk: Two pages targeting the same keyword compete and split ranking signals.
Mitigation: One page per service per city — strictly enforced. Cross-links are always to different services or different cities.
Detection: Claude checks for slug conflicts in _redirects before accepting a new page.

### 8d. Thin Link Sections

Risk: A link block with 1 link looks unnatural and may be flagged as thin.
Mitigation: Minimum 2 links per section, or section is omitted entirely.
RULE: A block with 0 or 1 items must not be rendered. Conditional on minimum 2 items.

### 8e. Topical Dilution

Risk: Linking across unrelated services in nearby-city blocks confuses topical signals.
Mitigation: Nearby-city blocks are same-service only. Same-city blocks intentionally cross services but signal city authority, not service dilution. H2 text is neutral ("Meer diensten in [City]").

### 8f. Crawl Budget (Hub Pages)

Risk: Hub pages linking to 20+ city pages each could absorb crawl budget away from city pages.
Mitigation: City pages are indexed via sitemap independent of hub crawl. Hub pages are lightweight. Both types are in sitemap when live.

### 8g. Stale Cross-Links

Risk: A link points to a page that no longer exists or changed slug.
Mitigation: Only use slugs from the pages/ directory. Never guess slugs. When a slug changes (should be very rare), Claude audits all pages linking to it.

### 8h. Recovery Hub Page Equity Leak

Risk: Breadcrumb parent links pass equity to old recovery hub pages (/website-laten-maken/, /seo/) which may be low-quality.
Mitigation: These links already exist and cannot be removed without a template change. Priority: build framework hub pages (Phase H) to replace recovery hubs. Until then, breadcrumb is the only link to recovery hubs.

---

## 9. Architecture Diagram

```
www.bdmnl.nl (Webflow main site)
  ↑ all CTAs point here (/contact/)
  ↑ nav/footer links point here (/diensten/, /kennisbank/, etc.)

bdmnl.nl SEO cluster
  Hub pages (future Phase H)
  └── /website-laten-maken/
        ↓ {{SERVICE_HUB_LINKS}}
        ├── /website-laten-maken-rotterdam/
        │     ↔ [SAME-CITY] /seo-bureau-rotterdam/
        │     ↔ [SAME-CITY] /webshop-laten-maken-rotterdam/
        │     ↔ [SAME-CITY] /webdesign-rotterdam/
        │     ↔ [NEARBY]    /website-laten-maken-brielle/
        │     ↔ [NEARBY]    /website-laten-maken-spijkenisse/
        │     ↔ [NEARBY]    /website-laten-maken-delft/
        │     ↑ [BREADCRUMB] /website-laten-maken/
        ├── /website-laten-maken-brielle/
        │     ↔ [SAME-CITY] /seo-bureau-brielle/
        │     ↔ [SAME-CITY] /webdesign-brielle/
        │     ↔ [NEARBY]    /website-laten-maken-spijkenisse/
        │     ↔ [NEARBY]    /website-laten-maken-hellevoetsluis/
        │     ↔ [NEARBY]    /website-laten-maken-rotterdam/
        │     ↑ [BREADCRUMB] /website-laten-maken/
        └── ... (all WLM city pages)
```

---

## 10. Summary Reference Table

| Link type | Token | Threshold | Max links | Section heading | Section class |
|---|---|---|---|---|---|
| Same-city | {{SAME_CITY_LINKS}} | 3 pages in city | 4 | Meer diensten in [City] | bdmnl-section--related |
| Nearby-city | {{NEARBY_CITY_LINKS}} | 3 pages in service | 3 | [Service] ook beschikbaar in: | bdmnl-section--nearby |
| Hub city list | {{SERVICE_HUB_LINKS}} | Hub page exists | All live cities | Steden waar wij actief zijn | (hub template only) |
| Breadcrumb | {{BREADCRUMB_PARENT_HREF}} | Always | 1 | — | bdmnl-breadcrumb |
| CTA | {{CTA_HREF}} | Always | 1–2 | — | bdmnl-cta |

---

*End of internal-linking-strategy.md*
*Version 1.0 — 2026-05-20*
*Next action: Add {{SAME_CITY_LINKS}} + {{NEARBY_CITY_LINKS}} tokens to master-template.html*
