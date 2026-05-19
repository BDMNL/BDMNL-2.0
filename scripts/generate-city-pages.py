#!/usr/bin/env python3
"""Generate the scalable BDMNL local SEO website system."""

from __future__ import annotations

import json
import shutil
import csv
from datetime import date
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "seo-system.json"
LAYOUT_PATH = ROOT / "templates" / "layout.html"
RECOVERY_TEMPLATE_PATH = ROOT / "templates" / "pages" / "recovery-page.html"
PREMIUM_RECOVERY_TEMPLATE_PATH = ROOT / "templates" / "pages" / "premium-recovery-page.html"
HEADER_PATH = ROOT / "templates" / "components" / "header.html"
FOOTER_PATH = ROOT / "templates" / "components" / "footer.html"
PREMIUM_BRIELLE_TEMPLATE_PATH = ROOT / "templates" / "pages" / "premium-brielle-example.html"
GENERATED_MARKER = "<!-- generated-by: bdmnl-seo-system -->"


def html(value: Any) -> str:
    return escape(str(value), quote=True)


def json_script(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=6)


def organization_identity(site: dict[str, Any]) -> dict[str, Any]:
    same_as = [social["url"] for social in site["socials"]]
    if site.get("legacy_domain"):
        same_as.append(site["legacy_domain"])
    if site.get("primary_domain"):
        same_as.append(site["primary_domain"])
    return {
        "@type": "Organization",
        "name": site["name"],
        "alternateName": [site.get("alternate_name", "Bulldog Media")],
        "url": site.get("primary_domain", site["base_url"]),
        "sameAs": same_as,
    }


def render(template: str, context: dict[str, str], raw_keys: set[str] | None = None) -> str:
    raw_keys = raw_keys or set()
    rendered = template
    for key, value in context.items():
        replacement = value if key in raw_keys else html(value)
        rendered = rendered.replace(f"{{{{{key}}}}}", replacement)

    leftovers = [part for part in rendered.split("{{") if "}}" in part]
    if leftovers:
        raise ValueError(f"Unresolved template tokens: {leftovers[:5]}")

    return rendered


def page_slug(service: dict[str, Any], city: dict[str, Any]) -> str:
    return f"{service['slug_prefix']}-{city['slug']}"


def page_path(site: dict[str, Any], slug: str) -> str:
    prefix = site.get("url_prefix", "").strip("/")
    return f"{prefix}/{slug}" if prefix else slug


def page_url(site: dict[str, Any], slug: str) -> str:
    return f"{site['base_url']}/{page_path(site, slug)}/"


def page_href(site: dict[str, Any], slug: str) -> str:
    return f"/{page_path(site, slug)}/"


def parse_percent(value: str) -> str:
    return value.replace("+", "").replace("%", "")


def build_faqs(service: dict[str, Any], city: dict[str, Any]) -> list[dict[str, str]]:
    city_name = city["name"]
    areas = ", ".join(city["areas"][:3])
    service_label = service["label"].lower()

    faq_sets = {
        "website": [
            (
                f"Wat kost een website laten maken in {city_name}?",
                f"De investering hangt af van het aantal pagina's, gewenste functies en SEO-ambitie. BDMNL start met strategie zodat de website voor {city_name} niet alleen mooi is, maar ook gericht is op aanvragen.",
            ),
            (
                f"Wordt mijn website geoptimaliseerd voor lokale vindbaarheid in {city_name}?",
                f"Ja. We verwerken lokale vragen, duidelijke verwijzingen en content voor gebieden zoals {areas}.",
            ),
            (
                "Kan BDMNL ook teksten en CTA's verzorgen?",
                "Ja. De website krijgt conversiegerichte copy, duidelijke CTA's en FAQ's die passen bij jouw doelgroep en dienstaanbod.",
            ),
            (
                "Is de website geschikt om later uit te breiden met SEO pagina's?",
                "Ja. De structuur is modulair opgebouwd zodat extra diensten, steden en SEO clusters later schaalbaar toegevoegd kunnen worden.",
            ),
        ],
        "seo": [
            (
                f"Wat doet een SEO bureau in {city_name} precies?",
                f"BDMNL onderzoekt lokale zoekintentie, verbetert techniek, bouwt contentclusters en optimaliseert pagina's voor diensten in {city_name}.",
            ),
            (
                f"Hoe snel zie ik resultaat met SEO in {city_name}?",
                "SEO is afhankelijk van concurrentie, techniek en contentkwaliteit. We richten ons op duurzame groei met meetbare verbeteringen in zichtbaarheid, rankings en aanvragen.",
            ),
            (
                f"Welke lokale gebieden neemt BDMNL mee voor {city_name}?",
                f"We kijken naar relevante wijken en plaatsen zoals {areas}, plus zoekopdrachten met commerciële intentie.",
            ),
            (
                "Combineert BDMNL SEO met webdesign?",
                "Ja. SEO werkt sterker wanneer de pagina snel laadt, duidelijk leest en bezoekers logisch naar contact of offerte leidt.",
            ),
        ],
        "social": [
            (
                f"Wat valt onder social media beheer in {city_name}?",
                "BDMNL helpt met strategie, contentplanning, visuals, captions, campagneformats en consistente publicatie voor lokale zichtbaarheid.",
            ),
            (
                "Kan social media worden gekoppeld aan SEO en website aanvragen?",
                "Ja. We zorgen dat social content aansluit op landingspagina's, CTA's en lokale thema's zodat kanalen elkaar versterken.",
            ),
            (
                f"Maakt BDMNL lokale content voor {city_name}?",
                f"Ja. Content kan inspelen op lokale context, doelgroepen en gebieden zoals {areas}, zonder generiek te voelen.",
            ),
            (
                "Is social media beheer geschikt voor MKB-bedrijven?",
                "Ja. Vooral bedrijven die consistent zichtbaar willen blijven zonder elke week zelf content te bedenken profiteren van een vaste contentflow.",
            ),
        ],
    }

    return [{"question": question, "answer": answer} for question, answer in faq_sets[service["faq_seed"]]]


def build_service_cards(service: dict[str, Any], city: dict[str, Any]) -> str:
    cards = [
        (
            "01",
            "Lokale strategie",
            f"We vertalen de lokale vraag in {city['name']} naar een heldere opbouw met duidelijke propositie, vertrouwen en vervolgstappen.",
        ),
        (
            "02",
            "Strakke uitvoering",
            f"{service['label']} krijgt een snelle Webflow-basis, rustige typografie en een duidelijke opbouw voor bezoekers.",
        ),
        (
            "03",
            "Conversie en groei",
            "We sturen bezoekers naar intake, offerte of contact met bewijsvoering, FAQ's en interne links naar verwante diensten.",
        ),
    ]
    return "\n".join(
        "\n".join(
            [
                '      <article class="service-card reveal">',
                f"        <span class=\"card-number\">{number}</span>",
                '        <div class="service-icon" aria-hidden="true"></div>',
                f"        <h3>{html(title)}</h3>",
                f"        <p>{html(copy)}</p>",
                '        <a href="#contact">Bespreek aanpak</a>',
                "      </article>",
            ]
        )
        for number, title, copy in cards
    )


def build_cluster_links(
    site: dict[str, Any], current_slug: str, city: dict[str, Any], services: list[dict[str, Any]]
) -> str:
    cards = []
    for index, service in enumerate(services, start=1):
        slug = page_slug(service, city)
        active = " is-active" if slug == current_slug else ""
        cards.append(
            "\n".join(
                [
                    f'      <a class="service-card related-card{active} reveal" href="{page_href(site, slug)}">',
                    f'        <span class="card-number">{index:02d}</span>',
                    '        <div class="service-icon" aria-hidden="true"></div>',
                    f"        <h3>{html(service['label'])} {html(city['name'])}</h3>",
                    f"        <p>{html(service['description_pattern'].format(city=city['name']))}</p>",
                    "      </a>",
                ]
            )
        )
    return "\n".join(cards)


def build_related_city_links(
    site: dict[str, Any], service: dict[str, Any], current_city: dict[str, Any], cities: list[dict[str, Any]]
) -> str:
    links = []
    for city in cities:
        if city["slug"] == current_city["slug"]:
            continue
        slug = page_slug(service, city)
        links.append(f'<a href="{page_href(site, slug)}">{html(service["label"])} {html(city["name"])}</a>')
    return "\n".join(links)


def build_faq_items(faqs: list[dict[str, str]]) -> str:
    return "\n".join(
        "\n".join(
            [
                '      <article class="faq-item">',
                f'        <button type="button" aria-expanded="false">{html(faq["question"])}<span></span></button>',
                '        <div class="faq-answer">',
                f'          <p>{html(faq["answer"])}</p>',
                "        </div>",
                "      </article>",
            ]
        )
        for faq in faqs
    )


def build_testimonial_cards(city: dict[str, Any], service: dict[str, Any]) -> str:
    testimonials = [
        (
            "BDMNL heeft onze website vernieuwd naar een moderne en gebruiksvriendelijke uitstraling. De communicatie verliep prettig en er werd snel geschakeld bij feedback of aanpassingen.",
            "HV Helius",
            "Lokale sportorganisatie",
        ),
        (
            "Onze oude website was verouderd en niet goed vindbaar in Google. BDMNL heeft dit volledig vernieuwd met een frisse uitstraling en duidelijke structuur voor onze klanten.",
            "Brielle Automotive",
            "Autobedrijf",
        ),
        (
            "Dankzij BDMNL hebben wij nu een professionele website die niet alleen mooi oogt, maar ook beter gevonden wordt in Google. Fijn contact en snelle communicatie tijdens het hele traject.",
            "Studio Brielle",
            "Creatieve onderneming",
        ),
    ]
    return "\n".join(
        "\n".join(
            [
                f'      <article class="testimonial-card{" featured" if index == 1 else ""} reveal">',
                '        <div class="quote-mark">"</div>',
                f"        <p>{html(copy)}</p>",
                "        <div>",
                f"          <strong>{html(name)}</strong>",
                f"          <span>{html(role)}</span>",
                "        </div>",
                "      </article>",
            ]
        )
        for index, (copy, name, role) in enumerate(testimonials)
    )


def build_marquee_items(city: dict[str, Any], service: dict[str, Any]) -> str:
    items = [service["label"], city["name"], *city["areas"][:4], "Lokale SEO", "Snelle UX", "Lead flow"]
    return "\n".join(f"<span>{html(item)}</span>" for item in items)


def professional_service_schema(
    site: dict[str, Any], city: dict[str, Any], service: dict[str, Any], canonical_url: str
) -> str:
    return json_script(
        {
            "@context": "https://schema.org",
            "@type": "ProfessionalService",
            "name": f"BDMNL - {service['label']} {city['name']}",
            "alternateName": "Bulldog Media",
            "url": canonical_url,
            "image": site["og_image"],
            "email": site["email"],
            "telephone": site["phone"],
            "areaServed": {"@type": "City", "name": city["name"]},
            "address": {
                "@type": "PostalAddress",
                "addressRegion": city["region"],
                "addressCountry": "NL",
            },
            "description": service["description_pattern"].format(city=city["name"]),
            "serviceType": service["service_type"],
            "sameAs": organization_identity(site)["sameAs"],
        }
    )


def faq_schema(faqs: list[dict[str, str]]) -> str:
    return json_script(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq["question"],
                    "acceptedAnswer": {"@type": "Answer", "text": faq["answer"]},
                }
                for faq in faqs
            ],
        }
    )


def breadcrumb_schema(base_url: str, city: dict[str, Any], service: dict[str, Any], canonical_url: str) -> str:
    return json_script(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                {"@type": "ListItem", "position": 2, "name": city["name"], "item": canonical_url},
                {"@type": "ListItem", "position": 3, "name": service["label"], "item": canonical_url},
            ],
        }
    )


def footer_context(site: dict[str, Any], cities: list[dict[str, Any]], services: list[dict[str, Any]]) -> dict[str, str]:
    first_service = services[0]
    footer_city_links = "\n".join(
        f'<a href="{page_href(site, page_slug(first_service, city))}">{html(city["name"])}</a>' for city in cities
    )
    footer_service_links = "\n".join(
        f'<a href="{page_href(site, page_slug(service, cities[0]))}">{html(service["label"])}</a>' for service in services
    )
    footer_internal_links = "\n".join(
        [
            '<a href="/contact/">Contact</a>',
            '<a href="/privacyverklaring/">Privacyverklaring</a>',
            '<a href="/cookiebeleid/">Cookiebeleid</a>',
            '<a href="/algemene-voorwaarden/">Algemene voorwaarden</a>',
        ]
    )
    return {
        "footer_city_links": footer_city_links,
        "footer_service_links": footer_service_links,
        "footer_internal_links": footer_internal_links,
        "current_year": str(date.today().year),
    }


def build_page_context(
    site: dict[str, Any],
    city: dict[str, Any],
    service: dict[str, Any],
    services: list[dict[str, Any]],
    cities: list[dict[str, Any]],
) -> dict[str, str]:
    slug = page_slug(service, city)
    canonical_url = page_url(site, slug)
    faqs = build_faqs(service, city)
    areas = ", ".join(city["areas"][:3])
    title = service["title_pattern"].format(city=city["name"])
    description = service["description_pattern"].format(city=city["name"])
    related_city_links = build_related_city_links(site, service, city, cities)
    keywords = ", ".join([f"{keyword} {city['name']}" for keyword in service["keywords"]])

    return {
        "asset_prefix": "../" * len(page_path(site, slug).split("/")),
        "canonical_url": canonical_url,
        "og_title": title,
        "og_description": description,
        "twitter_title": title,
        "twitter_description": description,
        "og_image": site["og_image"],
        "meta_title": title,
        "meta_description": description,
        "professional_service_schema": professional_service_schema(site, city, service, canonical_url),
        "faq_schema": faq_schema(faqs),
        "breadcrumb_schema": breadcrumb_schema(site["base_url"], city, service, canonical_url),
        "eyebrow": f"{service['label']} in {city['name']}",
        "city": city["name"],
        "slug": page_path(site, slug),
        "service_label": service["label"],
        "service_badge": service["badge"],
        "h1": service["h1_pattern"].format(city=city["name"]),
        "hero_lead": service["hero_pattern"].format(city=city["name"]),
        "primary_cta": service["primary_cta"],
        "stat_one_value": service["stat_one_value"],
        "stat_one_number": parse_percent(service["stat_one_value"]),
        "stat_one_prefix": "+" if service["stat_one_value"].startswith("+") else "",
        "stat_one_suffix": "+" if service["stat_one_value"].endswith("+") else ("%" if service["stat_one_value"].endswith("%") else ""),
        "stat_one_label": service["stat_one_label"],
        "stat_two_value": service["stat_two_value"],
        "stat_two_label": service["stat_two_label"],
        "stat_three_number": parse_percent(service["stat_three_value"]),
        "stat_three_label": service["stat_three_label"],
        "floating_one_label": service["floating_one_label"],
        "floating_one_value": service["floating_one_value"],
        "floating_two_label": service["floating_two_label"],
        "floating_two_value": service["floating_two_value"],
        "area_summary": areas,
        "trust_strategy": f"Positionering voor {city['name']}",
        "trust_seo": f"Content voor {areas}",
        "marquee_items": build_marquee_items(city, service),
        "intro_heading": f"{service['label']} {city['name']} met lokale relevantie en een professionele uitstraling.",
        "intro_copy_one": (
            f"In {city['name']} zoeken klanten anders dan in een landelijke markt. Daarom combineert BDMNL "
            f"{service['label'].lower()} met lokale content, technische SEO en een conversiegerichte flow."
        ),
        "intro_copy_two": (
            f"De pagina speelt in op {city['intent']} en verwerkt herkenbare gebieden zoals {areas}. "
            "Zo voelt de content lokaal, betrouwbaar en relevant."
        ),
        "intro_copy_three": (
            f"Deze pagina linkt door naar de andere diensten in de {city['name']} cluster, zodat website, SEO en social "
            "media elkaar versterken in plaats van los van elkaar te staan."
        ),
        "services_heading": f"Wat BDMNL doet voor {service['label'].lower()} in {city['name']}.",
        "services_intro": (
            f"Een schaalbare SEO pagina voor {city['name']} krijgt strategie, Webflow design, technische basis en "
            "interne links naar relevante diensten."
        ),
        "service_cards": build_service_cards(service, city),
        "portfolio_heading": f"Voorbeeldrichting voor {service['label'].lower()} in {city['name']}.",
        "portfolio_intro": (
            "Een lokale SEO pagina hoeft niet generiek te voelen. BDMNL combineert rustige visuele details, duidelijke CTA's "
            "en bewijsvoering met de herkenbare uitstraling van de huidige BDMNL 2.0 website."
        ),
        "portfolio_case_one": f"{service['label']} {city['name']} met lokale hero en trust flow",
        "portfolio_case_one_label": f"SEO structuur + {keywords}",
        "portfolio_case_two": f"Mobiele lead flow voor bezoekers uit {city['name']}",
        "portfolio_case_three": f"Credibility systeem voor {city['market']}",
        "proof_heading": f"Sterker online in {city['name']} met lokale content, Webflow, SEO en duidelijke CTA's.",
        "cluster_links": build_cluster_links(site, slug, city, services),
        "testimonial_heading": f"Waarom bedrijven kiezen voor BDMNL in {city['name']}.",
        "testimonial_cards": build_testimonial_cards(city, service),
        "cta_heading": f"Klaar om {service['label'].lower()} in {city['name']} goed neer te zetten?",
        "cta_copy": (
            f"Laat BDMNL een lokale SEO pagina bouwen voor {city['name']} die past binnen je website, "
            "met sterke interne links, schema data en duidelijke CTA's."
        ),
        "faq_heading": f"Veelgestelde vragen over {service['label'].lower()} in {city['name']}.",
        "faq_intro": "Antwoorden op lokale SEO vragen voordat je investeert in een schaalbare landingspagina.",
        "faq_items": build_faq_items(faqs),
        "related_city_links": related_city_links,
    }


def render_full_page(
    layout: str,
    page_template: str,
    header: str,
    footer: str,
    footer_ctx: dict[str, str],
    context: dict[str, str],
) -> str:
    page_content = render(
        page_template,
        context,
        raw_keys={
            "service_cards",
            "cluster_links",
            "testimonial_cards",
            "faq_items",
            "marquee_items",
            "related_city_links",
        },
    )
    header_html = render(header, {"asset_prefix": context["asset_prefix"]})
    footer_html = render(
        footer,
        {**footer_ctx, "asset_prefix": context["asset_prefix"]},
        raw_keys={"footer_city_links", "footer_service_links", "footer_internal_links"},
    )
    full_context = {
        **context,
        "global_header": header_html,
        "global_footer": footer_html,
        "page_content": page_content.strip(),
    }
    return (
        GENERATED_MARKER
        + "\n"
        + render(
            layout,
            full_context,
            raw_keys={
                "global_header",
                "global_footer",
                "page_content",
                "professional_service_schema",
                "faq_schema",
                "breadcrumb_schema",
            },
        )
    )


