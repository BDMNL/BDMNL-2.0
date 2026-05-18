#!/usr/bin/env python3
"""Generate SEO city landing pages from the reusable BDMNL template."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "templates" / "city-landing-template.html"
DATA_PATH = ROOT / "data" / "cities.json"
BASE_URL = "https://bdmnl.nl"


def html(value: Any) -> str:
    return escape(str(value), quote=True)


def build_faqs(city: str, market: str) -> list[dict[str, str]]:
    return [
        {
            "question": f"Waarom heeft mijn bedrijf in {city} een city landing page nodig?",
            "answer": (
                f"Een city landing page koppelt jouw aanbod aan de zoekintentie in {city}. "
                f"Daardoor zien bezoekers sneller dat je past bij hun lokale vraag en wordt de pagina relevanter voor SEO."
            ),
        },
        {
            "question": f"Blijft de pagina uniek voor {city}?",
            "answer": (
                f"Ja. De metadata, canonicals, headings, lokale tekstblokken, FAQ's en bewijsvoering worden afgestemd "
                f"op {city} en de {market}."
            ),
        },
        {
            "question": "Is het design geschikt voor mobiele bezoekers?",
            "answer": (
                "Ja. De template gebruikt compacte CTA's, responsive kaarten, duidelijke typografie en lichte animaties "
                "die ook op kleinere schermen premium blijven aanvoelen."
            ),
        },
        {
            "question": "Kan dezelfde template worden gebruikt voor meerdere steden?",
            "answer": (
                "Ja. De design system componenten blijven consistent, terwijl elke pagina unieke lokale content, "
                "schema data en canonical URL's krijgt."
            ),
        },
    ]


def build_faq_items(faqs: list[dict[str, str]]) -> str:
    items = []
    for faq in faqs:
        items.append(
            "\n".join(
                [
                    '            <article class="faq-item">',
                    f'              <button type="button" aria-expanded="false">{html(faq["question"])}<span></span></button>',
                    '              <div class="faq-answer">',
                    f'                <p>{html(faq["answer"])}</p>',
                    "              </div>",
                    "            </article>",
                ]
            )
        )
    return "\n".join(items)


def build_service_schema(city_data: dict[str, str], canonical_url: str) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": "BDMNL",
        "url": canonical_url,
        "areaServed": {
            "@type": "City",
            "name": city_data["city"],
        },
        "address": {
            "@type": "PostalAddress",
            "addressRegion": city_data["region"],
            "addressCountry": "NL",
        },
        "description": (
            f"Premium webdesign, SEO en conversiegerichte city landing pages voor bedrijven in {city_data['city']}."
        ),
        "serviceType": [
            "Webdesign",
            "SEO strategie",
            "Landing page design",
            "Website development",
        ],
        "sameAs": [BASE_URL],
    }
    return json.dumps(schema, ensure_ascii=False, indent=6)


def build_faq_schema(faqs: list[dict[str, str]]) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"],
                },
            }
            for faq in faqs
        ],
    }
    return json.dumps(schema, ensure_ascii=False, indent=6)


def build_page_context(city_data: dict[str, str]) -> dict[str, str]:
    city = city_data["city"]
    slug = city_data["slug"]
    market = city_data["market"]
    audience = city_data["audience"]
    local_focus = city_data["local_focus"]
    canonical_url = f"{BASE_URL}/{slug}/"
    faqs = build_faqs(city, market)
    lead_growth_number = city_data["lead_growth"].lstrip("+").rstrip("%")
    visibility_growth_number = city_data["visibility_growth"].lstrip("+").rstrip("%")

    return {
        "asset_prefix": "../",
        "canonical_url": canonical_url,
        "city": city,
        "city_slug": slug,
        "meta_title": f"Webdesign {city} | Premium websites door BDMNL",
        "meta_description": (
            f"BDMNL bouwt premium websites en SEO city landing pages voor bedrijven in {city}. "
            f"Moderne typografie, sterke CTA's, lokale content en conversiegericht design."
        ),
        "meta_keywords": (
            f"webdesign {city}, SEO {city}, landingspagina {city}, website laten maken {city}, BDMNL"
        ),
        "service_schema": build_service_schema(city_data, canonical_url),
        "faq_schema": build_faq_schema(faqs),
        "faq_items": build_faq_items(faqs),
        "h1": f"Webdesign {city} voor merken die lokaal premium willen overkomen.",
        "hero_lead": (
            f"BDMNL ontwerpt snelle, SEO-geoptimaliseerde landingspagina's voor {city} met de visuele "
            f"klasse van een high-end agency website en de structuur die bezoekers overtuigt."
        ),
        "metric_one_value": city_data["metric_one_value"],
        "metric_one_label": city_data["metric_one_label"],
        "metric_two_value": city_data["metric_two_value"],
        "metric_two_label": city_data["metric_two_label"],
        "lead_growth": city_data["lead_growth"],
        "lead_growth_number": lead_growth_number,
        "strategy_point": f"Positionering voor {city}",
        "seo_point": f"Content voor {local_focus}",
        "intro_heading": f"Een {city} pagina die niet voelt als een standaard SEO-template.",
        "intro_copy_one": (
            f"In de {market} vergelijken bezoekers snel. Een premium city page moet daarom niet alleen vindbaar zijn, "
            f"maar ook direct vertrouwen geven met duidelijke copy, rustige spacing en visuele autoriteit."
        ),
        "intro_copy_two": (
            f"Voor {audience} in {city} combineren we lokale relevantie met een moderne design flow: sterke hero, "
            f"bewijsvoering, servicekaarten, portfolio richting en FAQ's die drempels wegnemen."
        ),
        "service_one_copy": (
            f"Zoekintentie, contentblokken en interne links worden afgestemd op {city}, {local_focus} en de diensten "
            "waar jouw ideale klant actief naar zoekt."
        ),
        "service_two_copy": (
            f"Ruime layouts, premium micro-interacties en een moderne visuele hierarchie geven jouw merk in {city} "
            "direct meer autoriteit."
        ),
        "service_three_copy": (
            f"CTA's, proof points en FAQ's worden slim geplaatst zodat bezoekers uit {city} logisch doorgroeien naar "
            "aanvraag, intake of offerte."
        ),
        "portfolio_heading": f"Visuele richting voor {city} city pages met agency-level uitstraling.",
        "portfolio_case_one": f"{city} service page met sterke hero en trust flow",
        "portfolio_case_two": f"Compacte lead flow voor mobiele bezoekers in {city}",
        "portfolio_case_three": f"Premium bewijsvoering voor {audience}",
        "proof_heading": f"Meer autoriteit in {city} met rustige details, duidelijke claims en lokale focus.",
        "visibility_growth": city_data["visibility_growth"],
        "visibility_growth_number": visibility_growth_number,
        "visibility_label": city_data["visibility_label"],
        "testimonial_one": (
            f"De {city} pagina voelt veel premiumer zonder SEO-focus te verliezen. De flow maakt meteen duidelijk "
            "waarom bezoekers contact moeten opnemen."
        ),
        "testimonial_one_name": "Sanne de Vries",
        "testimonial_one_role": f"Marketing lead, {city}",
        "testimonial_two": (
            "BDMNL combineerde strategie, visueel design en lokale copy tot een pagina die aanvoelt als een "
            "high-end agency website."
        ),
        "testimonial_two_name": "Milan Vermeer",
        "testimonial_two_role": "Founder, groeibedrijf",
        "testimonial_three": (
            f"De nieuwe trust sections en CTA's geven onze propositie in {city} veel meer rust, ritme en overtuiging."
        ),
        "testimonial_three_name": "Nora Jansen",
        "testimonial_three_role": "Commercial director",
        "process_one": (
            f"We bepalen welke lokale behoefte, propositie en bewijsvoering in {city} centraal moeten staan."
        ),
        "process_two": (
            f"De pagina krijgt een SEO-vriendelijke flow met sterke headings, lokale {city} content, CTA's en FAQ's."
        ),
        "cta_heading": f"Klaar om in {city} meer vertrouwen en betere leads te winnen?",
        "cta_copy": (
            f"Laat BDMNL een landingspagina voor {city} ontwerpen die er premium uitziet, technisch strak staat en "
            "bezoekers richting actie brengt."
        ),
    }


def render_template(template: str, context: dict[str, str]) -> str:
    rendered = template
    for key, value in context.items():
        if key in {"service_schema", "faq_schema", "faq_items"}:
            replacement = value
        else:
            replacement = html(value)
        rendered = rendered.replace(f"{{{{{key}}}}}", replacement)

    leftovers = [part for part in rendered.split("{{") if "}}" in part]
    if leftovers:
        raise ValueError(f"Unresolved template tokens: {leftovers[:3]}")

    return rendered


def build_index(cities: list[dict[str, str]]) -> str:
    links = "\n".join(
        f'          <a class="service-card" href="./{html(city["slug"])}/">'
        f'<span class="card-number">{index:02d}</span><h3>Webdesign {html(city["city"])}</h3>'
        f'<p>Premium SEO city landing page voor {html(city["city"])}.</p></a>'
        for index, city in enumerate(cities, start=1)
    )

    return f"""<!doctype html>
