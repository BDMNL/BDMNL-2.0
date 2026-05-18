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
RECOVERY_TEMPLATE_PATH = ROOT / "templates" / "pages" / "recovery-page.html"
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


RECOVERY_CITIES = {
    "brielle": {
        "name": "Brielle",
        "region": "Zuid-Holland",
        "areas": ["Brielle Centrum", "Vierpolders", "Zwartewaal"],
        "intent": "lokale ondernemers op Voorne-Putten die online professioneler zichtbaar willen zijn",
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
}


RECOVERY_SERVICE_PROFILES = {
    "webdesign": {
        "label": "Webdesign",
        "short": "Webflow",
        "service_type": "Webdesign en website development",
        "title": "Webdesign {city} | Webflow websites door BDMNL",
        "description": "Webdesign in {city}? BDMNL bouwt snelle Webflow websites met sterke structuur, SEO-basis en duidelijke conversiepaden voor lokale bedrijven.",
        "h1": "Webdesign {city} met Webflow, snelheid en een duidelijke online basis.",
        "hero": "BDMNL ontwerpt en bouwt websites voor bedrijven in {city} die professioneel willen overkomen en beter vindbaar willen zijn. We combineren Webflow, heldere content, snelheid en praktische conversiepunten.",
        "cta": "Plan een websitegesprek",
        "faq_focus": "website",
    },
    "seo": {
        "label": "SEO",
        "short": "SEO",
        "service_type": "SEO en zoekmachine optimalisatie",
        "title": "{keyword} {city} | SEO en vindbaarheid door BDMNL",
        "description": "{keyword} in {city}? BDMNL helpt met technische SEO, snelle pagina's, lokale content en een duidelijke structuur voor betere vindbaarheid.",
        "h1": "{keyword} {city} voor betere lokale vindbaarheid.",
        "hero": "BDMNL helpt bedrijven in {city} beter gevonden worden met een praktische SEO-aanpak: techniek op orde, sterke pagina's, lokale content en interne links die logisch aanvoelen.",
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
            f'<a href="{recovery_href(first_page("webdesign"))}">Webdesign</a>',
            f'<a href="{recovery_href(first_page("seo"))}">SEO</a>',
            f'<a href="{recovery_href(first_page("social-media"))}">Social media</a>',
            f'<a href="{recovery_href(first_page("online-marketing"))}">Online marketing</a>',
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
                '<a href="/contact/">Contact</a>',
                '<a href="/privacyverklaring/">Privacyverklaring</a>',
                '<a href="/cookiebeleid/">Cookiebeleid</a>',
                '<a href="/algemene-voorwaarden/">Algemene voorwaarden</a>',
            ]
        ),
        "current_year": str(date.today().year),
    }


