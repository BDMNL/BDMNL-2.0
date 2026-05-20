# BDMNL Framework — Cat Instructions

> **LOCKED DESIGN SYSTEM — READ BEFORE TOUCHING ANYTHING**
> Version: 1.0
> Status: Production-ready / Immutable

---

## What Is This?

This is the BDMNL SEO Framework — a scalable, locked design system for generating premium Dutch local SEO pages at scale.

It consists of:
- `master-template.html` — The locked HTML template with all placeholders
- `design-tokens.css` — The locked CSS design system (colors, typography, spacing, components)
- `components/` — Optional reusable component snippets
- `../content/` — YAML content files (the ONLY things you touch)
- `../pages/` — Generated output pages (created from template + content)

---

## The Golden Rule

**Cat may ONLY replace `{{PLACEHOLDER}}` tokens with real content.**

Do NOT:
- Change HTML structure or class names
- Add inline styles or override CSS variables
- Modify `design-tokens.css` values
- Reorder or remove sections
- Add new CSS anywhere
- Change the footer
- Change the header nav
- Change the schema.org structure (only fill token values)

---

## How to Create a New Page

### Step 1 — Copy the master template
```
cp framework/master-template.html pages/webdesign-rotterdam/index.html
```

### Step 2 — Replace ALL tokens

Open the copied file. Find every `{{TOKEN}}` and replace it with real content. All tokens must be replaced — never leave a `{{}}` in production.

### Step 3 — Reference the YAML file

Check the corresponding `/content/` YAML file for the correct content values to use.

### Step 4 — Validate

Confirm:
- [ ] All `{{TOKENS}}` replaced
- [ ] `<title>` is 50-60 characters
- [ ] Meta description is 130-155 characters
- [ ] H1 contains city + service keyword
- [ ] All 5 FAQ items filled
- [ ] Schema phone and email filled
- [ ] Canonical URL is correct and absolute

---

## Full Token Reference

| Token | Description | Max Length |
|---|---|---|
| `{{CITY}}` | City name (e.g. Rotterdam) | 30 |
| `{{SERVICE}}` | Service slug (e.g. webdesign) | 30 |
| `{{H1}}` | Main H1 heading | 70 |
| `{{META_TITLE}}` | Page title tag | 60 |
| `{{META_DESC}}` | Meta description | 155 |
| `{{META_CANONICAL}}` | Absolute canonical URL | — |
| `{{INTRO_P1}}` | Hero subline + intro first paragraph | 200 |
| `{{INTRO_P2}}` | Intro second paragraph | 200 |
| `{{SECTION_1_H2}}` | Section 1 heading | 70 |
| `{{SECTION_1_P}}` | Section 1 paragraph | 400 |
| `{{SECTION_2_H2}}` | Section 2 heading | 70 |
| `{{SECTION_2_P}}` | Section 2 paragraph | 400 |
| `{{SECTION_3_H2}}` | Section 3 heading | 70 |
| `{{SECTION_3_P}}` | Section 3 paragraph | 400 |
| `{{CTA_HEADLINE}}` | CTA block headline | 60 |
| `{{CTA_SUBTEXT}}` | CTA supporting text | 150 |
| `{{CTA_BUTTON}}` | Button label | 30 |
| `{{CTA_HREF}}` | Button URL | — |
| `{{FAQ_1_Q}}` through `{{FAQ_5_Q}}` | FAQ questions | 100 |
| `{{FAQ_1_A}}` through `{{FAQ_5_A}}` | FAQ answers | 300 |
| `{{BREADCRUMB_PARENT}}` | Parent crumb label | 30 |
| `{{BREADCRUMB_PARENT_HREF}}` | Parent crumb URL | — |
| `{{SCHEMA_SERVICE_NAME}}` | Schema.org service description | 100 |
| `{{SCHEMA_AREA_SERVED}}` | Schema.org city name | 30 |
| `{{SCHEMA_PHONE}}` | Phone number | 20 |
| `{{SCHEMA_EMAIL}}` | Email address | 60 |

---

## Design System Rules

### Colors