<html lang="nl">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>BDMNL city landing pages | Premium SEO webdesign</title>
    <meta name="description" content="Bekijk de premium BDMNL city landing pages voor SEO webdesign in Nederlandse steden." />
    <meta name="robots" content="index,follow" />
    <meta name="theme-color" content="#F05A1A" />
    <link rel="canonical" href="{BASE_URL}/" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="./assets/css/landing.css" />
  </head>
  <body>
    <main id="main">
      <section class="hero section-pad">
        <div class="container">
          <p class="eyebrow"><span></span>BDMNL city pages</p>
          <h1>Premium SEO landingspagina's per stad.</h1>
          <p class="hero-lead">Een overzicht van gegenereerde city landing pages met moderne typografie, CTA's, trust sections, portfolio richting en FAQ accordions.</p>
          <div class="card-grid service-grid">
{links}
          </div>
        </div>
      </section>
    </main>
  </body>
</html>
"""


def main() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    cities = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for city_data in cities:
        context = build_page_context(city_data)
        output_dir = ROOT / city_data["slug"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(render_template(template, context), encoding="utf-8")

    (ROOT / "index.html").write_text(build_index(cities), encoding="utf-8")
    print(f"Generated {len(cities)} city landing pages.")


if __name__ == "__main__":
    main()