def recovery_faqs(page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> list[dict[str, str]]:
    city_name = city["name"]
    areas = ", ".join(city["areas"])
    keyword = page["keyword"].lower()
    return [
        {
            "question": f"Helpt BDMNL met {keyword} in {city_name}?",
            "answer": (
                f"Ja. BDMNL helpt bedrijven in {city_name} met {keyword}, waarbij we kijken naar uitstraling, snelheid, "
                "vindbaarheid en de route naar contact of aanvraag."
            ),
        },
        {
            "question": f"Wordt de pagina afgestemd op lokale zoekintentie in {city_name}?",
            "answer": (
                f"Ja. We verwerken lokale context rond {areas} en schrijven de pagina voor bezoekers die gericht zoeken naar "
                f"{keyword} in {city_name}."
            ),
        },
        {
            "question": "Past deze aanpak bij een bestaande BDMNL website?",
            "answer": (
                "Ja. De pagina gebruikt dezelfde BDMNL 2.0 basis met gedeelde header, footer, typografie, CTA's en SEO-structuur."
            ),
        },
        {
            "question": "Kan BDMNL ook helpen met verdere optimalisatie na livegang?",
            "answer": (
                "Ja. Na livegang kunnen we content, techniek, snelheid, SEO en conversiepunten gericht blijven verbeteren."
            ),
        },
    ]


def recovery_service_cards(page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> str:
    cards = [
        ("01", "Strategie", f"We bepalen wat bezoekers in {city['name']} nodig hebben en welke informatie hen helpt kiezen."),
        ("02", "Webflow & techniek", "We bouwen een snelle, rustige pagina met goede headings, nette code en duidelijke CTA's."),
        ("03", "SEO & interne links", "De pagina krijgt lokale content, FAQ's, schema markup en links naar relevante BDMNL pagina's."),
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
    related = [
        candidate
        for candidate in pages
        if candidate["path"] != page["path"]
        and (candidate["city_key"] == page["city_key"] or candidate["service_key"] == page["service_key"])
    ][:6]
    if len(related) < 3:
        related.extend([candidate for candidate in pages if candidate not in related and candidate["path"] != page["path"]][: 3 - len(related)])

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


def recovery_schema(site: dict[str, Any], page: dict[str, Any], city: dict[str, Any], profile: dict[str, str]) -> str:
    return json_script(
        {
            "@context": "https://schema.org",
            "@type": "ProfessionalService",
            "name": f"BDMNL - {page['keyword']} {city['name']}",
            "url": recovery_url(site, page),
            "image": site["og_image"],
            "email": site["email"],
            "telephone": site["phone"],
            "areaServed": {"@type": "City", "name": city["name"]},
            "address": {"@type": "PostalAddress", "streetAddress": "Krammer 8", "postalCode": "3232 HE", "addressLocality": "Brielle", "addressCountry": "NL"},
            "description": profile["description"].format(city=city["name"], keyword=page["keyword"]),
            "serviceType": profile["service_type"],
            "sameAs": [social["url"] for social in site["socials"]],
        }
    )


def recovery_breadcrumb(site: dict[str, Any], page: dict[str, Any], city: dict[str, Any]) -> str:
    return json_script(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site['base_url']}/"},
                {"@type": "ListItem", "position": 2, "name": page["category"].replace("-", " ").title(), "item": f"{site['base_url']}/{page['category']}/"},
                {"@type": "ListItem", "position": 3, "name": f"{page['keyword']} {city['name']}", "item": recovery_url(site, page)},
            ],
        }
    )


