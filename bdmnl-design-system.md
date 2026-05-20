# BDMNL design system extraction

Source: `https://www.bdmnl.nl`

Primary CSS asset inspected:

- `https://cdn.prod.website-files.com/69fda057dc1e72c50e433fc4/css/bdmnl-2-0-final.webflow.shared.95d7181c7.css`

## Core tokens

- Primary font: `Satoshi, Arial, sans-serif`
- Primary color: `#070a26`
- Secondary accent: `#f05a1a`
- Neutral gray: `#6f7890`
- Light gray surface: `#f5f5f7`
- White: `#ffffff`
- Container width: `1320px`
- Container padding: `15px`
- Section gaps:
  - large: `110px`
  - medium: `80px`
  - small: `60px`

## Typography

- Display title: `120px`
- XL title: `60px`
- H1: `48px`
- H2: `40px`
- H3: `33px`
- H4: `28px`
- H5: `24px`
- H6: `20px`
- Large body: `18px`
- Medium body: `16px`
- Small body: `14px`
- Button text: `18px`
- Line heights:
  - tight: `100%`
  - compact: `120%`
  - relaxed: `130%`
  - body: `150%`

## Layout patterns observed

- Main `.container` uses full width with max `1320px` and `15px` side padding.
- Main `.section` spacing uses the `--section-gap` token rather than ad hoc padding.
- Navigation is fixed with dashed vertical separators in the center menu.
- Service rows are horizontal/list-like, not heavy isolated cards.
- Portfolio and testimonials use strong horizontal rhythm.
- Footer uses a dark primary background on the real site, with curated grouped links instead of an exposed sitemap dump.

## Recovery implementation rule

The recovery platform should use these tokens as the base system and only adapt layout where the static recovery environment requires it. New layouts should not introduce a separate visual language.

Implemented in:

- `assets/css/bdmnl-design-system.css`
- imported by `assets/css/landing.css`

## Design constraints going forward

- Use orange as a secondary micro-accent only.
- Use `#070a26`, white and neutral gray as the dominant palette.
- Use Satoshi typography and BDMNL title/body rhythm.
- Use the 1320px container.
- Use 110/80/60px spacing rhythm.
- Avoid creating independent SEO-template visual systems.