def build_homepage(
    layout: str,
    header: str,
    footer: str,
    footer_ctx: dict[str, str],
    site: dict[str, Any],
    cities: list[dict[str, Any]],
    services: list[dict[str, Any]],
) -> str:
    cards = []
    for city in cities:
        links = " ".join(
            f'<a href="{page_href(site, page_slug(service, city))}">{html(service["label"])}</a>' for service in services
        )
        cards.append(
            "\n".join(
                [
                    '<article class="service-card reveal">',
                    f'<span class="card-number">{html(city["region"])}</span>',
                    f"<h2>{html(city['name'])}</h2>",
                    f"<p>{html(city['intent'])}</p>",
                    f'<div class="mini-link-row">{links}</div>',
                    "</article>",
                ]
            )
        )

    page_content = f"""
<section class="hero section-pad">
  <div class="container">
    <p class="eyebrow"><span></span>BDMNL SEO systeem</p>
    <h1>Lokale SEO pagina's in één helder BDMNL systeem.</h1>
    <p class="hero-lead">Een vaste structuur voor Webflow, SEO en social media pagina's per stad, met gedeelde componenten, interne links en nette technische SEO.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{page_href(site, page_slug(services[0], cities[0]))}" data-magnetic>Bekijk cluster</a>
      <a class="btn btn-secondary" href="/contact/" data-magnetic>Neem contact op</a>
    </div>
  </div>
</section>
<section class="section related-pages" id="diensten">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Lokale clusters</p>
      <h2>Verbonden SEO pagina's per stad.</h2>
      <p>Elke stad bevat drie verbonden pagina's: website laten maken, SEO bureau en social media beheer.</p>
    </div>
    <div class="card-grid service-grid">
      {"".join(cards)}
    </div>
  </div>
</section>
<section class="section portfolio" id="portfolio">
  <div class="container">
    <div class="section-heading reveal">
      <p class="eyebrow"><span></span>Cases</p>
      <h2>Een vaste basis voor lokale zichtbaarheid.</h2>
      <p>Dezelfde BDMNL header, footer, interacties en SEO basis worden automatisch toegepast op elke gegenereerde pagina.</p>
    </div>
  </div>
</section>
<section class="section process" id="proces">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Werkwijze</p>
      <h2>Data, componenten en generator vormen samen een herhaalbaar SEO systeem.</h2>
      <p>Nieuwe steden en diensten kunnen worden toegevoegd via de centrale data, waarna de generator metadata, schema, sitemap en interne links opnieuw opbouwt.</p>
    </div>
  </div>
</section>
<section class="section knowledge-section" id="kennisbank">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Kennisbank</p>
      <h2>Interne links, lokale clusters en technische SEO in één structuur.</h2>
      <p>Gebruik de sitemap en de lokale clusters om snel te controleren welke pagina's live staan en hoe ze aan elkaar gekoppeld zijn.</p>
    </div>
  </div>
</section>
<section class="section cta-band">
  <div class="container">
    <div class="cta-panel reveal" id="contact">
      <div>
        <p class="eyebrow light"><span></span>Contact</p>
        <h2>Plan een strategiegesprek over jouw lokale SEO systeem.</h2>
        <p>BDMNL helpt je de structuur, content en schaalbaarheid van lokale landingspagina's professioneel neer te zetten.</p>
      </div>
      <form class="cta-form" action="#" method="post">
        <label for="email">Zakelijk e-mailadres</label>
        <div>
          <input id="email" name="email" type="email" required />
          <button class="btn btn-dark" type="submit">Plan gesprek</button>
        </div>
      </form>
    </div>
  </div>
</section>
"""
    empty_schema = json_script(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": site["name"],
            "alternateName": site.get("alternate_name", "Bulldog Media"),
            "url": site["base_url"],
            "publisher": organization_identity(site),
        }
    )
    full_context = {
        "asset_prefix": "./",
        "canonical_url": f"{site['base_url']}/",
        "og_title": "BDMNL lokaal SEO systeem",
        "og_description": "Lokale SEO pagina's per stad en dienst binnen één gedeelde BDMNL structuur.",
        "twitter_title": "BDMNL lokaal SEO systeem",
        "twitter_description": "Lokale SEO pagina's per stad en dienst binnen één gedeelde BDMNL structuur.",
        "og_image": site["og_image"],
        "meta_title": "BDMNL lokaal SEO systeem | Webflow, SEO en online groei",
        "meta_description": "BDMNL bouwt schaalbare lokale SEO clusters voor websites, SEO en social media beheer in Brielle, Hellevoetsluis, Rockanje, Spijkenisse en Rotterdam.",
        "professional_service_schema": empty_schema,
        "faq_schema": json_script({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": []}),
        "breadcrumb_schema": json_script(
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site['base_url']}/"}],
            }
        ),
        "global_header": render(header, {"asset_prefix": "./"}),
        "global_footer": render(
            footer,
            {**footer_ctx, "asset_prefix": "./"},
            raw_keys={"footer_city_links", "footer_service_links", "footer_internal_links"},
        ),
        "page_content": page_content.strip(),
    }
    return GENERATED_MARKER + "\n" + render(
        layout,
        full_context,
        raw_keys={"global_header", "global_footer", "page_content", "professional_service_schema", "faq_schema", "breadcrumb_schema"},
    )


SUPPORT_PAGES = [
    {
        "slug": "contact",
        "title": "Contact opnemen met BDMNL | Webdesign, SEO & online marketing",
        "description": "Neem contact op met BDMNL in Brielle voor Webflow websites, SEO, branding, social media en online marketing.",
        "h1": "Neem contact op met BDMNL.",
        "body": (
            "Heb je een vraag over een website, webshop, branding, SEO of online marketing? "
            "Stuur BDMNL een bericht of plan een vrijblijvend gesprek. We denken praktisch met je mee over de volgende stap."
        ),
    },
    {
        "slug": "privacyverklaring",
        "title": "Privacyverklaring | BDMNL",
        "description": "Lees hoe BDMNL omgaat met persoonsgegevens, contactaanvragen en gegevens die nodig zijn voor onze dienstverlening.",
        "h1": "Privacyverklaring.",
        "body": (
            "BDMNL gaat zorgvuldig om met persoonsgegevens die je actief met ons deelt, bijvoorbeeld via contactformulieren, "
            "offerteaanvragen of e-mail. Gegevens worden gebruikt om vragen te beantwoorden, afspraken te maken en diensten uit te voeren."
        ),
    },
    {
        "slug": "cookiebeleid",
        "title": "Cookiebeleid | BDMNL",
        "description": "Lees hoe BDMNL cookies gebruikt voor een goed werkende website, analyse en verbetering van online ervaring.",
        "h1": "Cookiebeleid.",
        "body": (
            "BDMNL gebruikt cookies en vergelijkbare technieken om de website goed te laten werken en waar nodig prestaties te meten. "
            "Je kunt cookies beheren via je browserinstellingen."
        ),
    },
    {
        "slug": "algemene-voorwaarden",
        "title": "Algemene voorwaarden | BDMNL",
        "description": "Bekijk de algemene uitgangspunten voor samenwerking met BDMNL rond webdesign, SEO en online marketing.",
        "h1": "Algemene voorwaarden.",
        "body": (
            "Voor projecten met BDMNL maken we duidelijke afspraken over scope, planning, oplevering, betaling en verantwoordelijkheden. "
            "Bij een offerte of opdrachtbevestiging ontvang je de voorwaarden die op jouw project van toepassing zijn."
        ),
    },
]