def recovery_context(site: dict[str, Any], page: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, str]:
    city = RECOVERY_CITIES[page["city_key"]]
    profile = RECOVERY_SERVICE_PROFILES[page["service_key"]]
    title = profile["title"].format(city=city["name"], keyword=page["keyword"])
    description = profile["description"].format(city=city["name"], keyword=page["keyword"])
    faqs = recovery_faqs(page, city, profile)
    areas = ", ".join(city["areas"])
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
        "h1": profile["h1"].format(city=city["name"], keyword=page["keyword"]),
        "hero_lead": profile["hero"].format(city=city["name"], keyword=page["keyword"]),
        "primary_cta": profile["cta"],
        "city": city["name"],
        "service_label": profile["label"],
        "service_short": profile["short"],
        "path": page["path"],
        "local_focus": f"Lokale content voor {areas}",
        "marquee_items": "\n".join(f"<span>{html(item)}</span>" for item in [profile["label"], city["name"], *city["areas"], "Webflow", "SEO", "Online groei"]),
        "intro_heading": f"{page['keyword']} {city['name']} met een sterke BDMNL basis.",
        "intro_copy_one": (
            f"Deze pagina herstelt een belangrijke historische BDMNL URL voor {page['keyword'].lower()} in {city['name']}. "
            "De inhoud is opnieuw opgebouwd met de BDMNL 2.0 structuur, zodat bezoekers direct begrijpen wat we doen."
        ),
        "intro_copy_two": (
            f"We houden rekening met lokale zoekintentie rond {areas}. Daardoor voelt de pagina relevant voor bedrijven in de regio, "
            "zonder generieke template-teksten."
        ),
        "intro_copy_three": (
            "De pagina gebruikt dezelfde header, footer, CTA's, FAQ-structuur en SEO-opbouw als de rest van het recovery systeem."
        ),
        "services_heading": f"Hoe BDMNL helpt met {page['keyword'].lower()} in {city['name']}.",
        "services_intro": "We combineren strategie, Webflow, SEO en duidelijke content tot een pagina die snel laadt en logisch leest.",
        "service_cards": recovery_service_cards(page, city, profile),
        "related_cards": recovery_related_cards(page, pages),
        "testimonial_cards": recovery_testimonial_cards(),
        "cta_heading": f"Klaar om {page['keyword'].lower()} in {city['name']} goed neer te zetten?",
        "cta_copy": "Neem contact op met BDMNL voor een praktische aanpak rond website, SEO, content en online groei.",
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
    page_content = render(
        page_template,
        context,
        raw_keys={"service_cards", "related_cards", "testimonial_cards", "faq_items", "marquee_items"},
    )
    header_html = render(header, {"asset_prefix": context["asset_prefix"]})
    footer_html = render(
        footer,
        {**footer_ctx, "asset_prefix": context["asset_prefix"]},
        raw_keys={"footer_city_links", "footer_service_links", "footer_internal_links"},
    )
    return GENERATED_MARKER + "\n" + render(
        layout,
        {**context, "global_header": header_html, "global_footer": footer_html, "page_content": page_content.strip()},
        raw_keys={"global_header", "global_footer", "page_content", "professional_service_schema", "faq_schema", "breadcrumb_schema"},
    )


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
                    f"<p>Historische BDMNL URL hersteld met nieuwe BDMNL 2.0 structuur, lokale content en technische SEO.</p>",
                    f'<div class="mini-link-row"><a href="{recovery_href(page)}">Bekijk pagina</a></div>',
                    "</article>",
                ]
            )
        )

    page_content = f"""
<section class="hero section-pad">
  <div class="container">
    <p class="eyebrow"><span></span>BDMNL SEO recovery</p>
    <h1>Historische BDMNL URL's hersteld met een sterke premium basis.</h1>
    <p class="hero-lead">Deze omgeving herstelt belangrijke bestaande SEO pagina's voor webdesign, SEO, social media, online marketing en reclamebureau zoekopdrachten. Iedere pagina gebruikt dezelfde BDMNL header, footer, typografie, CTA's en schema-structuur.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{recovery_href(pages[0])}" data-magnetic>Bekijk recovery pagina</a>
      <a class="btn btn-secondary" href="/contact/" data-magnetic>Neem contact op</a>
    </div>
  </div>
</section>
<section class="section related-pages" id="diensten">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Herstelde pagina's</p>
      <h2>Belangrijke SEO URL's terug in één BDMNL systeem.</h2>
      <p>De sitemap bevat alle herstelde historische URLs. Hieronder staan enkele belangrijke ingangen.</p>
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
      <h2>Eerst SEO stabiliteit, daarna verder uitbouwen.</h2>
      <p>De prioriteit ligt nu op historische URL waarde herstellen met nette content, schema, interne links en gedeelde BDMNL componenten.</p>
    </div>
  </div>
</section>
<section class="section knowledge-section" id="kennisbank">
  <div class="container">
    <div class="section-heading centered reveal">
      <p class="eyebrow"><span></span>Kennisbank</p>
      <h2>Webflow, snelheid, SEO en conversie als vaste basis.</h2>
      <p>Nieuwe kennisbank- en AutoSEO-workflows kunnen later bovenop deze stabiele recovery-structuur worden gebouwd.</p>
    </div>
  </div>
</section>
<section class="section cta-band">
  <div class="container">
    <div class="cta-panel reveal" id="contact">
      <div>
        <p class="eyebrow light"><span></span>Contact</p>
        <h2>Wil je weten welke SEO pagina's eerst hersteld moeten worden?</h2>
        <p>BDMNL helpt met prioriteit, structuur, content en technische SEO voor bestaande en nieuwe pagina's.</p>
      </div>
      <form class="cta-form" action="/contact/" method="get">
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
    schema = json_script({"@context": "https://schema.org", "@type": "WebSite", "name": site["name"], "url": site["base_url"]})
    context = {
        "asset_prefix": "./",
        "canonical_url": f"{site['base_url']}/",
        "og_title": "BDMNL SEO recovery systeem",
        "og_description": "Historische BDMNL SEO URL's hersteld met gedeelde BDMNL 2.0 componenten.",
        "twitter_title": "BDMNL SEO recovery systeem",
        "twitter_description": "Historische BDMNL SEO URL's hersteld met gedeelde BDMNL 2.0 componenten.",
        "og_image": site["og_image"],
        "meta_title": "BDMNL SEO recovery systeem | Historische URL's herstellen",
        "meta_description": "BDMNL herstelt historische SEO pagina's met een premium BDMNL 2.0 structuur, gedeelde componenten, schema en interne links.",
        "professional_service_schema": schema,
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
        (output_dir / "index.html").write_text(
            render_recovery_page(layout, page_template, header, footer, footer_ctx, context),
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

    write_sitemap_for_paths(site, [page["path"] for page in pages], [page["slug"] for page in SUPPORT_PAGES])
    write_robots(site)
    print(f"Generated {len(pages)} SEO recovery pages, sitemap.xml and robots.txt.")


if __name__ == "__main__":
    main()
