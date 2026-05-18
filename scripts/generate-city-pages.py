#!/usr/bin/env python3
"""Generate the scalable BDMNL local SEO website system."""

from __future__ import annotations

import json
import shutil
from datetime import date
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "seo-system.json"
LAYOUT_PATH = ROOT / "templates" / "layout.html"
PAGE_TEMPLATE_PATH = ROOT / "templates" / "pages" / "seo-cluster-page.html"
HEADER_PATH = ROOT / "templates" / "components" / "header.html"
FOOTER_PATH = ROOT / "templates" / "components" / "footer.html"
GENERATED_MARKER = "<!-- generated-by: bdmnl-seo-system -->"


def html(value: Any) -> str:
    return escape(str(value), quote=True)


def json_script(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=6)


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
                f"Ja. We verwerken lokale zoekintentie, interne links, technische SEO en content voor gebieden zoals {areas}.",
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
            f"We vertalen de zoekintentie in {city['name']} naar een paginaflow met duidelijke propositie, trust en CTA's.",
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
            "sameAs": [social["url"] for social in site["socials"]],
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
    empty_schema = json_script({"@context": "https://schema.org", "@type": "WebSite", "name": site["name"], "url": site["base_url"]})
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


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    site = data["site"]
    cities = data["cities"]
    services = data["services"]
    layout = LAYOUT_PATH.read_text(encoding="utf-8")
    page_template = PAGE_TEMPLATE_PATH.read_text(encoding="utf-8")
    header = HEADER_PATH.read_text(encoding="utf-8")
    footer = FOOTER_PATH.read_text(encoding="utf-8")
    footer_ctx = footer_context(site, cities, services)
    slugs: list[str] = []

    remove_legacy_generated_pages(site, services, cities)

    for city in cities:
        for service in services:
            slug = page_slug(service, city)
            slugs.append(slug)
            context = build_page_context(site, city, service, services, cities)
            output_dir = ROOT / page_path(site, slug)
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "index.html").write_text(
                render_full_page(layout, page_template, header, footer, footer_ctx, context),
                encoding="utf-8",
            )

    (ROOT / "index.html").write_text(
        build_homepage(layout, header, footer, footer_ctx, site, cities, services),
        encoding="utf-8",
    )

    for page in SUPPORT_PAGES:
        output_dir = ROOT / page["slug"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(
            build_support_page(layout, header, footer, footer_ctx, site, page),
            encoding="utf-8",
        )

    write_sitemap(site, slugs, [page["slug"] for page in SUPPORT_PAGES])
    write_robots(site)
    print(f"Generated {len(slugs)} SEO cluster pages, sitemap.xml and robots.txt.")


if __name__ == "__main__":
    main()