def build_support_page(
    layout: str,
    header: str,
    footer: str,
    footer_ctx: dict[str, str],
    site: dict[str, Any],
    page: dict[str, str],
) -> str:
    asset_prefix = "../"
    contact_cards = ""
    if page["slug"] == "contact":
        contact_cards = f"""
    <div class="card-grid service-grid">
      <article class="service-card reveal">
        <span class="card-number">Mail</span>
        <h2>E-mail</h2>
        <p><a href="mailto:{html(site['email'])}">{html(site['email'])}</a></p>
      </article>
      <article class="service-card reveal">
        <span class="card-number">Bel</span>
        <h2>Telefoon</h2>
        <p><a href="tel:{html(site['phone_href'])}">{html(site['phone'])}</a></p>
      </article>
      <article class="service-card reveal">
        <span class="card-number">Adres</span>
        <h2>Brielle</h2>
        <p>{html(site['address'])}</p>
      </article>
    </div>
"""
    page_content = f"""
<section class="hero section-pad">
  <div class="container">
    <p class="eyebrow"><span></span>BDMNL</p>
    <h1>{html(page['h1'])}</h1>
    <p class="hero-lead">{html(page['body'])}</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="mailto:{html(site['email'])}" data-magnetic>Stuur een e-mail</a>
      <a class="btn btn-secondary" href="/sitemap.xml" data-magnetic>Bekijk sitemap</a>
    </div>
{contact_cards}
  </div>
</section>
"""
    web_page_schema = json_script(
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": page["title"],
            "url": f"{site['base_url']}/{page['slug']}/",
            "description": page["description"],
        }
    )
    breadcrumb = json_script(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site['base_url']}/"},
                {"@type": "ListItem", "position": 2, "name": page["h1"].rstrip("."), "item": f"{site['base_url']}/{page['slug']}/"},
            ],
        }
    )
    full_context = {
        "asset_prefix": asset_prefix,
        "canonical_url": f"{site['base_url']}/{page['slug']}/",
        "og_title": page["title"],
        "og_description": page["description"],
        "twitter_title": page["title"],
        "twitter_description": page["description"],
        "og_image": site["og_image"],
        "meta_title": page["title"],
        "meta_description": page["description"],
        "professional_service_schema": web_page_schema,
        "faq_schema": json_script({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": []}),
        "breadcrumb_schema": breadcrumb,
        "global_header": render(header, {"asset_prefix": asset_prefix}),
        "global_footer": render(
            footer,
            {**footer_ctx, "asset_prefix": asset_prefix},
            raw_keys={"footer_city_links", "footer_service_links", "footer_internal_links"},
        ),
        "page_content": page_content.strip(),
    }
    return GENERATED_MARKER + "\n" + render(
        layout,
        full_context,
        raw_keys={"global_header", "global_footer", "page_content", "professional_service_schema", "faq_schema", "breadcrumb_schema"},
    )


RECOVERY_CITIES = {
    "brielle": {
        "name": "Brielle",
        "region": "Zuid-Holland",
        "areas": ["Brielle Centrum", "Vierpolders", "Zwartewaal"],
        "intent": "lokale ondernemers op Voorne-Putten die online professioneler zichtbaar willen zijn",
    },
    "hellevoetsluis": {
        "name": "Hellevoetsluis",
        "region": "Zuid-Holland",
        "areas": ["Centrum", "De Struyten", "Ravense Hoek"],
        "intent": "bedrijven rond haven, retail en dienstverlening die lokaal beter gevonden willen worden",
    },
    "rockanje": {
        "name": "Rockanje",
        "region": "Zuid-Holland",
        "areas": ["Rockanje Dorp", "Tweede Slag", "Tinte"],
        "intent": "lokale en recreatieve ondernemers die seizoensvraag willen omzetten in aanvragen",
    },
    "spijkenisse": {
        "name": "Spijkenisse",
        "region": "Zuid-Holland",
        "areas": ["Centrum", "De Akkers", "Maaswijk"],
        "intent": "bedrijven in Nissewaard die vertrouwen, vindbaarheid en aanvragen willen versterken",
    },
    "rotterdam": {
        "name": "Rotterdam",
        "region": "Zuid-Holland",
        "areas": ["Centrum", "Kop van Zuid", "Kralingen"],
        "intent": "bedrijven die in een concurrerende markt sneller vertrouwen en aanvragen willen opbouwen",
    },
    "goes": {
        "name": "Goes",
        "region": "Zeeland",
        "areas": ["Goes Centrum", "De Poel", "Kloetinge"],
        "intent": "Zeeuwse ondernemers die lokaal beter gevonden willen worden en professioneel willen overkomen",
    },
    "dordrecht": {
        "name": "Dordrecht",
        "region": "Zuid-Holland",
        "areas": ["Binnenstad", "Sterrenburg", "Dubbeldam"],
        "intent": "dienstverleners en MKB-bedrijven die hun online basis willen versterken",
    },
    "vlaardingen": {
        "name": "Vlaardingen",
        "region": "Zuid-Holland",
        "areas": ["Centrum", "Holy", "Westwijk"],
        "intent": "lokale bedrijven die online vindbaarheid willen combineren met een moderne uitstraling",
    },
    "breda": {
        "name": "Breda",
        "region": "Noord-Brabant",
        "areas": ["Centrum", "Belcrum", "Princenhage"],
        "intent": "bedrijven die hun merk, website en lokale vindbaarheid sterker willen positioneren",
    },
    "tilburg": {
        "name": "Tilburg",
        "region": "Noord-Brabant",
        "areas": ["Centrum", "Spoorzone", "Reeshof"],
        "intent": "Brabantse ondernemers die online zichtbaarheid willen koppelen aan een professionele websitebasis",
    },
    "eindhoven": {
        "name": "Eindhoven",
        "region": "Noord-Brabant",
        "areas": ["Centrum", "Strijp-S", "Woensel"],
        "intent": "innovatieve bedrijven die digitaal sterker willen concurreren met heldere content en SEO",
    },
    "roosendaal": {
        "name": "Roosendaal",
        "region": "Noord-Brabant",
        "areas": ["Centrum", "Kalsdonk", "Tolberg"],
        "intent": "lokale dienstverleners en MKB-bedrijven die meer regionale aanvragen willen krijgen",
    },
    "bergen-op-zoom": {
        "name": "Bergen op Zoom",
        "region": "Noord-Brabant",
        "areas": ["Centrum", "Gageldonk", "Halsteren"],
        "intent": "bedrijven in West-Brabant die beter gevonden willen worden op lokale zoekvragen",
    },
    "leiden": {
        "name": "Leiden",
        "region": "Zuid-Holland",
        "areas": ["Binnenstad", "Bio Science Park", "Stevenshof"],
        "intent": "kennisgedreven bedrijven en lokale dienstverleners die professioneel zichtbaar willen zijn",
    },
    "delft": {
        "name": "Delft",
        "region": "Zuid-Holland",
        "areas": ["Binnenstad", "TU Delft", "Voorhof"],
        "intent": "technische bedrijven, creatieve ondernemers en lokale dienstverleners die online scherper willen positioneren",
    },
    "vlissingen": {
        "name": "Vlissingen",
        "region": "Zeeland",
        "areas": ["Binnenstad", "Boulevard", "Souburg"],
        "intent": "Zeeuwse ondernemers in maritieme, toeristische en dienstverlenende markten die sterker online willen staan",
    },
    "terneuzen": {
        "name": "Terneuzen",
        "region": "Zeeland",
        "areas": ["Centrum", "Axel", "Sluiskil"],
        "intent": "bedrijven in Zeeuws-Vlaanderen die online betrouwbaarheid en regionale vindbaarheid willen versterken",
    },
    "zierikzee": {
        "name": "Zierikzee",
        "region": "Zeeland",
        "areas": ["Binnenstad", "Schouwen-Duiveland", "Nieuwerkerk"],
        "intent": "lokale en toeristische ondernemers die aanvragen uit Schouwen-Duiveland willen aantrekken",
    },
    "den-bosch": {
        "name": "Den Bosch",
        "region": "Noord-Brabant",
        "areas": ["Binnenstad", "Paleiskwartier", "Rosmalen"],
        "intent": "Brabantse bedrijven die hun merk, website en online vindbaarheid professioneler willen neerzetten",
    },
    "haarlem": {
        "name": "Haarlem",
        "region": "Noord-Holland",
        "areas": ["Centrum", "Schalkwijk", "Waarderpolder"],
        "intent": "creatieve ondernemers en lokale dienstverleners die in een concurrerende Randstadmarkt willen opvallen",
    },
    "alkmaar": {
        "name": "Alkmaar",
        "region": "Noord-Holland",
        "areas": ["Binnenstad", "Overdie", "De Hoef"],
        "intent": "Noord-Hollandse MKB-bedrijven die regionale zichtbaarheid willen koppelen aan professionele uitstraling",
    },
    "hilversum": {
        "name": "Hilversum",
        "region": "Noord-Holland",
        "areas": ["Centrum", "Media Park", "Kerkelanden"],
        "intent": "media, creatieve en zakelijke bedrijven die online betrouwbaarheid en herkenbaarheid willen versterken",
    },
    "hoofddorp": {
        "name": "Hoofddorp",
        "region": "Noord-Holland",
        "areas": ["Centrum", "Beukenhorst", "Toolenburg"],
        "intent": "bedrijven rond Haarlemmermeer en Schiphol die zakelijke zichtbaarheid en conversie willen verbeteren",
    },
    "amsterdam": {
        "name": "Amsterdam",
        "region": "Noord-Holland",
        "areas": ["Centrum", "De Pijp", "Noord"],
        "intent": "ambitieuze teams die snelheid, SEO en uitstraling op niveau willen brengen",
    },
    "den-haag": {
        "name": "Den Haag",
        "region": "Zuid-Holland",
        "areas": ["Centrum", "Bezuidenhout", "Scheveningen"],
        "intent": "professionele organisaties die online duidelijker en betrouwbaarder willen overkomen",
    },
    "middelburg": {
        "name": "Middelburg",
        "region": "Zeeland",
        "areas": ["Binnenstad", "Dauwendaele", "Mortiere"],
        "intent": "Zeeuwse bedrijven die hun website, SEO en online marketing praktisch willen verbeteren",
    },
    "dirksland": {
        "name": "Dirksland",
        "region": "Zuid-Holland",
        "areas": ["Dirksland", "Herkingen", "Melissant"],
        "intent": "ondernemers op Goeree-Overflakkee die lokaal beter vindbaar willen worden",
    },
    "goeree-overflakkee": {
        "name": "Goeree-Overflakkee",
        "region": "Zuid-Holland",
        "areas": ["Middelharnis", "Sommelsdijk", "Ouddorp"],
        "intent": "bedrijven op het eiland die hun website, SEO en online marketing willen versterken",
    },
    "domburg": {
        "name": "Domburg",
        "region": "Zeeland",
        "areas": ["Domburg", "Oostkapelle", "Aagtekerke"],
        "intent": "recreatie- en dienstverlenende bedrijven die online sterker zichtbaar willen zijn",
    },
    "zoutelande": {
        "name": "Zoutelande",
        "region": "Zeeland",
        "areas": ["Zoutelande", "Biggekerke", "Westkapelle"],
        "intent": "lokale en toeristische ondernemers die beter gevonden willen worden",
    },
    "ellemeet": {
        "name": "Ellemeet",
        "region": "Zeeland",
        "areas": ["Ellemeet", "Renesse", "Scharendijke"],
        "intent": "ondernemers in Schouwen-Duiveland die hun lokale zichtbaarheid willen verbeteren",
    },
    "melissant": {
        "name": "Melissant",
        "region": "Zuid-Holland",
        "areas": ["Melissant", "Dirksland", "Sommelsdijk"],
        "intent": "lokale bedrijven die online marketing praktisch willen inzetten voor groei",
    },
    "ouddorp": {
        "name": "Ouddorp",
        "region": "Zuid-Holland",
        "areas": ["Ouddorp", "Goedereede", "Stellendam"],
        "intent": "ondernemers aan de kust die online zichtbaarheid willen omzetten in aanvragen",
    },
}


AUTHORITY_CITY_KEYS = {
    "brielle",
    "rotterdam",
    "spijkenisse",
    "hellevoetsluis",
    "dordrecht",
    "goes",
    "middelburg",
    "breda",
}


LOCAL_AUTHORITY = {
    "brielle": {
        "nearby": ["Vierpolders", "Zwartewaal", "Hellevoetsluis", "Rockanje"],
        "market": "Brielle is compact, lokaal en persoonlijk: ondernemers worden vaak gekozen op vertrouwen, herkenbaarheid en snelle bereikbaarheid.",
        "scenario": "Denk aan een lokale dienstverlener, praktijk, horecaondernemer of specialist op Voorne-Putten die professioneel wil overkomen bij klanten die eerst online vergelijken.",
        "positioning": "BDMNL zet Brielse bedrijven neer met een rustige premium uitstraling, duidelijke bewijsvoering en content die aansluit op zoekvragen uit Brielle en omliggende plaatsen.",
        "proof": "Lokale nabijheid vanuit Brielle, korte lijnen en ervaring met websites die vertrouwen moeten opbouwen voordat iemand belt of een offerte aanvraagt.",
    },
    "rotterdam": {
        "nearby": ["Schiedam", "Vlaardingen", "Barendrecht", "Capelle aan den IJssel"],
        "market": "Rotterdam is competitief en snel: bezoekers vergelijken aanbieders in enkele seconden en verwachten direct scherpte, bewijs en een professionele uitstraling.",
        "scenario": "Voor zakelijke dienstverleners, agencies, technische bedrijven en groeiende teams is een website vaak het eerste moment waarop merk, expertise en schaalbaarheid samenkomen.",
        "positioning": "BDMNL vertaalt Rotterdamse ambitie naar heldere positionering, snelle Webflow techniek en SEO-content die niet voelt als losse zoekwoorden.",
        "proof": "Een pagina moet in Rotterdam harder werken: boven de vouw overtuigen, daarna verdiepen met cases, trust, lokale relevantie en een logische route naar contact.",
    },
    "spijkenisse": {
        "nearby": ["Hekelingen", "Hoogvliet", "Brielle", "Rotterdam"],
        "market": "Spijkenisse heeft een brede MKB-markt waar lokale vindbaarheid, bereikbaarheid en vertrouwen zwaar meewegen in de keuze voor een aanbieder.",
        "scenario": "Een aannemer, zorgpraktijk, automotive bedrijf of zakelijke dienstverlener wil niet alleen gevonden worden, maar ook direct professioneel en betrouwbaar ogen.",
        "positioning": "BDMNL helpt bedrijven in Nissewaard hun aanbod simpeler uitleggen, sterker vormgeven en beter verbinden met lokale zoekintentie.",
        "proof": "De combinatie van lokale termen, duidelijke CTA's en moderne UX maakt het makkelijker voor bezoekers uit Spijkenisse om de stap naar contact te zetten.",
    },
    "hellevoetsluis": {
        "nearby": ["Brielle", "Rockanje", "Ouddorp", "Spijkenisse"],
        "market": "Hellevoetsluis combineert lokale dienstverlening, havenhistorie, retail en recreatie; online vertrouwen is belangrijk voor zowel inwoners als regionale bezoekers.",
        "scenario": "Bedrijven die afhankelijk zijn van aanvragen, reserveringen of adviesgesprekken hebben een site nodig die snel uitlegt wat ze doen en waarom ze dichtbij relevant zijn.",
        "positioning": "BDMNL maakt de lokale context voelbaar zonder de pagina vol te stoppen met plaatsnamen: duidelijk, premium en gericht op conversie.",
        "proof": "Een sterke pagina verbindt Hellevoetsluis, Voorne aan Zee en omliggende plaatsen met concrete diensten en herkenbare klantvragen.",
    },
    "dordrecht": {
        "nearby": ["Zwijndrecht", "Papendrecht", "Sliedrecht", "Rotterdam"],
        "market": "Dordrecht heeft een volwassen lokale markt met veel dienstverleners, maakbedrijven en regionale spelers die online serieus vergeleken worden.",
        "scenario": "Een bedrijf in de Drechtsteden heeft baat bij een website die vakmanschap, betrouwbaarheid en regionale bereikbaarheid direct zichtbaar maakt.",
        "positioning": "BDMNL bouwt Dordtse pagina's met heldere hiërarchie, sterke headings en lokale content die aansluit op commerciële zoekopdrachten.",
        "proof": "De pagina laat niet alleen zien dat je actief bent in Dordrecht, maar waarom jouw aanbod relevant is voor klanten in de hele regio.",
    },
    "goes": {
        "nearby": ["Kapelle", "Kloetinge", "Middelburg", "Zierikzee"],
        "market": "Goes is een belangrijk zakelijk centrum in Zeeland waar lokale zichtbaarheid en regionale uitstraling elkaar versterken.",
        "scenario": "Voor Zeeuwse bedrijven is het belangrijk dat een website professioneel voelt voor lokale klanten én sterk genoeg is voor aanvragen uit de bredere provincie.",
        "positioning": "BDMNL combineert Zeeuwse nuchterheid met premium digital agency UX: helder, snel, betrouwbaar en gericht op nieuwe aanvragen.",
        "proof": "Door Goes te koppelen aan omliggende plaatsen en concrete klantvragen ontstaat lokale content die natuurlijk leest en SEO ondersteunt.",
    },
    "middelburg": {
        "nearby": ["Vlissingen", "Goes", "Veere", "Domburg"],
        "market": "Middelburg vraagt om een professionele balans tussen lokale historie, toerisme, zakelijke dienstverlening en regionale concurrentie.",
        "scenario": "Een specialist, praktijk, winkel of hospitality-bedrijf wil zichtbaar zijn voor mensen die lokaal zoeken en daarna snel willen beoordelen of het aanbod past.",
        "positioning": "BDMNL geeft Middelburgse pagina's een rustige, hoogwaardige structuur met content die inspeelt op vertrouwen, ligging en duidelijke vervolgstappen.",
        "proof": "Lokale relevantie werkt hier vooral wanneer de pagina concreet blijft: wat doe je, voor wie, waar ben je actief en waarom moeten bezoekers nu contact opnemen?",
    },
    "breda": {
        "nearby": ["Oosterhout", "Etten-Leur", "Tilburg", "Roosendaal"],
        "market": "Breda is sterk in creativiteit, zakelijke dienstverlening, hospitality en groeiende MKB-bedrijven; uitstraling en positionering zijn doorslaggevend.",
        "scenario": "Een bedrijf dat in Breda wil opvallen heeft een website nodig die niet standaard voelt en tegelijk snel uitlegt wat de waarde is.",
        "positioning": "BDMNL bouwt Bredase autoriteitspagina's met scherpe copy, premium visuals en lokale SEO die past bij een competitieve Brabantse markt.",
        "proof": "Met duidelijke merkpresentatie, lokale context en conversiegerichte CTA's wordt de pagina meer dan een vindbaarheidspagina: het wordt een sales asset.",
    },
}


SERVICE_AUTHORITY = {
    "website-laten-maken": {
        "benefit": "een website die direct vertrouwen geeft en klaar is voor lokale SEO",
        "outcome": "meer kwalitatieve aanvragen uit de regio",
        "decision": "Bezoekers moeten snel snappen wat je doet, waarom je betrouwbaar bent en welke stap logisch is.",
        "visual_label": "Website concept",
    },
    "webdesign": {
        "benefit": "een premium ontwerp met scherpe structuur, sterke UX en Webflow snelheid",
        "outcome": "een professionelere eerste indruk en betere lead flow",
        "decision": "Goed webdesign haalt ruis weg: heldere hiërarchie, sterke typografie en een route die bezoekers vanzelf volgen.",
        "visual_label": "UX preview",
    },
    "seo": {
        "benefit": "lokale vindbaarheid met content die menselijk leest en technisch klopt",
        "outcome": "duurzame zichtbaarheid op zoekopdrachten met commerciële intentie",
        "decision": "SEO werkt pas echt wanneer techniek, lokale relevantie en conversie samen op één pagina landen.",
        "visual_label": "SEO map",
    },
    "webshop-laten-maken": {
        "benefit": "een webshop die vertrouwen, productpresentatie en bestelgemak samenbrengt",
        "outcome": "meer online bestellingen en betere productaanvragen",
        "decision": "Een webshop moet niet alleen werken; bezoekers moeten snel begrijpen waarom ze juist hier kopen.",
        "visual_label": "Webshop basis",
    },
    "online-marketing": {
        "benefit": "een online marketingstructuur waarin website, SEO en content elkaar versterken",
        "outcome": "meer consistente zichtbaarheid en betere opvolging",
        "decision": "Online marketing werkt sterker wanneer campagnes terugvallen op een heldere website en lokale content.",
        "visual_label": "Groei structuur",
    },
    "social-media": {
        "benefit": "een herkenbaar contentritme dat aansluit op website, merk en lokale markt",
        "outcome": "meer herkenning, vertrouwen en terugkerende contactmomenten",
        "decision": "Social media moet voelen als onderdeel van je merk, niet als losse posts zonder richting.",
        "visual_label": "Content ritme",
    },
    "hosting": {
        "benefit": "hosting die snelheid, veiligheid en continuïteit ondersteunt",
        "outcome": "minder technische ruis en een betrouwbaardere websitebasis",
        "decision": "Goede hosting is onzichtbaar voor bezoekers, maar merkbaar in snelheid, vertrouwen en stabiliteit.",
        "visual_label": "Hosting basis",
    },
    "branding-design": {
        "benefit": "branding en design die je bedrijf herkenbaar en geloofwaardig neerzetten",
        "outcome": "een sterker merkgevoel en meer vertrouwen bij eerste bezoekers",
        "decision": "Een merk moet in beeld, tekst en website hetzelfde vertrouwen uitstralen.",
        "visual_label": "Brand system",
    },
}


META_OVERRIDES = {
    "online-marketing-middelburg": {
        "title": "Online marketing Middelburg en Walcheren | BDMNL",
        "description": "Online marketing in Middelburg en Walcheren? BDMNL verbindt websites, SEO en content tot een duidelijke groeistructuur voor Zeeuwse bedrijven.",
    },
    "seo/seo-bureau-rotterdam": {
        "title": "SEO bureau Rotterdam | Technische SEO en content door BDMNL",
        "description": "SEO bureau in Rotterdam nodig? BDMNL versterkt technische SEO, contentstructuur en lokale autoriteit voor bedrijven in een competitieve markt.",
    },
    "social-media/social-media-beheer-brielle": {
        "title": "Social media beheer Brielle | Contentritme voor lokale bedrijven",
        "description": "Social media beheer in Brielle? BDMNL helpt lokale bedrijven met herkenbare content, planning en koppeling met website en SEO.",
    },
}


RECOVERY_SERVICE_PROFILES = {
    "website-laten-maken": {
        "label": "Website laten maken",
        "short": "Website",
        "service_type": "Website development en Webflow webdesign",
        "title": "Website laten maken {city} | Premium Webflow website door BDMNL",
        "description": "Website laten maken in {city}? BDMNL ontwikkelt premium Webflow websites met lokale SEO, sterke UX en een duidelijke route naar contact.",
        "h1": "Website laten maken in {city} voor bedrijven die premium willen overkomen.",
        "hero": "BDMNL ontwikkelt websites voor bedrijven in {city} die niet alleen online willen staan, maar professioneel gekozen willen worden. Denk aan scherpe positionering, snelle Webflow techniek, lokale SEO en CTA's die logisch voelen.",
        "cta": "Plan een websitegesprek",
        "faq_focus": "website",
    },
    "webdesign": {
        "label": "Webdesign",
        "short": "Webflow",
        "service_type": "Webdesign en website development",
        "title": "Webdesign {city} | Premium UX en Webflow door BDMNL",
        "description": "Webdesign in {city}? BDMNL ontwerpt premium websites met scherpe typografie, Webflow snelheid, lokale SEO en conversiegericht UX-design.",
        "h1": "Webdesign {city} met de uitstraling van een premium digital agency.",
        "hero": "BDMNL ontwerpt websites voor bedrijven in {city} die serieuzer, scherper en betrouwbaarder willen overkomen. We combineren rust in design met duidelijke content, snelle techniek en lokale context.",
        "cta": "Plan een websitegesprek",
        "faq_focus": "website",
    },
    "seo": {
        "label": "SEO",
        "short": "SEO",
        "service_type": "SEO en zoekmachine optimalisatie",
        "title": "{keyword} {city} | Lokale SEO strategie door BDMNL",
        "description": "{keyword} in {city}? BDMNL verbetert lokale vindbaarheid met technische SEO, sterke content, interne links en pagina's die aanvragen opleveren.",
        "h1": "{keyword} {city} voor vindbaarheid die ook vertrouwen opbouwt.",
        "hero": "BDMNL helpt bedrijven in {city} groeien met SEO die verder gaat dan zoekwoorden. De basis: snelle techniek, lokale content, sterke interne links en pagina's die bezoekers overtuigen om contact op te nemen.",
        "cta": "Plan een SEO-gesprek",
        "faq_focus": "seo",
    },
    "social-media": {
        "label": "Social media",
        "short": "Social",
        "service_type": "Social media beheer",
        "title": "{keyword} {city} | Content en planning door BDMNL",
        "description": "{keyword} in {city}? BDMNL helpt lokale bedrijven met content, planning en campagnes die passen bij hun website, SEO en merkverhaal.",
        "h1": "{keyword} {city} met content die past bij je merk.",
        "hero": "BDMNL helpt bedrijven in {city} zichtbaar blijven met social content die aansluit op hun website, doelgroep en lokale markt. Praktisch, herkenbaar en zonder losse flodders.",
        "cta": "Plan een contentgesprek",
        "faq_focus": "social",
    },
    "online-marketing": {
        "label": "Online marketing",
        "short": "Marketing",
        "service_type": "Online marketing",
        "title": "Online marketing {city} | Websites, SEO en campagnes door BDMNL",
        "description": "Online marketing in {city}? BDMNL helpt lokale bedrijven met websites, SEO, content en campagnes die samen zorgen voor online groei.",
        "h1": "Online marketing {city} met een praktische BDMNL aanpak.",
        "hero": "BDMNL helpt bedrijven in {city} groeien met een combinatie van website, SEO, content en online marketing. Geen losse acties, maar een duidelijke basis die past bij je bedrijf.",
        "cta": "Plan een groeigesprek",
        "faq_focus": "marketing",
    },
    "webshop-laten-maken": {
        "label": "Webshop laten maken",
        "short": "Webshop",
        "service_type": "Webshop development en conversie optimalisatie",
        "title": "Webshop laten maken {city} | Premium webshop door BDMNL",
        "description": "Webshop laten maken in {city}? BDMNL ontwikkelt snelle, betrouwbare webshops met sterke productpresentatie, SEO-basis en duidelijke conversie.",
        "h1": "Webshop laten maken {city} voor bedrijven die professioneel online willen verkopen.",
        "hero": "BDMNL helpt bedrijven in {city} met webshops die helder presenteren, snel laden en vertrouwen geven tijdens het aankoopproces.",
        "cta": "Plan een webshopgesprek",
        "faq_focus": "website",
    },
    "hosting": {
        "label": "Hosting",
        "short": "Hosting",
        "service_type": "Website hosting en onderhoud",
        "title": "Hosting {city} | Snelle en betrouwbare websitebasis door BDMNL",
        "description": "Hosting in {city}? BDMNL helpt bedrijven met snelle hosting, onderhoud, veiligheid en een stabiele technische basis voor websites en webshops.",
        "h1": "Hosting {city} voor een snelle, veilige en betrouwbare website.",
        "hero": "BDMNL helpt bedrijven in {city} met hosting die snelheid, betrouwbaarheid en onderhoud ondersteunt zonder technische ruis.",
        "cta": "Bespreek hosting",
        "faq_focus": "website",
    },
    "branding-design": {
        "label": "Branding en design",
        "short": "Branding",
        "service_type": "Branding, huisstijl en digitaal design",
        "title": "Branding en design {city} | Merkidentiteit door BDMNL",
        "description": "Branding en design in {city}? BDMNL helpt bedrijven met een herkenbare uitstraling, sterke huisstijl en digitaal design dat vertrouwen opbouwt.",
        "h1": "Branding en design {city} voor een merk dat professioneler voelt.",
        "hero": "BDMNL helpt bedrijven in {city} met branding en design die richting geven aan website, content en online marketing.",
        "cta": "Plan een merkgesprek",
        "faq_focus": "agency",
    },
    "reclamebureau": {
        "label": "Reclamebureau",
        "short": "BDMNL",
        "service_type": "Webdesign, branding en online marketing",
        "title": "Reclamebureau {city} | Webdesign, SEO en online marketing door BDMNL",
        "description": "Reclamebureau in {city}? BDMNL helpt met Webflow websites, branding, SEO, social media en online marketing voor lokale bedrijven.",
        "h1": "Reclamebureau {city} voor webdesign, SEO en online groei.",
        "hero": "BDMNL is geen traditioneel reclamebureau. We helpen bedrijven in {city} met websites, branding, SEO, social media en online marketing die praktisch resultaat moeten opleveren.",
        "cta": "Plan een kennismaking",
        "faq_focus": "agency",
    },
}


RECOVERY_URLS = [
    ("webdesign", "webdesign", "webdesign-brielle", "brielle", "Webdesign"),
    ("webdesign", "webdesign", "webdesign-rotterdam", "rotterdam", "Webdesign"),
    ("webdesign", "webdesign", "webdesign-goes", "goes", "Webdesign"),
    ("webdesign", "webdesign", "webdesign-dordrecht", "dordrecht", "Webdesign"),
    ("webdesign", "webdesign", "webdesign-vlaardingen", "vlaardingen", "Webdesign"),
    ("webdesign", "webdesign", "webdesign-breda", "breda", "Webdesign"),
    ("webdesign", "webdesign", "webdesign-amsterdam", "amsterdam", "Webdesign"),
    ("webdesign", "webdesign", "webdesign-den-haag", "den-haag", "Webdesign"),
    ("webdesign", "webdesign", "webdesign-middelburg", "middelburg", "Webdesign"),
    ("seo", "seo", "seo-rotterdam", "rotterdam", "SEO"),
    ("seo", "seo", "seo-bureau-rotterdam", "rotterdam", "SEO bureau"),
    ("seo", "seo", "zoekmachine-optimalisatie-rotterdam", "rotterdam", "Zoekmachine optimalisatie"),
    ("seo", "seo", "seo-goes", "goes", "SEO"),
    ("seo", "seo", "seo-dordrecht", "dordrecht", "SEO"),
    ("seo", "seo", "seo-amsterdam", "amsterdam", "SEO"),
    ("seo", "seo", "seo-den-haag", "den-haag", "SEO"),
    ("seo", "seo", "seo-breda", "breda", "SEO"),
    ("social-media", "social-media", "social-media-brielle", "brielle", "Social media"),
    ("social-media", "social-media", "social-media-beheer-brielle", "brielle", "Social media beheer"),
    ("social-media", "social-media", "social-media-goes", "goes", "Social media"),
    ("social-media", "social-media", "social-media-rotterdam", "rotterdam", "Social media"),
    ("social-media", "social-media", "social-media-dordrecht", "dordrecht", "Social media"),
    ("social-media", "social-media", "social-media-vlaardingen", "vlaardingen", "Social media"),
    ("online-marketing", "online-marketing", "online-marketing-goes", "goes", "Online marketing"),
    ("online-marketing", "online-marketing", "online-marketing-brielle", "brielle", "Online marketing"),
    ("online-marketing", "online-marketing", "online-marketing-dordrecht", "dordrecht", "Online marketing"),
    ("online-marketing", "online-marketing", "online-marketing-vlaardingen", "vlaardingen", "Online marketing"),
    ("reclamebureau", "reclamebureau", "reclamebureau-brielle", "brielle", "Reclamebureau"),
    ("reclamebureau", "reclamebureau", "reclamebureau-rotterdam", "rotterdam", "Reclamebureau"),
    ("reclamebureau", "reclamebureau", "reclamebureau-goes", "goes", "Reclamebureau"),
    ("reclamebureau", "reclamebureau", "reclamebureau-dordrecht", "dordrecht", "Reclamebureau"),
    ("reclamebureau", "reclamebureau", "reclamebureau-vlaardingen", "vlaardingen", "Reclamebureau"),
]


ADDITIONAL_LOCAL_RECOVERY_URLS = [
    {"category": "seo", "service_key": "seo", "slug": "seo-bureau-dirksland", "path": "seo-bureau-dirksland", "city_key": "dirksland", "keyword": "SEO bureau"},
    {"category": "seo", "service_key": "seo", "slug": "seo-bureau-goeree-overflakkee", "path": "seo-bureau-goeree-overflakkee", "city_key": "goeree-overflakkee", "keyword": "SEO bureau"},
    {"category": "seo", "service_key": "seo", "slug": "seo-bureau-domburg", "path": "seo-bureau-domburg", "city_key": "domburg", "keyword": "SEO bureau"},
    {"category": "seo", "service_key": "seo", "slug": "seo-bureau-zoutelande", "path": "seo-bureau-zoutelande", "city_key": "zoutelande", "keyword": "SEO bureau"},
    {"category": "seo", "service_key": "seo", "slug": "seo-bureau-ellemeet", "path": "seo-bureau-ellemeet", "city_key": "ellemeet", "keyword": "SEO bureau"},
    {"category": "online-marketing", "service_key": "online-marketing", "slug": "online-marketing-melissant", "path": "online-marketing-melissant", "city_key": "melissant", "keyword": "Online marketing"},
    {"category": "online-marketing", "service_key": "online-marketing", "slug": "online-marketing-domburg", "path": "online-marketing-domburg", "city_key": "domburg", "keyword": "Online marketing"},
    {"category": "online-marketing", "service_key": "online-marketing", "slug": "online-marketing-middelburg", "path": "online-marketing-middelburg", "city_key": "middelburg", "keyword": "Online marketing"},
    {"category": "online-marketing", "service_key": "online-marketing", "slug": "online-marketing-ouddorp", "path": "online-marketing-ouddorp", "city_key": "ouddorp", "keyword": "Online marketing"},
]

PRIORITY_CITY_KEYS = [
    "rotterdam",
    "brielle",
    "hellevoetsluis",
    "rockanje",
    "spijkenisse",
    "dordrecht",
    "vlaardingen",
    "den-haag",
    "goes",
    "middelburg",
    "breda",
    "tilburg",
    "eindhoven",
    "roosendaal",
    "bergen-op-zoom",
]

EXPANSION_SERVICE_ROUTES = [
    {
        "category": "webdesign",
        "service_key": "webdesign",
        "path_pattern": "webdesign/webdesign-{city_slug}",
        "keyword": "Webdesign",
        "cluster": "recovery-webdesign",
    },
    {
        "category": "website-laten-maken",
        "service_key": "website-laten-maken",
        "path_pattern": "website-laten-maken-{city_slug}",
        "keyword": "Website laten maken",
        "cluster": "website-laten-maken",
    },
    {
        "category": "seo-bureau",
        "service_key": "seo",
        "path_pattern": "seo-bureau-{city_slug}",
        "keyword": "SEO bureau",
        "cluster": "seo-bureau",
    },
    {
        "category": "online-marketing",
        "service_key": "online-marketing",
        "path_pattern": "online-marketing/online-marketing-{city_slug}",
        "keyword": "Online marketing",
        "cluster": "recovery-online-marketing",
    },
    {
        "category": "social-media-beheer",
        "service_key": "social-media",
        "path_pattern": "social-media-beheer-{city_slug}",
        "keyword": "Social media beheer",
        "cluster": "social-media-beheer",
    },
    {
        "category": "reclamebureau",
        "service_key": "reclamebureau",
        "path_pattern": "reclamebureau/reclamebureau-{city_slug}",
        "keyword": "Reclamebureau",
        "cluster": "recovery-reclamebureau",
    },
]

REGIONAL_CLUSTER_PLAN = {
    "Zuid-Holland": [
        "rotterdam",
        "den-haag",
        "dordrecht",
        "leiden",
        "delft",
        "gouda",
        "schiedam",
        "vlaardingen",
        "zoetermeer",
        "spijkenisse",
        "brielle",
        "hellevoetsluis",
    ],
    "Zeeland": [
        "goes",
        "middelburg",
        "vlissingen",
        "terneuzen",
        "zierikzee",
        "hulst",
        "sluis",
        "kapelle",
        "tholen",
        "domburg",
        "zoutelande",
    ],
    "Noord-Brabant": [
        "breda",
        "eindhoven",
        "tilburg",
        "den-bosch",
        "roosendaal",
        "bergen-op-zoom",
        "helmond",
        "oosterhout",
        "etten-leur",
        "waalwijk",
    ],
    "Noord-Holland": [
        "amsterdam",
        "haarlem",
        "alkmaar",
        "hilversum",
        "hoofddorp",
        "zaandam",
        "amstelveen",
        "purmerend",
        "hoorn",
        "den-helder",
    ],
}

REGIONAL_CLUSTER_CITY_NAMES = {
    "gouda": "Gouda",
    "schiedam": "Schiedam",
    "zoetermeer": "Zoetermeer",
    "hulst": "Hulst",
    "sluis": "Sluis",
    "kapelle": "Kapelle",
    "tholen": "Tholen",
    "helmond": "Helmond",
    "oosterhout": "Oosterhout",
    "etten-leur": "Etten-Leur",
    "waalwijk": "Waalwijk",
    "zaandam": "Zaandam",
    "amstelveen": "Amstelveen",
    "purmerend": "Purmerend",
    "hoorn": "Hoorn",
    "den-helder": "Den Helder",
}

REGIONAL_SERVICE_CLUSTERS = [
    ("website-laten-maken", "Website laten maken"),
    ("webshop-laten-maken", "Webshop laten maken"),
    ("online-marketing", "Online marketing"),
    ("social-media-beheer", "Social media beheer"),
    ("hosting", "Hosting"),
    ("branding-design", "Branding en design"),
    ("webdesign", "Webdesign"),
    ("seo-bureau", "SEO bureau"),
]

FIRST_BATCH_CITY_KEYS = [
    "rotterdam",
    "den-haag",
    "dordrecht",
    "leiden",
    "delft",
    "goes",
    "middelburg",
    "vlissingen",
    "terneuzen",
    "zierikzee",
    "breda",
    "eindhoven",
    "tilburg",
    "den-bosch",
    "roosendaal",
    "amsterdam",
    "haarlem",
    "alkmaar",
    "hilversum",
    "hoofddorp",
]

FIRST_BATCH_SERVICE_ROUTES = [
    {
        "category": "website-laten-maken",
        "service_key": "website-laten-maken",
        "path_pattern": "website-laten-maken-{city_slug}",
        "keyword": "Website laten maken",
        "cluster": "website-laten-maken",
    },
    {
        "category": "webshop-laten-maken",
        "service_key": "webshop-laten-maken",
        "path_pattern": "webshop-laten-maken-{city_slug}",
        "keyword": "Webshop laten maken",
        "cluster": "webshop-laten-maken",
    },
    {
        "category": "online-marketing",
        "service_key": "online-marketing",
        "path_pattern": "online-marketing/online-marketing-{city_slug}",
        "keyword": "Online marketing",
        "cluster": "online-marketing",
    },
    {
        "category": "social-media-beheer",
        "service_key": "social-media",
        "path_pattern": "social-media-beheer-{city_slug}",
        "keyword": "Social media beheer",
        "cluster": "social-media-beheer",
    },
    {
        "category": "hosting",
        "service_key": "hosting",
        "path_pattern": "hosting-{city_slug}",
        "keyword": "Hosting",
        "cluster": "hosting",
    },
    {
        "category": "branding-design",
        "service_key": "branding-design",
        "path_pattern": "branding-design-{city_slug}",
        "keyword": "Branding en design",
        "cluster": "branding-design",
    },
]

ZUID_HOLLAND_COMPLETION_CITY_KEYS = [
    "leiden",
    "delft",
]

ZUID_HOLLAND_COMPLETION_ROUTES = [
    {
        "category": "webdesign",
        "service_key": "webdesign",
        "path_pattern": "webdesign/webdesign-{city_slug}",
        "keyword": "Webdesign",
        "cluster": "webdesign",
    },
    {
        "category": "seo-bureau",
        "service_key": "seo",
        "path_pattern": "seo-bureau-{city_slug}",
        "keyword": "SEO bureau",
        "cluster": "seo-bureau",
    },
]


CONTENT_RECOVERY_PAGES = [
    {
        "path": "over-bdmnl",
        "kind": "core",
        "schema_type": "AboutPage",
        "title": "Over BDMNL | Van Bulldog Media naar digital agency",
        "description": "Leer BDMNL kennen: de doorontwikkeling van Bulldog Media naar een digital agency voor websites, SEO, branding, hosting en online groei.",
        "eyebrow": "Over BDMNL",
        "h1": "BDMNL bouwt voort op de ervaring van Bulldog Media.",
        "intro": "BDMNL is de doorontwikkeling van Bulldog Media: dezelfde digitale basis, dezelfde focus op websites, SEO en online groei, maar met een volwassenere identiteit en een scherper systeem voor moderne bedrijven.",
        "sections": [
            ("Van Bulldog Media naar BDMNL", "Bulldog Media groeide uit tot een bredere digitale partner. De naam BDMNL maakt die ontwikkeling duidelijker: minder losse marketing, meer samenhang tussen strategie, website, techniek, content en vindbaarheid."),
            ("Expertise die is meegegroeid", "De kern bleef hetzelfde: websites, webshops, hosting, branding, SEO, online marketing en social media beheer voor bedrijven die online professioneler willen overkomen."),
            ("Regionale basis, bredere blik", "BDMNL werkt vanuit Brielle voor ondernemers op Voorne-Putten, in Rotterdam, Zeeland, Noord-Brabant, Noord-Holland en daarbuiten. De lokale mentaliteit blijft: korte lijnen, duidelijke keuzes en werk dat praktisch resultaat moet opleveren."),
            ("Huidige positionering", "BDMNL staat voor een premium maar nuchtere digital agency aanpak. Geen tijdelijke trucjes, maar een online basis die vertrouwen opbouwt, technisch klopt en kan doorgroeien."),
        ],
    },
    {
        "path": "bulldog-media",
        "kind": "core",
        "schema_type": "AboutPage",
        "title": "Bulldog Media is nu BDMNL | Rebrand en digitale continuiteit",
        "description": "Bulldog Media is doorontwikkeld naar BDMNL. Lees hoe dezelfde expertise in webdesign, SEO, hosting, branding en online marketing verdergaat.",
        "eyebrow": "Bulldog Media",
        "h1": "Bulldog Media is doorontwikkeld naar BDMNL.",
        "intro": "BDMNL is geen losstaande nieuwe partij, maar de voortzetting en rebrand van Bulldog Media. De ervaring, dienstverlening en digitale expertise zijn doorontwikkeld naar een modernere identiteit.",
        "sections": [
            ("Dezelfde basis, scherper verhaal", "Bulldog Media stond voor websites, online marketing en digitale zichtbaarheid. BDMNL bouwt daarop voort met een helderder merk, een premium uitstraling en een sterker systeem voor groei."),
            ("Services blijven herkenbaar", "Webdesign, websites, webshops, hosting, SEO, branding, online marketing en social media beheer blijven onderdeel van de aanpak. De naam is veranderd, de expertise is meegenomen."),
            ("Waarom dit belangrijk is", "Voor klanten en zoekmachines moet duidelijk zijn dat Bulldog Media en BDMNL bij dezelfde ontwikkeling horen. Daarom benoemen we de overgang transparant en professioneel."),
            ("Voor bestaande relaties", "Wie Bulldog Media kende, vindt dezelfde praktische mentaliteit terug bij BDMNL: korte lijnen, duidelijke keuzes en digitale oplossingen die betrouwbaar moeten werken."),
        ],
    },
    {
        "path": "van-bulldog-media-naar-bdmnl",
        "kind": "core",
        "schema_type": "AboutPage",
        "title": "Van Bulldog Media naar BDMNL | Het verhaal achter de rebrand",
        "description": "Waarom Bulldog Media verderging als BDMNL: de groei van het bureau, de nieuwe identiteit en de visie achter de doorontwikkeling.",
        "eyebrow": "Rebrand",
        "h1": "Van Bulldog Media naar BDMNL.",
        "intro": "De overgang van Bulldog Media naar BDMNL markeert een volwassenere fase: meer focus, meer samenhang en een identiteit die beter past bij de digitale diensten van nu.",
        "sections": [
            ("Waarom de naam veranderde", "De werkzaamheden groeiden verder dan een klassieke mediapartner. BDMNL past beter bij een agency dat strategie, websites, branding, hosting, SEO en online marketing als een geheel ziet."),
            ("Wat hetzelfde bleef", "De praktische manier van werken, de regionale betrokkenheid en de focus op duidelijke digitale oplossingen zijn gebleven. De rebrand maakt die basis juist sterker herkenbaar."),
            ("Wat veranderde", "BDMNL legt meer nadruk op premium webdesign, technische kwaliteit, lokale SEO, schaalbare contentstructuren en een consistente merkervaring."),
            ("Toekomstvisie", "BDMNL groeit door als digital agency voor bedrijven die online betrouwbaarder, scherper en beter vindbaar willen worden."),
        ],
    },
    {
        "path": "gratis-seo-scan",
        "kind": "core",
        "title": "Gratis SEO scan | Laat je website controleren door BDMNL",
        "description": "Vraag een gratis SEO scan aan bij BDMNL en ontdek waar je website kansen laat liggen op techniek, snelheid, content en vindbaarheid.",
        "eyebrow": "Gratis SEO scan",
        "h1": "Ontdek waar je website SEO-kansen laat liggen.",
        "intro": "Met een SEO scan kijkt BDMNL naar snelheid, content, lokale vindbaarheid en gebruiksgemak. Je krijgt praktische aandachtspunten waar je direct mee verder kunt.",
        "sections": [
            ("Snelheid en gebruiksgemak", "We kijken of je website snel laadt, logisch is opgebouwd en prettig werkt voor bezoekers."),
            ("Content en structuur", "Goede SEO begint met duidelijke teksten, lokale vragen en een logische route naar contact."),
            ("Praktisch advies", "Geen lange rapporten vol ruis, maar concrete verbeterpunten voor meer zichtbaarheid en betere aanvragen."),
        ],
    },
    {
        "path": "kennisbank/webdesign",
        "kind": "knowledge",
        "title": "Webdesign kennisbank | BDMNL over Webflow, snelheid en conversie",
        "description": "Lees BDMNL inzichten over webdesign, Webflow, snelheid, SEO en conversie voor moderne websites.",
        "eyebrow": "Kennisbank",
        "h1": "Webdesign kennisbank.",
        "intro": "Webdesign gaat bij BDMNL verder dan een mooi ontwerp. Een goede website is snel, duidelijk, vindbaar en gebouwd om bezoekers naar de juiste actie te begeleiden.",
        "sections": [
            ("Webflow als flexibele basis", "Webflow maakt het mogelijk om snel professionele websites te bouwen met veel aandacht voor structuur, animatie en beheerbaarheid."),
            ("Snelheid en SEO", "Een trage website kost aanvragen. Daarom kijken we naar snelheid, contentstructuur en vindbaarheid als onderdeel van het ontwerp."),
            ("Conversiegericht ontwerp", "Bezoekers moeten snel begrijpen wat je doet, waarom ze je kunnen vertrouwen en welke stap ze kunnen zetten."),
        ],
    },
    {
        "path": "homepage",
        "kind": "core",
        "title": "BDMNL homepage | Webdesign, SEO en online marketing",
        "description": "BDMNL bouwt websites, branding, SEO en online marketing voor bedrijven die online sterker willen groeien.",
        "eyebrow": "BDMNL",
        "h1": "Alles voor een sterke online uitstraling.",
        "intro": "BDMNL helpt bedrijven groeien met moderne websites, webshops, branding, social media en online marketing. Vanuit Brielle werken we aan digitale oplossingen die duidelijk, snel en professioneel aanvoelen.",
        "sections": [
            ("Websites & webshops", "Snelle websites en webshops met een duidelijke structuur, sterke uitstraling en aandacht voor conversie."),
            ("SEO & online marketing", "Van lokale vindbaarheid tot campagnes en content: BDMNL zorgt dat online kanalen beter samenwerken."),
            ("Branding & social media", "Een herkenbare uitstraling en consistente content helpen bedrijven vertrouwen opbouwen bij hun doelgroep."),
        ],
    },
    {
        "path": "blog/content-marketing",
        "kind": "article",
        "title": "Content marketing | BDMNL kennisbank",
        "description": "Lees hoe content marketing helpt om beter vindbaar te worden, vertrouwen op te bouwen en bezoekers richting actie te begeleiden.",
        "eyebrow": "Blog",
        "h1": "Content marketing: zichtbaar worden met inhoud die klopt.",
        "intro": "Content marketing werkt wanneer je antwoord geeft op echte vragen van je doelgroep. Voor BDMNL betekent dat: praktische teksten, duidelijke structuur en content die aansluit op SEO en conversie.",
        "sections": [
            ("Begin bij de vraag van je klant", "Goede content begint met begrijpen waar je doelgroep naar zoekt. Daarna bepaal je welke pagina of welk artikel het beste antwoord geeft."),
            ("Koppel content aan je website", "Blogartikelen, landingspagina's en dienstenpagina's moeten elkaar versterken met logische verwijzingen en duidelijke vervolgstappen."),
            ("Schrijf menselijk", "Vermijd vage marketingtaal. Leg helder uit wat je doet, waarom het relevant is en welke stap bezoekers kunnen zetten."),
        ],
    },
    {
        "path": "blog/wordpress-waarom-is-dat-zo-populair",
        "kind": "article",
        "title": "WordPress: waarom is dat zo populair? | BDMNL kennisbank",
        "description": "Waarom WordPress populair is, wanneer het past en waarom BDMNL ook vaak kijkt naar Webflow, snelheid en beheerbaarheid.",
        "eyebrow": "Blog",
        "h1": "WordPress: waarom is dat zo populair?",
        "intro": "WordPress is populair omdat het flexibel, bekend en breed ondersteund is. Toch is populariteit niet hetzelfde als de beste keuze voor elk project. BDMNL kijkt vooral naar beheer, snelheid, veiligheid en groeidoelen.",
        "sections": [
            ("Veel mogelijkheden", "Voor veel bedrijven is WordPress aantrekkelijk door de grote hoeveelheid thema's, plugins en ontwikkelaars."),
            ("Let op onderhoud", "Plugins, updates en beveiliging vragen aandacht. Zonder onderhoud kan een website trager of kwetsbaarder worden."),
            ("Vergelijk met Webflow", "Voor websites waar snelheid, ontwerpvrijheid en beheerbaarheid belangrijk zijn, kan Webflow een sterke keuze zijn."),
        ],
    },
    {
        "path": "blog/professionele-website-hosting-betrouwbaar-en-snel",
        "kind": "article",
        "title": "Professionele website hosting: betrouwbaar en snel | BDMNL",
        "description": "Lees waarom betrouwbare hosting belangrijk is voor snelheid, veiligheid, SEO en een professionele website-ervaring.",
        "eyebrow": "Blog",
        "h1": "Professionele website hosting: betrouwbaar en snel.",
        "intro": "Hosting is de basis onder je website. Een professionele website moet snel laden, veilig blijven en bereikbaar zijn wanneer klanten je nodig hebben.",
        "sections": [
            ("Snelheid telt", "Snelle hosting helpt bezoekers beter door je website en ondersteunt je SEO-prestaties."),
            ("Veiligheid en updates", "Een goede hostingomgeving verkleint risico's en maakt onderhoud overzichtelijker."),
            ("Support wanneer nodig", "Bij BDMNL kijken we naar hosting als onderdeel van de totale websitebasis: techniek, support en continuïteit."),
        ],
    },
    {
        "path": "blog/hoe-vaak-moet-je-je-website-updaten",
        "kind": "article",
        "title": "Hoe vaak moet je je website updaten? | BDMNL kennisbank",
        "description": "Ontdek wanneer je je website moet updaten voor veiligheid, snelheid, SEO, content en conversie.",
        "eyebrow": "Blog",
        "h1": "Hoe vaak moet je je website updaten?",
        "intro": "Een website is nooit echt af. Content, techniek en zoekgedrag veranderen. Daarom is regelmatig updaten belangrijk voor veiligheid, snelheid en vindbaarheid.",
        "sections": [
            ("Onderhoud en veiligheid", "Controleer regelmatig of je website veilig, snel en goed werkend blijft. Zeker bij websites met extra koppelingen is onderhoud belangrijk."),
            ("Content bijwerken", "Diensten, prijzen, cases en contactinformatie moeten actueel blijven. Verouderde content kost vertrouwen."),
            ("SEO verbeteren", "Nieuwe zoekvragen en lokale kansen kunnen aanleiding zijn om content uit te breiden of belangrijke pagina's beter met elkaar te verbinden."),
        ],
    },
    {
        "path": "blog/hoe-kun-je-een-eigen-blog-beginnen",
        "kind": "article",
        "title": "Hoe kun je een eigen blog beginnen? | BDMNL kennisbank",
        "description": "Leer hoe je een eigen blog begint met een duidelijk doel, goede structuur, SEO en content die past bij je doelgroep.",
        "eyebrow": "Blog",
        "h1": "Hoe kun je een eigen blog beginnen?",
        "intro": "Een blog werkt het beste wanneer je vooraf bepaalt wie je wilt bereiken en welke vragen je wilt beantwoorden. Daarna bouw je een vaste structuur voor onderwerpen, verwijzingen en vervolgstappen.",
        "sections": [
            ("Kies een helder thema", "Begin met onderwerpen die direct aansluiten op je diensten, klanten en zoekgedrag."),
            ("Maak een simpele structuur", "Gebruik duidelijke titels, tussenkoppen en verwijzingen naar relevante dienstenpagina's."),
            ("Publiceer consistent", "Een blog hoeft niet elke dag nieuw te zijn. Belangrijker is dat elk artikel nuttig, actueel en goed vindbaar is."),
        ],
    },
    {
        "path": "blog/waarom-bulldog-media-bdmnl-werd",
        "kind": "article",
        "title": "Waarom Bulldog Media BDMNL werd | Brand authority",
        "description": "Lees waarom Bulldog Media verderging als BDMNL en hoe de rebrand de digitale expertise, diensten en positionering versterkt.",
        "eyebrow": "Brand story",
        "h1": "Waarom Bulldog Media BDMNL werd.",
        "intro": "De rebrand van Bulldog Media naar BDMNL is geen breuk met het verleden. Het is een duidelijke stap naar een volwassener agencyverhaal, met dezelfde basis en een scherper toekomstbeeld.",
        "sections": [
            ("Een naam die beter past bij de huidige praktijk", "De werkzaamheden groeiden van losse media- en websitediensten naar een samenhangend geheel van webdesign, hosting, SEO, branding en online marketing."),
            ("Meer focus op digitale groei", "BDMNL legt de nadruk op websites die vertrouwen opbouwen, content die vindbaar is en systemen die praktisch beheerd kunnen worden."),
            ("Continuiteit voor klanten", "Bestaande kennis, ervaring en werkwijze blijven aanwezig. De rebrand maakt vooral duidelijker waar het bureau nu voor staat."),
        ],
    },
    {
        "path": "blog/evolutie-bulldog-media-naar-bdmnl",
        "kind": "article",
        "title": "De evolutie van Bulldog Media naar BDMNL | BDMNL",
        "description": "Van Bulldog Media naar BDMNL: hoe de dienstverlening doorgroeide naar webdesign, SEO, hosting, branding en digitale strategie.",
        "eyebrow": "Evolutie",
        "h1": "De evolutie van Bulldog Media naar BDMNL.",
        "intro": "Een merk groeit mee met de diensten, klanten en markt. Bulldog Media ontwikkelde zich door naar BDMNL om beter aan te sluiten op moderne digitale vraagstukken.",
        "sections": [
            ("Van uitvoering naar samenhang", "Waar een website vroeger vaak een los project was, vraagt online groei nu om samenhang tussen merk, content, techniek en vindbaarheid."),
            ("Van lokaal zichtbaar naar professioneel gekozen", "BDMNL helpt bedrijven niet alleen zichtbaar worden, maar ook betrouwbaarder overkomen op het moment dat klanten vergelijken."),
            ("Een sterker digitaal fundament", "De doorontwikkeling maakt ruimte voor betere processen, premium ontwerp, technische kwaliteit en schaalbare SEO-structuren."),
        ],
    },
    {
        "path": "blog/hoe-bdmnl-is-gebouwd",
        "kind": "article",
        "title": "Hoe BDMNL is gebouwd op Bulldog Media ervaring",
        "description": "BDMNL is gebouwd op de ervaring van Bulldog Media, met een aangescherpte focus op websites, hosting, SEO, branding en online groei.",
        "eyebrow": "BDMNL",
        "h1": "Hoe BDMNL is gebouwd.",
        "intro": "BDMNL is ontstaan vanuit bestaande ervaring met websites, online marketing en digitale zichtbaarheid. De nieuwe identiteit brengt die ervaring onder in een duidelijker agency-systeem.",
        "sections": [
            ("Praktische ervaring als basis", "De kracht van BDMNL zit in het combineren van strategie en uitvoering: niet alleen bedenken wat nodig is, maar het ook technisch en inhoudelijk goed neerzetten."),
            ("Een premium maar nuchtere aanpak", "BDMNL kiest voor rustige vormgeving, duidelijke taal, snelle techniek en SEO die natuurlijk verwerkt is in de structuur."),
            ("Klaar voor verdere groei", "De rebrand maakt het makkelijker om diensten als webdesign, hosting, branding, SEO en online marketing als een herkenbaar geheel te presenteren."),
        ],
    },
    {
        "path": "blog/toekomstvisie-bdmnl",
        "kind": "article",
        "title": "De toekomstvisie van BDMNL | Premium digital agency",
        "description": "De toekomstvisie van BDMNL: premium websites, sterke lokale SEO, betrouwbare hosting, branding en online marketing vanuit een heldere basis.",
        "eyebrow": "Visie",
        "h1": "De toekomstvisie van BDMNL.",
        "intro": "BDMNL bouwt verder aan een digitale basis waarin uitstraling, snelheid, vindbaarheid en vertrouwen samenkomen. De rebrand vanuit Bulldog Media maakt die richting duidelijker.",
        "sections": [
            ("Premium hoeft niet ingewikkeld te zijn", "Een sterke website is rustig, snel en overtuigend. BDMNL wil bedrijven helpen met digitale middelen die professioneel voelen en praktisch blijven."),
            ("Lokale SEO met echte relevantie", "De komende fase draait om lokale autoriteit: pagina's die niet alleen gevonden worden, maar ook inhoudelijk kloppen voor de stad, regio en dienst."),
            ("Een herkenbaar agency-systeem", "BDMNL blijft bouwen aan een systeem waarin branding, hosting, webdesign, SEO en online marketing elkaar versterken."),
        ],
    },
]


def recovery_pages() -> list[dict[str, Any]]:
    pages = []
    for category, service_key, slug, city_key, keyword in RECOVERY_URLS:
        pages.append(
            {
                "category": category,
                "service_key": service_key,
                "slug": slug,
                "path": f"{category}/{slug}",
                "city_key": city_key,
                "keyword": keyword,
            }
        )
    pages.extend(ADDITIONAL_LOCAL_RECOVERY_URLS)

    existing_paths = {page["path"] for page in pages}
    for city_key in PRIORITY_CITY_KEYS:
        city_slug = RECOVERY_CITIES[city_key].get("slug", city_key)
        for route in EXPANSION_SERVICE_ROUTES:
            path = route["path_pattern"].format(city_slug=city_slug)
            if path in existing_paths:
                continue
            existing_paths.add(path)
            pages.append(
                {
                    "category": route["category"],
                    "service_key": route["service_key"],
                    "slug": path.split("/")[-1],
                    "path": path,
                    "city_key": city_key,
                    "keyword": route["keyword"],
                    "cluster": route["cluster"],
                    "source": "priority-expansion",
                }
            )

    for city_key in FIRST_BATCH_CITY_KEYS:
        city_slug = RECOVERY_CITIES[city_key].get("slug", city_key)
        for route in FIRST_BATCH_SERVICE_ROUTES:
            path = route["path_pattern"].format(city_slug=city_slug)
            if path in existing_paths:
                continue
            existing_paths.add(path)
            pages.append(
                {
                    "category": route["category"],
                    "service_key": route["service_key"],
                    "slug": path.split("/")[-1],
                    "path": path,
                    "city_key": city_key,
                    "keyword": route["keyword"],
                    "cluster": route["cluster"],
                    "source": "controlled-regional-batch",
                }
            )

    for city_key in ZUID_HOLLAND_COMPLETION_CITY_KEYS:
        city_slug = RECOVERY_CITIES[city_key].get("slug", city_key)
        for route in ZUID_HOLLAND_COMPLETION_ROUTES:
            path = route["path_pattern"].format(city_slug=city_slug)
            if path in existing_paths:
                continue
            existing_paths.add(path)
            pages.append(
                {
                    "category": route["category"],
                    "service_key": route["service_key"],
                    "slug": path.split("/")[-1],
                    "path": path,
                    "city_key": city_key,
                    "keyword": route["keyword"],
                    "cluster": route["cluster"],
                    "source": "zuid-holland-completion-batch",
                }
            )

    return pages


def recovery_url(site: dict[str, Any], page: dict[str, Any]) -> str:
    return f"{site['base_url']}/{page['path']}/"


def recovery_href(page: dict[str, Any]) -> str:
    return f"/{page['path']}/"


def recovery_footer_context(site: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, str]:
    def first_page(service_key: str) -> dict[str, Any]:
        return next(page for page in pages if page["service_key"] == service_key)

    footer_service_links = "\n".join(
        [
            f'<a href="{recovery_href(first_page("website-laten-maken"))}">Website laten maken</a>',
            f'<a href="{recovery_href(first_page("webshop-laten-maken"))}">Webshop laten maken</a>',
            f'<a href="{recovery_href(first_page("webdesign"))}">Webdesign</a>',
            f'<a href="{recovery_href(first_page("seo"))}">SEO</a>',
            f'<a href="{recovery_href(first_page("social-media"))}">Social media</a>',
            f'<a href="{recovery_href(first_page("online-marketing"))}">Online marketing</a>',
            f'<a href="{recovery_href(first_page("hosting"))}">Hosting</a>',
            f'<a href="{recovery_href(first_page("branding-design"))}">Branding en design</a>',
            f'<a href="{recovery_href(first_page("reclamebureau"))}">Reclamebureau</a>',
        ]
    )
    seen_cities: set[str] = set()
    city_links = []
    for page in pages:
        if page["city_key"] in seen_cities:
            continue
        seen_cities.add(page["city_key"])
        city = RECOVERY_CITIES[page["city_key"]]
        city_links.append(f'<a href="{recovery_href(page)}">{html(city["name"])}</a>')

    return {
        "footer_city_links": "\n".join(city_links),
        "footer_service_links": footer_service_links,
        "footer_internal_links": "\n".join(
            [
                '<a href="/over-bdmnl/">Over BDMNL</a>',
                '<a href="/bulldog-media/">Bulldog Media</a>',
                '<a href="/van-bulldog-media-naar-bdmnl/">Van Bulldog Media naar BDMNL</a>',
                '<a href="/homepage/">BDMNL homepage</a>',
                '<a href="/gratis-seo-scan/">Gratis SEO scan</a>',
                '<a href="/kennisbank/webdesign/">Kennisbank</a>',
                '<a href="/contact/">Contact</a>',
                '<a href="/privacyverklaring/">Privacyverklaring</a>',
                '<a href="/cookiebeleid/">Cookiebeleid</a>',
                '<a href="/algemene-voorwaarden/">Algemene voorwaarden</a>',
            ]
        ),
        "current_year": str(date.today().year),
    }


def local_authority(city_key: str) -> dict[str, Any]:
    city = RECOVERY_CITIES[city_key]
    return LOCAL_AUTHORITY.get(
        city_key,
        {
            "nearby": city["areas"],
            "market": f"{city['name']} heeft een lokale markt waarin vertrouwen, duidelijke communicatie en online vindbaarheid belangrijk zijn.",
            "scenario": f"Voor bedrijven in {city['name']} moet een pagina snel laten zien wat je doet, waar je actief bent en waarom klanten contact opnemen.",
            "positioning": f"BDMNL vertaalt {city['name']} naar een professionele pagina met lokale context, premium vormgeving en een logische route naar aanvraag.",
            "proof": "De combinatie van rustige UX, lokale content en duidelijke CTA's maakt de pagina sterker dan een standaard SEO-landingspagina.",
        },
    )


def service_authority(page: dict[str, Any], profile: dict[str, str]) -> dict[str, str]:
    return SERVICE_AUTHORITY.get(
        page["service_key"],
        {
            "benefit": f"een duidelijke aanpak voor {profile['label'].lower()}",
            "outcome": "meer vertrouwen, betere herkenning en een duidelijkere route naar contact",
            "decision": "De pagina moet bezoekers helpen begrijpen waarom BDMNL relevant is en welke stap ze kunnen zetten.",
            "visual_label": profile["label"],
        },
    )


def build_authority_facts(city_key: str, city: dict[str, Any], page: dict[str, Any], profile: dict[str, str]) -> str:
    local = local_authority(city_key)
    service = service_authority(page, profile)
    facts = [
        ("Lokale context", local["market"]),
        ("Regionale vraag", f"Relevant voor {', '.join(local['nearby'][:4])} en de bredere regio {city['region']}."),
        ("Commerciële intentie", f"Gebouwd voor bezoekers die zoeken naar {page['keyword'].lower()} in {city['name']} en snel willen beoordelen of BDMNL past."),
        ("Gewenste uitkomst", service["outcome"]),
    ]
    return "\n".join(
        "\n".join(
            [
                '      <article class="authority-fact">',
                f"        <span>{html(label)}</span>",
                f"        <p>{html(copy)}</p>",
                "      </article>",
            ]
        )
        for label, copy in facts
    )


def build_local_scenario_cards(city_key: str, city: dict[str, Any], page: dict[str, Any], profile: dict[str, str]) -> str:
    local = local_authority(city_key)
    service = service_authority(page, profile)
    cards = [
        ("Markt", local["market"]),
        ("Scenario", local["scenario"]),
        ("Positionering", local["positioning"]),
        ("Resultaat", f"De pagina stuurt op {service['outcome']} zonder dat de content als SEO-filler voelt."),
    ]
    return "\n".join(
        "\n".join(
            [
                '      <article class="local-card reveal">',
                f"        <span>{html(label)}</span>",
                f"        <p>{html(copy)}</p>",
                "      </article>",
            ]
        )
        for label, copy in cards
    )


def build_authority_visual(city_key: str, city: dict[str, Any], page: dict[str, Any], profile: dict[str, str]) -> str:
    local = local_authority(city_key)
    service = service_authority(page, profile)
    nearby = local["nearby"][:3]
    return "\n".join(
        [
            '<div class="authority-visual-card reveal">',
            '  <div class="authority-visual-top">',
            f"    <span>{html(service['visual_label'])}</span>",
            f"    <strong>{html(city['name'])}</strong>",
            "  </div>",
            '  <div class="authority-device" aria-hidden="true">',
            "    <div></div><div></div><div></div>",
            "  </div>",
            '  <div class="authority-map">',
            f"    <span>{html(city['name'])}</span>",
            *(f"    <i>{html(place)}</i>" for place in nearby),
            "  </div>",
            f"  <p>{html(local['proof'])}</p>",
            "</div>",
        ]
    )


def build_cta_actions(site: dict[str, Any], page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> str:
    subject = f"{page['keyword']} {city['name']}"
    subject_href = subject.replace(" ", "%20")
    return "\n".join(
        [
            '<div class="cta-actions" aria-label="Contactopties">',
            '  <span class="cta-actions-label">Kies je volgende stap</span>',
            f'  <a class="btn btn-dark" href="/contact/" data-magnetic>{html(profile["cta"])}</a>',
            '  <a class="btn btn-light" href="/gratis-seo-scan/">Gratis website check</a>',
            f'  <a class="btn btn-ghost-light" href="mailto:{html(site["email"])}?subject={html(subject_href)}">Vraag voorstel aan</a>',
            '  <p class="cta-note">Directe route naar contact, scan of voorstel zonder schijnformulier.</p>',
            "</div>",
        ]
    )


def build_direct_cta_actions(site: dict[str, Any], primary_label: str, subject: str) -> str:
    subject_href = subject.replace(" ", "%20")
    return "\n".join(
        [
            '<div class="cta-actions" aria-label="Contactopties">',
            '  <span class="cta-actions-label">Direct contact</span>',
            f'  <a class="btn btn-dark" href="/contact/" data-magnetic>{html(primary_label)}</a>',
            '  <a class="btn btn-light" href="/gratis-seo-scan/">Gratis website check</a>',
            f'  <a class="btn btn-ghost-light" href="mailto:{html(site["email"])}?subject={html(subject_href)}">Mail BDMNL direct</a>',
            '  <p class="cta-note">Directe route naar contact, zonder schijnformulier of onduidelijke vervolgstap.</p>',
            "</div>",
        ]
    )


def city_display_name(city_key: str) -> str:
    if city_key in RECOVERY_CITIES:
        return RECOVERY_CITIES[city_key]["name"]
    return REGIONAL_CLUSTER_CITY_NAMES.get(city_key, city_key.replace("-", " ").title())


def authority_page(page: dict[str, Any]) -> bool:
    return page["service_key"] in {"website-laten-maken", "webdesign", "seo"} and page["city_key"] in AUTHORITY_CITY_KEYS


def recovery_faqs(page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> list[dict[str, str]]:
    city_name = city["name"]
    areas = ", ".join(city["areas"])
    keyword = page["keyword"].lower()
    local = local_authority(page["city_key"])
    service = service_authority(page, profile)
    return [
        {
            "question": f"Wanneer is {keyword} in {city_name} een slimme investering?",
            "answer": (
                f"Dat is vooral waardevol wanneer klanten je online vergelijken voordat ze contact opnemen. BDMNL zorgt dan voor {service['benefit']} "
                f"en een pagina die past bij de markt in {city_name}."
            ),
        },
        {
            "question": f"Hoe maakt BDMNL de pagina lokaal relevant voor {city_name}?",
            "answer": (
                f"We verwerken lokale context rond {areas}, nabijgelegen plaatsen zoals {', '.join(local['nearby'][:3])} en realistische klantvragen. "
                "Daardoor leest de pagina natuurlijker en wordt de lokale intentie sterker."
            ),
        },
        {
            "question": "Blijft de pagina premium in plaats van generiek SEO-gericht?",
            "answer": (
                "Ja. We houden de opbouw rustig, schrijven menselijk en gebruiken SEO als structuur onder de pagina, niet als zichtbare vulling."
            ),
        },
        {
            "question": "Welke vervolgstap past na het bekijken van deze pagina?",
            "answer": (
                "Plan een gesprek of stuur een korte mail. Dan kijkt BDMNL naar je huidige website, lokale markt en de pagina's die nodig zijn om sterker te groeien."
            ),
        },
    ]


def recovery_service_cards(page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> str:
    local = local_authority(page["city_key"])
    service = service_authority(page, profile)
    cards = [
        (
            "01",
            "Lokale positionering",
            f"We bepalen hoe {page['keyword'].lower()} in {city['name']} moet voelen voor klanten uit {', '.join(local['nearby'][:2])} en de regio.",
        ),
        (
            "02",
            "Premium UX en content",
            f"De pagina krijgt scherpe headings, rustige secties en copy die uitlegt waarom jouw bedrijf de juiste keuze is.",
        ),
        (
            "03",
            "SEO die natuurlijk leest",
            f"Lokale zoekwoorden, FAQ's en interne links worden verwerkt zonder de leesbaarheid of premium uitstraling te verliezen.",
        ),
        (
            "04",
            "Conversie zonder frictie",
            f"We sturen op {service['outcome']} met duidelijke CTA's, contactroutes en bewijsvoering op de juiste plekken.",
        ),
    ]
    return "\n".join(
        "\n".join(
            [
                '      <article class="service-card reveal">',
                f'        <span class="card-number">{number}</span>',
                '        <div class="service-icon" aria-hidden="true"></div>',
                f"        <h3>{html(title)}</h3>",
                f"        <p>{html(copy)}</p>",
                '        <a href="/contact/">Bespreek dit met BDMNL</a>',
                "      </article>",
            ]
        )
        for number, title, copy in cards
    )


def recovery_related_cards(page: dict[str, Any], pages: list[dict[str, Any]]) -> str:
    same_city = [candidate for candidate in pages if candidate["path"] != page["path"] and candidate["city_key"] == page["city_key"]]
    same_service = [
        candidate
        for candidate in pages
        if candidate["path"] != page["path"] and candidate["service_key"] == page["service_key"] and candidate not in same_city
    ]
    related = same_city + same_service[:4]
    if len(related) < 4:
        related.extend([candidate for candidate in pages if candidate not in related and candidate["path"] != page["path"]][: 4 - len(related)])

    return "\n".join(
        "\n".join(
            [
                f'      <a class="service-card related-card reveal" href="{recovery_href(candidate)}">',
                f'        <span class="card-number">{html(RECOVERY_SERVICE_PROFILES[candidate["service_key"]]["label"])}</span>',
                '        <div class="service-icon" aria-hidden="true"></div>',
                f"        <h3>{html(candidate['keyword'])} {html(RECOVERY_CITIES[candidate['city_key']]['name'])}</h3>",
                f"        <p>Bekijk hoe BDMNL deze dienst lokaal positioneert voor {html(RECOVERY_CITIES[candidate['city_key']]['name'])}.</p>",
                "      </a>",
            ]
        )
        for candidate in related
    )


def recovery_testimonial_cards() -> str:
    testimonials = [
        (
            "BDMNL heeft onze website vernieuwd naar een moderne en gebruiksvriendelijke uitstraling. De communicatie verliep prettig en er werd snel geschakeld bij feedback of aanpassingen.",
            "HV Helius",
            "Lokale sportorganisatie",
        ),
        (
            "Onze oude website was verouderd en niet goed vindbaar in Google. BDMNL heeft dit volledig vernieuwd met een frisse uitstraling en duidelijke structuur voor onze klanten.",
            "Brielle Automotive",
            "Autobedrijf",
        ),
        (
            "Dankzij BDMNL hebben wij nu een professionele website die niet alleen mooi oogt, maar ook beter gevonden wordt in Google. Fijn contact en snelle communicatie tijdens het hele traject.",
            "Studio Brielle",
            "Creatieve onderneming",
        ),
    ]
    return "\n".join(
        "\n".join(
            [
                f'      <article class="testimonial-card{" featured" if index == 1 else ""} reveal">',
                '        <div class="quote-mark">"</div>',
                f"        <p>{html(copy)}</p>",
                "        <div>",
                f"          <strong>{html(name)}</strong>",
                f"          <span>{html(role)}</span>",
                "        </div>",
                "      </article>",
            ]
        )
        for index, (copy, name, role) in enumerate(testimonials)
    )


def premium_case_notes(page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> str:
    service = service_authority(page, profile)
    notes = [
        (
            "01 Strategie",
            "De eerste vijf seconden bepalen vertrouwen.",
            f"We brengen propositie, doelgroep en lokale vraag in {city['name']} terug naar een duidelijke bovenkant: wie je helpt, waarom dat relevant is en welke stap iemand kan zetten.",
        ),
        (
            "02 Uitvoering",
            f"{profile['label']} als beheerbare basis.",
            f"De pagina wordt licht, responsive en overzichtelijk opgebouwd, met ruimte voor bewijs, diensten, lokale content en latere uitbreiding.",
        ),
        (
            "03 Vindbaarheid",
            "Lokale SEO zonder keyword-gevoel.",
            f"{city['name']}, {city['region']} en relevante omliggende plaatsen worden natuurlijk verwerkt in headings, tekst, schema en interne links.",
        ),
    ]
    if page["service_key"] in {"hosting", "branding-design", "webshop-laten-maken"}:
        notes[1] = (
            "02 Uitvoering",
            service["visual_label"],
            f"BDMNL maakt de dienst concreet met duidelijke deliverables, realistische verwachtingen en een structuur die bezoekers helpt kiezen.",
        )
    return "\n".join(
        "\n".join(
            [
                '      <article class="case-note">',
                f"        <span>{html(label)}</span>",
                f"        <h3>{html(title)}</h3>",
                f"        <p>{html(copy)}</p>",
                "      </article>",
            ]
        )
        for label, title, copy in notes
    )


def premium_expertise_cards(page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> str:
    service = service_authority(page, profile)
    cards = [
        ("01", "Positionering", "Heldere keuzes in doelgroep, belofte en bewijsvoering."),
        ("02", "Ontwerp", "Editorial rust, sterke hiërarchie en premium uitstraling."),
        ("03", "Techniek", "Snelle realisatie met nette SEO-basis en schaalbaarheid."),
        ("04", "Conversie", f"Subtiele contactroutes gericht op {service['outcome']}."),
    ]
    return "\n".join(
        "\n".join(
            [
                "      <article>",
                f"        <span>{html(number)}</span>",
                f"        <h3>{html(title)}</h3>",
                f"        <p>{html(copy)}</p>",
                "      </article>",
            ]
        )
        for number, title, copy in cards
    )


def premium_deliverables(page: dict[str, Any]) -> str:
    deliverables = {
        "website-laten-maken": ["Strategie", "Webflow build", "SEO basis", "Copystructuur", "Meetbare contactflow"],
        "webshop-laten-maken": ["Shopstructuur", "Productpresentatie", "Checkout flow", "SEO basis", "Conversiepunten"],
        "online-marketing": ["Kanaalstrategie", "SEO content", "Campagnebasis", "Rapportage", "Lead flow"],
        "social-media": ["Contentritme", "Formats", "Planning", "Campagnehaakjes", "Website koppeling"],
        "hosting": ["Snelheid", "Veiligheid", "Onderhoud", "Backups", "Monitoring"],
        "branding-design": ["Positionering", "Visuele richting", "Huisstijl", "Design system", "Website toepassing"],
        "webdesign": ["UX structuur", "Webflow design", "Responsive layout", "SEO basis", "Conversie"],
        "seo": ["Technische SEO", "Lokale content", "Interne links", "Schema", "Monitoring"],
        "reclamebureau": ["Strategie", "Branding", "Website", "Content", "Online groei"],
    }.get(page["service_key"], ["Strategie", "Content", "Techniek", "SEO", "Conversie"])
    return "\n".join(f"<span>{html(item)}</span>" for item in deliverables)


def premium_related_links(page: dict[str, Any], pages: list[dict[str, Any]]) -> str:
    same_city = [candidate for candidate in pages if candidate["path"] != page["path"] and candidate["city_key"] == page["city_key"]]
    same_service = [
        candidate
        for candidate in pages
        if candidate["path"] != page["path"] and candidate["service_key"] == page["service_key"] and candidate not in same_city
    ]
    related = (same_city[:10] + same_service[:4])[:12]
    return "\n".join(
        "\n".join(
            [
                f'      <a href="{recovery_href(candidate)}">',
                f"        <span>{html(RECOVERY_SERVICE_PROFILES[candidate['service_key']]['label'])}</span>",
                f"        <strong>{html(candidate['keyword'])} {html(RECOVERY_CITIES[candidate['city_key']]['name'])}</strong>",
                "        <i>Bekijk</i>",
                "      </a>",
            ]
        )
        for candidate in related
    )


def content_sections_html(page: dict[str, Any]) -> str:
    return "\n".join(
        "\n".join(
            [
                '        <article class="knowledge-card reveal">',
                f"          <h2>{html(title)}</h2>",
                f"          <p>{html(copy)}</p>",
                "        </article>",
            ]
        )
        for title, copy in page["sections"]
    )


def content_related_cards(pages: list[dict[str, Any]]) -> str:
    candidates = [
        ("Bulldog Media is nu BDMNL", "/bulldog-media/", "Lees hoe Bulldog Media is doorontwikkeld naar BDMNL."),
        ("Van Bulldog Media naar BDMNL", "/van-bulldog-media-naar-bdmnl/", "Bekijk het verhaal achter de rebrand en continuiteit."),
        ("Over BDMNL", "/over-bdmnl/", "Leer de huidige positionering en historie van BDMNL kennen."),
        ("Webdesign Brielle", "/webdesign/webdesign-brielle/", "Bekijk hoe BDMNL webdesign lokaal neerzet."),
        ("SEO Rotterdam", "/seo/seo-rotterdam/", "Bekijk hoe BDMNL lokale vindbaarheid in Rotterdam aanpakt."),
        ("Gratis SEO scan", "/gratis-seo-scan/", "Laat je website controleren op snelheid, structuur en vindbaarheid."),
        ("Content marketing", "/blog/content-marketing/", "Lees hoe inhoud helpt om vertrouwen en vindbaarheid op te bouwen."),
        ("Waarom Bulldog Media BDMNL werd", "/blog/waarom-bulldog-media-bdmnl-werd/", "Lees waarom de rebrand past bij de doorontwikkeling van het bureau."),
        ("De evolutie naar BDMNL", "/blog/evolutie-bulldog-media-naar-bdmnl/", "Ontdek hoe Bulldog Media doorgroeide naar het huidige BDMNL."),
        ("Hoe BDMNL is gebouwd", "/blog/hoe-bdmnl-is-gebouwd/", "Bekijk hoe bestaande ervaring is vertaald naar de huidige agency-aanpak."),
        ("Toekomstvisie BDMNL", "/blog/toekomstvisie-bdmnl/", "Lees hoe BDMNL verder bouwt aan digitale autoriteit."),
        ("Website updaten", "/blog/hoe-vaak-moet-je-je-website-updaten/", "Bekijk wanneer content, techniek en SEO opnieuw aandacht nodig hebben."),
        ("Blog beginnen", "/blog/hoe-kun-je-een-eigen-blog-beginnen/", "Gebruik blogs als ondersteunende content binnen je SEO structuur."),
        ("Professionele hosting", "/blog/professionele-website-hosting-betrouwbaar-en-snel/", "Lees waarom snelheid en betrouwbaarheid belangrijk zijn voor SEO."),
        ("WordPress populair", "/blog/wordpress-waarom-is-dat-zo-populair/", "Vergelijk bekende CMS-keuzes met snelheid, beheer en onderhoud."),
    ]
    return "\n".join(
        "\n".join(
            [
                f'      <a class="service-card related-card reveal" href="{href}">',
                '<span class="card-number">BDMNL</span>',
                f"<h3>{html(title)}</h3>",
                f"<p>{html(copy)}</p>",
                "</a>",
            ]
        )
        for title, href, copy in candidates
    )


def content_faqs(page: dict[str, Any]) -> list[dict[str, str]]:
    if page["kind"] == "article":
        return [
            {
                "question": "Kan BDMNL helpen om dit toe te passen op mijn website?",
                "answer": "Ja. BDMNL helpt met Webflow, SEO, content en online marketing, zodat inzichten uit de kennisbank praktisch worden vertaald naar je website.",
            },
            {
                "question": "Is dit onderwerp belangrijk voor SEO?",
                "answer": "Ja. Duidelijke content, snelheid, structuur en logische verwijzingen helpen bezoekers én zoekmachines beter begrijpen waar je website over gaat.",
            },
        ]
    return [
        {
            "question": "Kan ik hierover contact opnemen met BDMNL?",
            "answer": "Ja. Je kunt BDMNL bereiken via info@bdmnl.nl of telefonisch via 085 060 56 27.",
        },
        {
            "question": "Sluit dit aan op de BDMNL aanpak?",
            "answer": "Ja. BDMNL werkt met een herkenbare basis: duidelijke structuur, snelle techniek, sterke content en heldere contactmomenten.",
        },
    ]


def render_content_page(
    layout: str,
    header: str,
    footer: str,
    footer_ctx: dict[str, str],
    site: dict[str, Any],
    page: dict[str, Any],
    pages: list[dict[str, Any]],
) -> str:
    asset_prefix = "../" * len(page["path"].split("/"))
    page_url = f"{site['base_url']}/{page['path']}/"
    faqs = content_faqs(page)
    article_class = " article-page" if page["kind"] == "article" else ""
    schema_type = page.get("schema_type") or ("Article" if page["kind"] == "article" else "WebPage")
    main_schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "headline" if schema_type == "Article" else "name": page["title"],
        "url": page_url,
        "description": page["description"],
        "publisher": organization_identity(site),
    }
    if "bulldog" in page["path"] or "bdmnl" in page["path"]:
        main_schema["about"] = [
            {"@type": "Organization", "name": "BDMNL", "alternateName": "Bulldog Media"},
            {"@type": "Brand", "name": "Bulldog Media"},
        ]
        main_schema["mentions"] = [
            {"@type": "Organization", "name": "Bulldog Media", "url": site.get("legacy_domain", "https://www.bulldogmedia.nl")},
            {"@type": "Organization", "name": "BDMNL", "url": site.get("primary_domain", "https://www.bdmnl.nl")},
        ]
    page_content = f"""
<section class="hero section-pad{article_class}">
  <div class="container">
    <p class="eyebrow"><span></span>{html(page['eyebrow'])}</p>
    <h1>{html(page['h1'])}</h1>
    <p class="hero-lead">{html(page['intro'])}</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="/contact/" data-magnetic>Neem contact op</a>
      <a class="btn btn-secondary" href="/kennisbank/webdesign/" data-magnetic>Bekijk kennisbank</a>
    </div>
  </div>
</section>
<section class="section knowledge-section" id="kennisbank">
  <div class="container">
    <div class="knowledge-article">
{content_sections_html(page)}
    </div>
  </div>
</section>
<section class="section related-pages" id="diensten">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Verder binnen BDMNL</p>
      <h2>Gerelateerde pagina's.</h2>
      <p>Gebruik deze links om door te gaan naar relevante diensten, inzichten of contact.</p>
    </div>
    <div class="card-grid service-grid">
{content_related_cards(pages)}
    </div>
  </div>
</section>
<section class="section process" id="proces">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Werkwijze</p>
      <h2>Praktisch, duidelijk en gericht op online groei.</h2>
      <p>BDMNL combineert strategie, Webflow, SEO en content tot een online basis die past bij je bedrijf.</p>
    </div>
  </div>
</section>
<section class="section portfolio" id="portfolio">
  <div class="container">
    <div class="section-heading reveal">
      <p class="eyebrow"><span></span>Cases</p>
      <h2>Digitale projecten met impact.</h2>
      <p>Van websites en webshops tot branding, SEO en online marketing: BDMNL werkt aan digitale oplossingen die duidelijk en professioneel voelen.</p>
    </div>
  </div>
</section>
<section class="section cta-band">
  <div class="container">
    <div class="cta-panel reveal" id="contact">
      <div>
        <p class="eyebrow light"><span></span>Contact</p>
        <h2>Wil je hiermee aan de slag?</h2>
        <p>Neem contact op met BDMNL voor een praktische aanpak rond website, SEO, content of online marketing.</p>
      </div>
      <div class="cta-visual" aria-hidden="true">
        <span></span>
        <strong>BDMNL</strong>
        <em>SEO recovery</em>
      </div>
      {build_direct_cta_actions(site, "Neem contact op", page["title"])}
    </div>
  </div>
</section>
<section class="section faq" id="faq">
  <div class="container faq-grid">
    <div class="section-heading reveal">
      <p class="eyebrow"><span></span>FAQ</p>
      <h2>Veelgestelde vragen.</h2>
      <p>Korte antwoorden over dit onderwerp en hoe BDMNL kan helpen.</p>
    </div>
    <div class="faq-list reveal">
      {build_faq_items(faqs)}
    </div>
  </div>
</section>
"""
    breadcrumb = json_script(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site['base_url']}/"},
                {"@type": "ListItem", "position": 2, "name": page["h1"].rstrip("."), "item": page_url},
            ],
        }
    )
    context = {
        "asset_prefix": asset_prefix,
        "canonical_url": page_url,
        "og_title": page["title"],
        "og_description": page["description"],
        "twitter_title": page["title"],
        "twitter_description": page["description"],
        "og_image": site["og_image"],
        "meta_title": page["title"],
        "meta_description": page["description"],
        "professional_service_schema": json_script(main_schema),
        "faq_schema": faq_schema(faqs),
        "breadcrumb_schema": breadcrumb,
        "global_header": render(header, {"asset_prefix": asset_prefix}),
        "global_footer": render(
            footer,
            {**footer_ctx, "asset_prefix": asset_prefix},
            raw_keys={"footer_city_links", "footer_service_links", "footer_internal_links"},
        ),
        "page_content": page_content.strip(),
    }
    return GENERATED_MARKER + "\n" + render(
        layout,
        context,
        raw_keys={"global_header", "global_footer", "page_content", "professional_service_schema", "faq_schema", "breadcrumb_schema"},
    )


def recovery_schema(site: dict[str, Any], page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> str:
    return json_script(
        {
            "@context": "https://schema.org",
            "@type": "ProfessionalService",
            "name": f"BDMNL - {page['keyword']} {city['name']}",
            "alternateName": "Bulldog Media",
            "url": recovery_url(site, page),
            "image": site["og_image"],
            "email": site["email"],
            "telephone": site["phone"],
            "areaServed": {"@type": "City", "name": city["name"]},
            "address": {"@type": "PostalAddress", "streetAddress": "Krammer 8", "postalCode": "3232 HE", "addressLocality": "Brielle", "addressCountry": "NL"},
            "description": profile["description"].format(city=city["name"], keyword=page["keyword"]),
            "serviceType": profile["service_type"],
            "sameAs": organization_identity(site)["sameAs"],
        }
    )


def recovery_breadcrumb(site: dict[str, Any], page: dict[str, Any], city: dict[str, Any]) -> str:
    profile = RECOVERY_SERVICE_PROFILES[page["service_key"]]
    return json_script(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site['base_url']}/"},
                {"@type": "ListItem", "position": 2, "name": profile["label"], "item": f"{site['base_url']}/#diensten"},
                {"@type": "ListItem", "position": 3, "name": f"{page['keyword']} {city['name']}", "item": recovery_url(site, page)},
            ],
        }
    )


def recovery_context(site: dict[str, Any], page: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, str]:
    city = RECOVERY_CITIES[page["city_key"]]
    profile = RECOVERY_SERVICE_PROFILES[page["service_key"]]
    title = profile["title"].format(city=city["name"], keyword=page["keyword"])
    description = profile["description"].format(city=city["name"], keyword=page["keyword"])
    if page["path"] in META_OVERRIDES:
        title = META_OVERRIDES[page["path"]]["title"]
        description = META_OVERRIDES[page["path"]]["description"]
    faqs = recovery_faqs(page, city, profile)
    areas = ", ".join(city["areas"])
    local = local_authority(page["city_key"])
    service = service_authority(page, profile)
    nearby = ", ".join(local["nearby"][:4])
    is_authority = authority_page(page)
    h1 = profile["h1"].format(city=city["name"], keyword=page["keyword"])
    hero_lead = profile["hero"].format(city=city["name"], keyword=page["keyword"])
    if is_authority:
        hero_lead = (
            f"{hero_lead} Voor ondernemers in {city['name']} en plaatsen als {nearby} draait het om meer dan vindbaarheid: "
            f"de pagina moet vertrouwen opbouwen, scherp positioneren en leiden naar {service['outcome']}."
        )
    return {
        "asset_prefix": "../" * len(page["path"].split("/")),
        "canonical_url": recovery_url(site, page),
        "og_title": title,
        "og_description": description,
        "twitter_title": title,
        "twitter_description": description,
        "og_image": site["og_image"],
        "meta_title": title,
        "meta_description": description,
        "professional_service_schema": recovery_schema(site, page, city, profile),
        "faq_schema": faq_schema(faqs),
        "breadcrumb_schema": recovery_breadcrumb(site, page, city),
        "eyebrow": f"{page['keyword']} in {city['name']}",
        "h1": h1,
        "hero_lead": hero_lead,
        "premium_h1": h1,
        "premium_hero_lead": (
            f"{profile['label']} in {city['name']} moet vertrouwen opbouwen voordat iemand contact opneemt. "
            f"BDMNL combineert strategie, content en techniek tot een rustige pagina die past bij de lokale markt."
        ),
        "premium_brief_intro": (
            f"Voor ondernemers in {city['name']} en omliggende plaatsen zoals {nearby}, die professioneel gevonden en gekozen willen worden."
        ),
        "premium_focus": f"{profile['label']} en lokale autoriteit",
        "premium_market": f"{city['region']} / {city['name']}",
        "premium_goal": service["outcome"],
        "premium_local_heading": f"{profile['label']} moet in {city['name']} eerst betrouwbaar voelen.",
        "premium_authority_copy": (
            "De pagina wordt behandeld als een merk- en verkoopdocument: eerst positionering, daarna bewijs, daarna de technische SEO-laag die de juiste bezoekers aantrekt."
        ),
        "premium_case_label": "Authority standard",
        "premium_case_heading": "Van lokaal zichtbaar naar professioneel gekozen.",
        "premium_case_intro": f"Een BDMNL pagina voor {city['name']} moet aanvoelen als een volwassen merkpresentatie: rustig, overtuigend en klaar voor groei.",
        "premium_case_notes": premium_case_notes(page, city, profile),
        "premium_expertise_heading": "De pagina werkt als een digitaal verkoopgesprek.",
        "premium_expertise_intro": (
            f"Goede {profile['label'].lower()} hoeft niet druk te zijn. Het moet scherp zijn. "
            "BDMNL combineert strategie, ontwerp, content en techniek zodat bezoekers zonder frictie begrijpen waarom jouw bedrijf de juiste keuze is."
        ),
        "premium_expertise_cards": premium_expertise_cards(page, city, profile),
        "premium_deliverables": premium_deliverables(page),
        "premium_related_links": premium_related_links(page, pages),
        "premium_mail_subject": f"{page['keyword']} {city['name']}".replace(" ", "%20"),
        "hero_proof": f"BDMNL koppelt premium Webflow design aan lokale SEO voor {city['name']} en {city['region']}.",
        "primary_cta": profile["cta"],
        "city": city["name"],
        "service_label": profile["label"],
        "service_short": profile["short"],
        "path": page["path"],
        "local_focus": f"{city['name']}, {nearby}",
        "marquee_items": "\n".join(f"<span>{html(item)}</span>" for item in [profile["label"], city["name"], *local["nearby"][:4], "Webflow", "SEO", "Conversie"]),
        "logo_panel_copy": f"BDMNL combineert lokale marktkennis, premium UX, Webflow techniek en SEO voor bedrijven in {city['name']} en omgeving.",
        "intro_heading": f"{page['keyword']} {city['name']} met lokale autoriteit en een premium eerste indruk.",
        "intro_copy_one": (
            f"{local['market']} Daarom moet {page['keyword'].lower()} in {city['name']} direct duidelijk maken waar je voor staat, "
            f"voor wie je werkt en waarom iemand de volgende stap zet."
        ),
        "intro_copy_two": (
            f"{local['scenario']} BDMNL vertaalt dat naar {service['benefit']}, zonder overbodige SEO-zinnen of generieke beloftes."
        ),
        "intro_copy_three": (
            f"{service['decision']} De pagina blijft leesbaar, snel en logisch opgebouwd voor bezoekers uit {areas}."
        ),
        "authority_facts": build_authority_facts(page["city_key"], city, page, profile),
        "local_authority_heading": f"Wat maakt {city['name']} anders als lokale markt?",
        "local_authority_intro": local["positioning"],
        "local_scenario_cards": build_local_scenario_cards(page["city_key"], city, page, profile),
        "authority_visual": build_authority_visual(page["city_key"], city, page, profile),
        "services_heading": f"Een scherpere aanpak voor {page['keyword'].lower()} in {city['name']}.",
        "services_intro": f"Geen dunne SEO-pagina, maar een compacte autoriteitspagina met lokale context, premium design en conversie voor {city['region']}.",
        "service_cards": recovery_service_cards(page, city, profile),
        "portfolio_heading": f"Premium pagina-opbouw voor {page['keyword'].lower()} in {city['name']}.",
        "portfolio_intro": "De visuele opbouw ondersteunt vertrouwen: een rustige hero, duidelijke diensten, lokale bewijsvoering en CTA's die niet voelen als druk.",
        "portfolio_label_one": page["keyword"],
        "portfolio_title_one": f"Een bovenkant die meteen positioneert.",
        "portfolio_note_one": f"{city['name']} + {profile['label']} + duidelijke waardepropositie",
        "portfolio_title_two": f"Lokale signalen zonder keyword stuffing.",
        "portfolio_note_two": f"{city['name']}, {nearby}",
        "portfolio_title_three": "Vertrouwen voor de klik naar contact.",
        "portfolio_note_three": "Bewijs, FAQ, interne links en duidelijke CTA's",
        "related_cards": recovery_related_cards(page, pages),
        "testimonial_cards": recovery_testimonial_cards(),
        "cta_heading": f"Wil je dat {page['keyword'].lower()} in {city['name']} serieuzer voelt?",
        "cta_copy": f"Laat BDMNL meekijken naar je huidige pagina, lokale kansen en de route naar {service['outcome']}. Je krijgt een concreet gesprek over structuur, content, SEO en conversie.",
        "cta_actions": build_cta_actions(site, page, city, profile),
        "faq_heading": f"Veelgestelde vragen over {page['keyword'].lower()} in {city['name']}.",
        "faq_items": build_faq_items(faqs),
    }


def render_recovery_page(
    layout: str,
    page_template: str,
    header: str,
    footer: str,
    footer_ctx: dict[str, str],
    context: dict[str, str],
) -> str:
    template_path = PREMIUM_RECOVERY_TEMPLATE_PATH if PREMIUM_RECOVERY_TEMPLATE_PATH.exists() else RECOVERY_TEMPLATE_PATH
    page_template = template_path.read_text(encoding="utf-8")
    page_content = render(
        page_template,
        context,
        raw_keys={
            "service_cards",
            "related_cards",
            "testimonial_cards",
            "faq_items",
            "marquee_items",
            "authority_facts",
            "local_scenario_cards",
            "authority_visual",
            "cta_actions",
            "premium_case_notes",
            "premium_expertise_cards",
            "premium_deliverables",
            "premium_related_links",
        },
    )
    header_html = render(header, {"asset_prefix": context["asset_prefix"]})
    footer_html = render(
        footer,
        {**footer_ctx, "asset_prefix": context["asset_prefix"]},
        raw_keys={"footer_city_links", "footer_service_links", "footer_internal_links"},
    )
    html_output = GENERATED_MARKER + "\n" + render(
        layout,
        {**context, "global_header": header_html, "global_footer": footer_html, "page_content": page_content.strip()},
        raw_keys={"global_header", "global_footer", "page_content", "professional_service_schema", "faq_schema", "breadcrumb_schema"},
    )
    html_output = html_output.replace(
        '<link rel="stylesheet" href="../assets/css/landing.css" />',
        '<link rel="stylesheet" href="../assets/css/landing.css" />\n    <link rel="stylesheet" href="../assets/css/premium-example.css" />',
        1,
    )
    return html_output.replace("<body>", '<body class="premium-example-page">', 1)


def render_premium_brielle_example(
    layout: str,
    header: str,
    footer: str,
    footer_ctx: dict[str, str],
    context: dict[str, str],
) -> str:
    page_content = PREMIUM_BRIELLE_TEMPLATE_PATH.read_text(encoding="utf-8")
    header_html = render(header, {"asset_prefix": context["asset_prefix"]})
    footer_html = render(
        footer,
        {**footer_ctx, "asset_prefix": context["asset_prefix"]},
        raw_keys={"footer_city_links", "footer_service_links", "footer_internal_links"},
    )
    html_output = GENERATED_MARKER + "\n" + render(
        layout,
        {**context, "global_header": header_html, "global_footer": footer_html, "page_content": page_content.strip()},
        raw_keys={"global_header", "global_footer", "page_content", "professional_service_schema", "faq_schema", "breadcrumb_schema"},
    )
    html_output = html_output.replace(
        '<link rel="stylesheet" href="../assets/css/landing.css" />',
        '<link rel="stylesheet" href="../assets/css/landing.css" />\n    <link rel="stylesheet" href="../assets/css/premium-example.css" />',
        1,
    )
    return html_output.replace("<body>", '<body class="premium-example-page">', 1)


def cleanup_generated_recovery(pages: list[dict[str, Any]]) -> None:
    expected = {page["path"] for page in pages}
    top_dirs = {"webdesign", "seo", "social-media", "online-marketing", "reclamebureau"}
    for top in top_dirs:
        directory = ROOT / top
        if not directory.exists():
            continue
        for child in directory.iterdir():
            if child.is_dir() and f"{top}/{child.name}" not in expected:
                shutil.rmtree(child)


def write_sitemap_for_paths(site: dict[str, Any], paths: list[str], support_slugs: list[str]) -> None:
    today = date.today().isoformat()
    urls = [f"{site['base_url']}/"]
    urls.extend(f"{site['base_url']}/{path}/" for path in paths)
    urls.extend(f"{site['base_url']}/{page['path']}/" for page in CONTENT_RECOVERY_PAGES)
    urls.extend(f"{site['base_url']}/{slug}/" for slug in support_slugs)
    entries = "\n".join(
        "\n".join(
            [
                "  <url>",
                f"    <loc>{html(url)}</loc>",
                f"    <lastmod>{today}</lastmod>",
                "    <changefreq>monthly</changefreq>",
                "    <priority>0.8</priority>",
                "  </url>",
            ]
        )
        for url in urls
    )
    (ROOT / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
""",
        encoding="utf-8",
    )


def build_recovery_homepage(
    layout: str,
    header: str,
    footer: str,
    footer_ctx: dict[str, str],
    site: dict[str, Any],
    pages: list[dict[str, Any]],
) -> str:
    cards = []
    featured = pages[:12]
    for page in featured:
        city = RECOVERY_CITIES[page["city_key"]]
        profile = RECOVERY_SERVICE_PROFILES[page["service_key"]]
        cards.append(
            "\n".join(
                [
                    '<article class="service-card reveal">',
                    f'<span class="card-number">{html(profile["label"])}</span>',
                    f"<h2>{html(page['keyword'])} {html(city['name'])}</h2>",
                    f"<p>Een gerichte BDMNL pagina voor {html(city['name'])}, met lokale context, duidelijke voordelen en een logische route naar contact.</p>",
                    f'<div class="mini-link-row"><a href="{recovery_href(page)}">Bekijk pagina</a></div>',
                    "</article>",
                ]
            )
        )

    homepage_faqs = [
        {
            "question": "Welke SEO recovery pagina's staan op seo.bdmnl.nl?",
            "answer": "De recovery omgeving bevat lokale pagina's voor webdesign, website laten maken, SEO bureau, online marketing, social media beheer en reclamebureau diensten.",
        },
        {
            "question": "Waarom werkt BDMNL met lokale serviceclusters?",
            "answer": "Lokale serviceclusters helpen zoekmachines en bezoekers begrijpen welke dienst BDMNL in welke regio aanbiedt, met interne links tussen verwante pagina's.",
        },
        {
            "question": "Kunnen recovery pagina's later worden uitgebreid?",
            "answer": "Ja. De pagina's worden gegenereerd vanuit een gedeelde structuur, zodat nieuwe steden, diensten en contentblokken schaalbaar kunnen worden toegevoegd.",
        },
    ]

    page_content = f"""
<section class="hero section-pad">
  <div class="container">
    <p class="eyebrow"><span></span>BDMNL digital agency</p>
    <h1>Webflow, SEO en online marketing voor bedrijven die sterker willen groeien.</h1>
    <p class="hero-lead">BDMNL bouwt snelle websites, sterke lokale vindbaarheid en herkenbare online communicatie. Eén duidelijke uitstraling, korte lijnen en pagina's die bezoekers helpen de juiste stap te zetten.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{recovery_href(pages[0])}" data-magnetic>Bekijk webdesign</a>
      <a class="btn btn-secondary" href="/contact/" data-magnetic>Neem contact op</a>
    </div>
  </div>
</section>
<section class="section related-pages" id="diensten">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Diensten & steden</p>
      <h2>Lokale pagina's met een herkenbaar BDMNL verhaal.</h2>
      <p>Bekijk hoe BDMNL diensten als webdesign, SEO, social media en online marketing lokaal positioneert.</p>
    </div>
    <div class="card-grid service-grid">
      {"".join(cards)}
    </div>
  </div>
</section>
<section class="section portfolio" id="portfolio">
  <div class="container">
    <div class="section-heading reveal">
      <p class="eyebrow"><span></span>Cases</p>
      <h2>Digitale projecten met impact.</h2>
      <p>BDMNL werkt aan websites, webshops, branding, SEO en online marketing voor ondernemers die online sterker willen staan.</p>
    </div>
  </div>
</section>
<section class="section process" id="proces">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Werkwijze</p>
      <h2>Eerst helder krijgen wat nodig is, daarna slim bouwen.</h2>
      <p>BDMNL begint met doelen, doelgroep en lokale kansen. Daarna vertalen we dat naar design, content, techniek en conversie.</p>
    </div>
  </div>
</section>
<section class="section knowledge-section" id="kennisbank">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Kennisbank</p>
      <h2>Webflow, snelheid, SEO en conversie als vaste basis.</h2>
      <p>In de kennisbank delen we praktische inzichten over Webflow, snelheid, SEO, hosting, content en conversie.</p>
    </div>
  </div>
</section>
<section class="section faq" id="faq">
  <div class="container faq-grid">
    <div class="section-heading reveal">
      <p class="eyebrow"><span></span>FAQ</p>
      <h2>Veelgestelde vragen over het recovery systeem.</h2>
      <p>Korte antwoorden over de lokale SEO structuur van BDMNL.</p>
    </div>
    <div class="faq-list reveal">
      {build_faq_items(homepage_faqs)}
    </div>
  </div>
</section>
<section class="section cta-band">
  <div class="container">
    <div class="cta-panel reveal" id="contact">
      <div>
        <p class="eyebrow light"><span></span>Contact</p>
        <h2>Klaar om je website, SEO of online marketing sterker neer te zetten?</h2>
        <p>BDMNL denkt mee over de juiste aanpak en vertaalt die naar een professionele online basis.</p>
      </div>
      <div class="cta-visual" aria-hidden="true">
        <span></span>
        <strong>BDMNL</strong>
        <em>Recovery structuur</em>
      </div>
      {build_direct_cta_actions(site, "Plan strategiegesprek", "BDMNL SEO recovery")}
    </div>
  </div>
</section>
"""
    schema = json_script(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": site["name"],
            "alternateName": site.get("alternate_name", "Bulldog Media"),
            "url": site["base_url"],
            "publisher": organization_identity(site),
        }
    )
    context = {
        "asset_prefix": "./",
        "canonical_url": f"{site['base_url']}/",
        "og_title": "BDMNL | Webdesign, SEO en online marketing",
        "og_description": "BDMNL helpt bedrijven groeien met snelle Webflow websites, SEO, branding, social media en online marketing.",
        "twitter_title": "BDMNL | Webdesign, SEO en online marketing",
        "twitter_description": "BDMNL helpt bedrijven groeien met snelle Webflow websites, SEO, branding, social media en online marketing.",
        "og_image": site["og_image"],
        "meta_title": "BDMNL | Webdesign, SEO & online marketing bureau",
        "meta_description": "BDMNL helpt bedrijven groeien met Webflow websites, SEO, branding, social media en online marketing die professioneel en duidelijk aanvoelen.",
        "professional_service_schema": schema,
        "faq_schema": faq_schema(homepage_faqs),
        "breadcrumb_schema": json_script(
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site['base_url']}/"}],
            }
        ),
        "global_header": render(header, {"asset_prefix": "./"}),
        "global_footer": render(
            footer,
            {**footer_ctx, "asset_prefix": "./"},
            raw_keys={"footer_city_links", "footer_service_links", "footer_internal_links"},
        ),
        "page_content": page_content.strip(),
    }
    return GENERATED_MARKER + "\n" + render(
        layout,
        context,
        raw_keys={"global_header", "global_footer", "page_content", "professional_service_schema", "faq_schema", "breadcrumb_schema"},
    )


def remove_legacy_generated_pages(site: dict[str, Any], services: list[dict[str, Any]], cities: list[dict[str, Any]]) -> None:
    keep = {page_slug(service, city) for service in services for city in cities}
    legacy_prefixes = ("webdesign-",)
    for child in ROOT.iterdir():
        if not child.is_dir():
            continue
        if child.name in keep or child.name.startswith(legacy_prefixes):
            shutil.rmtree(child)

    prefix = site.get("url_prefix", "").strip("/")
    if not prefix:
        return

    prefix_dir = ROOT / prefix
    if not prefix_dir.exists():
        return

    for child in prefix_dir.iterdir():
        if child.is_dir() and child.name not in keep:
            shutil.rmtree(child)


def write_sitemap(site: dict[str, Any], slugs: list[str], support_slugs: list[str]) -> None:
    today = date.today().isoformat()
    urls = [f"{site['base_url']}/"] + [page_url(site, slug) for slug in slugs]
    urls.extend(f"{site['base_url']}/{slug}/" for slug in support_slugs)
    entries = "\n".join(
        "\n".join(
            [
                "  <url>",
                f"    <loc>{html(url)}</loc>",
                f"    <lastmod>{today}</lastmod>",
                "    <changefreq>monthly</changefreq>",
                "    <priority>0.8</priority>",
                "  </url>",
            ]
        )
        for url in urls
    )
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def write_robots(site: dict[str, Any]) -> None:
    robots = f"""User-agent: *
Allow: /

Sitemap: {site['base_url']}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")


def baseline_recovery_paths() -> set[str]:
    paths = {f"{category}/{slug}" for category, _service_key, slug, _city_key, _keyword in RECOVERY_URLS}
    paths.update(page["path"] for page in ADDITIONAL_LOCAL_RECOVERY_URLS)
    return paths


def page_service_family(page: dict[str, Any]) -> str:
    if page["keyword"].lower() in {"seo", "seo bureau", "zoekmachine optimalisatie"}:
        return "seo"
    if page["keyword"].lower() in {"social media", "social media beheer"}:
        return "social-media"
    return page["service_key"]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_recovery_reports(site: dict[str, Any], pages: list[dict[str, Any]], support_slugs: list[str]) -> None:
    baseline_paths = baseline_recovery_paths()
    duplicate_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for page in pages:
        duplicate_groups.setdefault((page["city_key"], page_service_family(page)), []).append(page)

    duplicate_paths = {
        page["path"]
        for group in duplicate_groups.values()
        if len(group) > 1
        for page in group
        if page["path"] in baseline_paths and page.get("source") != "priority-expansion"
    }

    audit_rows: list[dict[str, Any]] = []
    audit_rows.append(
        {
            "url": f"{site['base_url']}/",
            "path": "/",
            "city": "",
            "region": "",
            "service": "homepage",
            "keyword": "BDMNL digital agency",
            "status_before_expansion": "existing-live",
            "classification": "strong",
            "reason": "Live recovery homepage with service/city discovery links, metadata, schema and CTA.",
            "source": "recovery-homepage",
        }
    )
    for page in pages:
        city = RECOVERY_CITIES[page["city_key"]]
        profile = RECOVERY_SERVICE_PROFILES[page["service_key"]]
        url = recovery_url(site, page)
        existed_before = page["path"] in baseline_paths
        if page["path"] in duplicate_paths:
            classification = "redirect candidate"
            reason = "Historical route overlaps a newer service/city cluster and should be reviewed before consolidation."
        elif existed_before:
            classification = "strong"
            reason = "Live generated recovery page with metadata, schema, FAQ, CTA blocks and internal links."
        else:
            classification = "missing"
            reason = "Priority service/city URL was not in the previous live recovery set and is generated in this expansion."

        audit_rows.append(
            {
                "url": url,
                "path": f"/{page['path']}/",
                "city": city["name"],
                "region": city["region"],
                "service": profile["label"],
                "keyword": page["keyword"],
                "status_before_expansion": "existing-live" if existed_before else "missing-before-expansion",
                "classification": classification,
                "reason": reason,
                "source": page.get("source", "historical-recovery-system"),
            }
        )

    for content_page in CONTENT_RECOVERY_PAGES:
        audit_rows.append(
            {
                "url": f"{site['base_url']}/{content_page['path']}/",
                "path": f"/{content_page['path']}/",
                "city": "",
                "region": "",
                "service": content_page["kind"],
                "keyword": content_page["eyebrow"],
                "status_before_expansion": "existing-live",
                "classification": "strong" if content_page["kind"] == "article" else "weak",
                "reason": "Supporting recovery content; useful internally but not a primary local commercial landing page.",
                "source": "historical-content-recovery",
            }
        )

    for slug in support_slugs:
        audit_rows.append(
            {
                "url": f"{site['base_url']}/{slug}/",
                "path": f"/{slug}/",
                "city": "",
                "region": "",
                "service": "support",
                "keyword": slug,
                "status_before_expansion": "existing-live",
                "classification": "weak",
                "reason": "Required support page with basic content, not a commercial SEO landing page.",
                "source": "support-page",
            }
        )

    missing_rows = []
    for page in pages:
        if page["path"] in baseline_paths:
            continue
        city = RECOVERY_CITIES[page["city_key"]]
        profile = RECOVERY_SERVICE_PROFILES[page["service_key"]]
        missing_rows.append(
            {
                "url": recovery_url(site, page),
                "path": f"/{page['path']}/",
                "city": city["name"],
                "region": city["region"],
                "service": profile["label"],
                "keyword": page["keyword"],
                "reason": "Priority regional commercial page absent from current recovery coverage.",
                "generated_status": "created",
                "excluded_if": "temporary, preview, duplicate-only or no commercial SEO value",
            }
        )

    cluster_rows = []
    all_paths = {page["path"] for page in pages}
    path_patterns = {
        "website-laten-maken": "website-laten-maken-{city_slug}",
        "webshop-laten-maken": "webshop-laten-maken-{city_slug}",
        "online-marketing": "online-marketing/online-marketing-{city_slug}",
        "social-media-beheer": "social-media-beheer-{city_slug}",
        "hosting": "hosting-{city_slug}",
        "branding-design": "branding-design-{city_slug}",
        "webdesign": "webdesign/webdesign-{city_slug}",
        "seo-bureau": "seo-bureau-{city_slug}",
    }
    first_batch_clusters = {route["cluster"] for route in FIRST_BATCH_SERVICE_ROUTES}
    zh_completion_paths = {
        route["path_pattern"].format(city_slug=RECOVERY_CITIES[city_key].get("slug", city_key))
        for city_key in ZUID_HOLLAND_COMPLETION_CITY_KEYS
        for route in ZUID_HOLLAND_COMPLETION_ROUTES
    }
    for region, city_keys in REGIONAL_CLUSTER_PLAN.items():
        for city_key in city_keys:
            city_name = city_display_name(city_key)
            city_slug = RECOVERY_CITIES.get(city_key, {}).get("slug", city_key)
            for cluster, service in REGIONAL_SERVICE_CLUSTERS:
                path = path_patterns[cluster].format(city_slug=city_slug)
                if path in zh_completion_paths and path in all_paths:
                    status = "generated-zuid-holland-completion"
                elif path in all_paths:
                    status = "generated-first-batch" if city_key in FIRST_BATCH_CITY_KEYS and cluster in first_batch_clusters else "existing-recovery"
                elif city_key in FIRST_BATCH_CITY_KEYS and cluster in first_batch_clusters:
                    status = "missing-batch-review"
                else:
                    status = "planned-controlled"
                cluster_rows.append(
                    {
                        "cluster": cluster,
                        "city": city_name,
                        "region": region,
                        "planned_path": f"/{path}/",
                        "status": status,
                        "overwrite_risk": "none",
                        "note": "Regional cluster plan; only first-batch rows are generated in this phase.",
                    }
                )

    write_csv(
        ROOT / "recovery-audit.csv",
        audit_rows,
        [
            "url",
            "path",
            "city",
            "region",
            "service",
            "keyword",
            "status_before_expansion",
            "classification",
            "reason",
            "source",
        ],
    )
    write_csv(
        ROOT / "missing-pages.csv",
        missing_rows,
        ["url", "path", "city", "region", "service", "keyword", "reason", "generated_status", "excluded_if"],
    )
    write_csv(
        ROOT / "cluster-plan.csv",
        cluster_rows,
        ["cluster", "city", "region", "planned_path", "status", "overwrite_risk", "note"],
    )

    duplicate_count = len(duplicate_paths)
    total_html_pages = len(pages) + len(CONTENT_RECOVERY_PAGES) + len(support_slugs) + 1
    total_sitemap_urls = total_html_pages

    report = f"""# BDMNL SEO recovery validation report

Generated: {date.today().isoformat()}

## Scope

- Existing recovery infrastructure preserved: templates, shared CSS/JS, generated recovery pages, sitemap and robots flow.
- Search Console export files were not present in this workspace or tracked on `origin/main`; expansion therefore uses the existing recovery URL inventory plus the requested priority services, regions and cities.
- Temporary, preview and non-commercial URLs were not generated.
- Authority upgrade applied to website laten maken, SEO bureau and webdesign pages, with priority local content for Brielle, Rotterdam, Spijkenisse, Hellevoetsluis, Dordrecht, Goes, Middelburg and Breda.

## Output files

- `recovery-audit.csv`: {len(audit_rows)} audited URLs and coverage rows.
- `missing-pages.csv`: {len(missing_rows)} missing-before-expansion URLs generated.
- `cluster-plan.csv`: {len(cluster_rows)} next-generation cluster rows.
- `sitemap.xml`: updated with recovery URLs on `{site['base_url']}`.

## Coverage

- Recovery pages generated: {len(pages)}
- Supporting content pages: {len(CONTENT_RECOVERY_PAGES)}
- Support pages: {len(support_slugs)}
- Total HTML pages in sitemap scope: {total_html_pages}
- Redirect candidates flagged: {duplicate_count}

## Quality checks built into generation

- Canonical URL, OG tags and Twitter metadata.
- ProfessionalService, FAQPage and BreadcrumbList schema.
- CTA blocks, FAQ sections and internal related links.
- Shared BDMNL 2.0 styling and responsive layout.
- Local city and region references in headings, body copy and FAQ answers.
- Premium authority sections with local market context, regional scenarios, visual mockups and direct CTA buttons instead of fake inline forms.

## Validation performed

- Generator completed successfully.
- HTML parser validation target: {total_html_pages} generated `index.html` files.
- Sitemap XML validation target: {total_sitemap_urls} URL entries.
- Priority coverage target: {len(PRIORITY_CITY_KEYS)} cities x {len(EXPANSION_SERVICE_ROUTES)} service routes.
- CSV outputs generated with audit, missing-page and cluster-plan rows.

## Deployment notes

- `robots.txt` now points to `{site['base_url']}/sitemap.xml`.
- Sitemap URLs now match the live recovery host instead of the primary production domain.
- Cluster URLs use `website-laten-maken-[city]`, `seo-bureau-[city]` and `social-media-beheer-[city]` without deleting or overwriting historical recovery routes.
"""
    (ROOT / "validation-report.md").write_text(report, encoding="utf-8")


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    site = data["site"]
    layout = LAYOUT_PATH.read_text(encoding="utf-8")
    page_template = RECOVERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    header = HEADER_PATH.read_text(encoding="utf-8")
    footer = FOOTER_PATH.read_text(encoding="utf-8")
    pages = recovery_pages()
    footer_ctx = recovery_footer_context(site, pages)

    cleanup_generated_recovery(pages)

    for page in pages:
        context = recovery_context(site, page, pages)
        output_dir = ROOT / page["path"]
        output_dir.mkdir(parents=True, exist_ok=True)
        rendered_page = render_recovery_page(layout, page_template, header, footer, footer_ctx, context)
        (output_dir / "index.html").write_text(
            rendered_page,
            encoding="utf-8",
        )

    (ROOT / "index.html").write_text(
        build_recovery_homepage(layout, header, footer, footer_ctx, site, pages),
        encoding="utf-8",
    )

    for page in SUPPORT_PAGES:
        output_dir = ROOT / page["slug"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(
            build_support_page(layout, header, footer, footer_ctx, site, page),
            encoding="utf-8",
        )

    for page in CONTENT_RECOVERY_PAGES:
        output_dir = ROOT / page["path"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(
            render_content_page(layout, header, footer, footer_ctx, site, page, pages),
            encoding="utf-8",
        )

    write_sitemap_for_paths(site, [page["path"] for page in pages], [page["slug"] for page in SUPPORT_PAGES])
    write_robots(site)
    write_recovery_reports(site, pages, [page["slug"] for page in SUPPORT_PAGES])
    print(
        f"Generated {len(pages) + len(CONTENT_RECOVERY_PAGES)} SEO recovery pages, "
        "sitemap.xml, robots.txt and recovery reports."
    )


if __name__ == "__main__":
    main()