| Variable | Value | Usage |
|---|---|---|
| `--color-black` | `#0a0a0a` | Primary text, hero bg |
| `--color-white` | `#ffffff` | Page background, inverse text |
| `--color-accent` | `#e85d04` | **ORANGE — MICRO-ACCENT ONLY** |

**Orange rule:** Use the orange accent for ONE element per page. Acceptable: the primary CTA button, a single nav link, the footer "Gebouwd in Nederland" label. NEVER for headings, backgrounds, borders, or decorative elements.

### Typography

| Variable | Value | Use for |
|---|---|---|
| `--text-5xl` | 3.815rem | H1 hero |
| `--text-3xl` | 2.441rem | H2 sections, CTA headline |
| `--text-2xl` | 1.953rem | H2 mobile |
| `--text-lg` | 1.250rem | Intro P1, hero subline |
| `--text-base` | 1.000rem | Body text |
| `--text-sm` | 0.800rem | Nav, footer, captions |

Font stack: **Inter** → Helvetica Neue → Arial → sans-serif

### Spacing

All spacing follows an 8px base grid. Use the `--space-{n}` tokens only. Never use hardcoded pixel values.

### Breakpoints (for reference)

| Name | Width |
|---|---|
| Mobile | < 640px |
| Tablet | 640px–768px |
| Desktop | 769px–1024px |
| Wide | > 1024px |

---

## Directory Structure

```
BDMNL-2.0/
├── framework/                   ← LOCKED — do not modify
│   ├── README.md                ← You are here (Cat instructions)
│   ├── master-template.html     ← Source template with {{TOKENS}}
│   ├── design-tokens.css        ← Complete CSS design system
│   └── components/              ← Optional reusable snippets
│       └── .gitkeep
│
├── content/                     ← Cat fills these YAML files
│   ├── rotterdam-website.yaml   ← Rotterdam page content
│   ├── brielle-webdesign.yaml   ← Brielle page content
│   └── [city-service].yaml      ← Add new files here
│
└── pages/                       ← Generated output pages go here
    └── .gitkeep
```

---

## Naming Convention for Content Files

```
[city]-[service].yaml
```

Examples:
- `rotterdam-webdesign.yaml`
- `amsterdam-branding.yaml`
- `brielle-seo.yaml`
- `delft-logo-design.yaml`

---

## Naming Convention for Generated Pages

Pages go in `/pages/` folder, one folder per page:

```
pages/
└── [service]-[city]/
    └── index.html
```

Examples:
- `pages/webdesign-rotterdam/index.html`
- `pages/branding-amsterdam/index.html`
- `pages/seo-brielle/index.html`

---

## SEO Content Guidelines

When filling tokens, follow these rules:

**H1:** Must contain city + service. Example: "Professioneel Webdesign Rotterdam — BDMNL"

**Meta Title:** City + service + brand. Max 60 chars. Example: "Webdesign Rotterdam | Premium websites | BDMNL"

**Meta Description:** Benefit + city + CTA. Max 155 chars.

**INTRO_P1:** Set the scene — who is this for, what do they get. Lead with the city and service.

**INTRO_P2:** Build trust — expertise, local knowledge, results.

**SECTION headings:** Should be semantic H2s. Include secondary keywords naturally. Not stuffed.

**FAQ:** Answer real questions people ask about this service in this city. Use natural language. Each answer minimum 2 sentences.

---

## What Is Locked vs. What Cat Can Change

| Element | Status |
|---|---|
| HTML structure | 🔒 LOCKED |
| CSS class names | 🔒 LOCKED |
| design-tokens.css values | 🔒 LOCKED |
| Header navigation links | 🔒 LOCKED |
| Footer structure and links | 🔒 LOCKED |
| Schema.org structure | 🔒 LOCKED |
| JavaScript (nav + FAQ) | 🔒 LOCKED |
| `{{TOKEN}}` values | ✅ Cat fills these |
| Content YAML files | ✅ Cat creates/edits these |
| New pages in /pages/ | ✅ Cat creates these |
| New YAML files in /content/ | ✅ Cat creates these |

---

*BDMNL Framework v1.0 — Built for scale, locked for quality.*
