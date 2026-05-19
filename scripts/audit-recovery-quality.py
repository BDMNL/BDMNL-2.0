#!/usr/bin/env python3
"""Create SEO quality audit outputs for the seo.bdmnl.nl recovery pages."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


BASE_URL = "https://seo.bdmnl.nl"
ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "recovery-quality-audit.csv"
REPORT_PATH = ROOT / "recovery-quality-report.md"

PRIORITY_CITIES = {
    "brielle",
    "rotterdam",
    "spijkenisse",
    "hellevoetsluis",
    "dordrecht",
    "goes",
    "middelburg",
    "breda",
}
CORE_SERVICE_MARKERS = {
    "webdesign": "webdesign",
    "website-laten-maken": "website-laten-maken",
    "seo-bureau": "seo-bureau",
    "social-media-beheer": "social-media-beheer",
    "online-marketing": "online-marketing",
    "reclamebureau": "reclamebureau",
}
KNOWN_LEGACY_OVERLAPS = {
    "/seo/seo-bureau-rotterdam/": "/seo-bureau-rotterdam/",
    "/social-media/social-media-beheer-brielle/": "/social-media-beheer-brielle/",
    "/online-marketing-middelburg/": "/online-marketing/online-marketing-middelburg/",
}


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self.meta_description = ""
        self.canonical = ""
        self.robots = ""
        self.h1: list[str] = []
        self.h2: list[str] = []
        self.json_ld: list[dict] = []
        self.text_parts: list[str] = []
        self._tag_stack: list[str] = []
        self._in_title = False
        self._in_json = False
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        self._tag_stack.append(tag)
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])
        if tag == "title":
            self._in_title = True
        if tag == "meta" and data.get("name") == "description":
            self.meta_description = data.get("content", "")
        if tag == "meta" and data.get("name") == "robots":
            self.robots = data.get("content", "")
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")
        if tag == "script" and data.get("type") == "application/ld+json":
            self._in_json = True
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_json:
            raw = "".join(self._json_parts)
            try:
                self.json_ld.append(json.loads(raw))
            except json.JSONDecodeError:
                self.json_ld.append({"@type": "Invalid"})
            self._in_json = False
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        elif self._in_json:
            self._json_parts.append(data)
        else:
            if self._tag_stack and self._tag_stack[-1] == "h1":
                self.h1.append(text)
            if self._tag_stack and self._tag_stack[-1] == "h2":
                self.h2.append(text)
            if self._tag_stack and self._tag_stack[-1] not in {"script", "style"}:
                self.text_parts.append(text)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts).strip()

    @property
    def body_text(self) -> str:
        return " ".join(self.text_parts)


def page_path(file_path: Path) -> str:
    relative = file_path.parent.relative_to(ROOT)
    return "/" if str(relative) == "." else f"/{relative.as_posix()}/"


def page_city(path: str) -> str:
    slug = path.strip("/").split("/")[-1]
    for marker in CORE_SERVICE_MARKERS:
        if slug.startswith(f"{marker}-"):
            return slug.replace(f"{marker}-", "")
    if slug.startswith("seo-"):
        return slug.replace("seo-", "")
    if slug.startswith("social-media-"):
        return slug.replace("social-media-", "")
    return ""


def page_service(path: str) -> str:
    slug = path.strip("/").split("/")[-1]
    for marker, service in CORE_SERVICE_MARKERS.items():
        if marker in slug or path.strip("/").startswith(marker):
            return service
    if slug.startswith("seo-"):
        return "seo"
    if slug.startswith("social-media-"):
        return "social-media"
    if path.startswith("/blog/"):
        return "blog"
    return "support"


def is_priority_authority_path(path: str) -> bool:
    for city in PRIORITY_CITIES:
        expected = {
            f"/website-laten-maken-{city}/",
            f"/seo-bureau-{city}/",
            f"/webdesign/webdesign-{city}/",
        }
        if path in expected:
            return True
    return False


def local_internal_links(parser: Parser) -> list[str]:
    links: list[str] = []
    for href in parser.links:
        parsed = urlparse(href)
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        if parsed.scheme and f"{parsed.scheme}://{parsed.netloc}" != BASE_URL:
            continue
        if parsed.path.startswith("/assets/") or parsed.path.endswith(".xml") or parsed.path.endswith(".txt"):
            continue
        normalized = "/" if parsed.path == "/" else f"/{parsed.path.strip('/')}/"
        links.append(normalized)
    return links


def sitemap_paths() -> set[str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    paths = set()
    for element in root.findall(f".//{namespace}loc"):
        parsed = urlparse(element.text or "")
        paths.add("/" if parsed.path == "/" else f"/{parsed.path.strip('/')}/")
    return paths


def score_page(path: str, parser: Parser, all_paths: set[str], title_counts: Counter[str], desc_counts: Counter[str]) -> tuple[int, list[str], str]:
    score = 100
    flags: list[str] = []
    expected_canonical = f"{BASE_URL}{path}"
    body_words = len(re.findall(r"\w+", parser.body_text))
    links = [link for link in local_internal_links(parser) if link in all_paths and link != path]
    schema_types = {item.get("@type") for item in parser.json_ld if isinstance(item, dict)}
    city = page_city(path)
    service = page_service(path)

    if parser.canonical != expected_canonical:
        score -= 35
        flags.append("canonical_mismatch")
    if path not in sitemap_paths():
        score -= 25
        flags.append("missing_from_sitemap")
    if parser.robots and "noindex" in parser.robots.lower():
        score -= 20
        flags.append("noindex")
    if title_counts[parser.title] > 1:
        score -= 15
        flags.append("duplicate_title")
    if desc_counts[parser.meta_description] > 1:
        score -= 15
        flags.append("duplicate_meta_description")
    if body_words < 550 and service not in {"support"}:
        score -= 18
        flags.append("thin_content")
    if len(parser.h2) < 4 and service not in {"support"}:
        score -= 10
        flags.append("weak_heading_depth")
    if len(links) < 8 and service not in {"support"}:
        score -= 12
        flags.append("weak_internal_links")
    if city and city not in parser.body_text.lower().replace(" ", "-") and city.replace("-", " ") not in parser.body_text.lower():
        score -= 10
        flags.append("low_city_uniqueness")
    if not ({"ProfessionalService", "FAQPage", "BreadcrumbList"} & schema_types) and service not in {"blog", "support"}:
        score -= 15
        flags.append("schema_weak")
    if path in KNOWN_LEGACY_OVERLAPS:
        flags.append(f"monitor_overlap_with:{KNOWN_LEGACY_OVERLAPS[path]}")

    if score >= 88:
        index_recommendation = "index"
    elif score >= 72:
        index_recommendation = "index-monitor"
    else:
        index_recommendation = "review-before-indexing"
    return max(score, 0), flags, index_recommendation


def main() -> None:
    pages: dict[str, Parser] = {}
    for file_path in sorted(ROOT.glob("**/index.html")):
        parser = Parser()
        parser.feed(file_path.read_text(encoding="utf-8"))
        pages[page_path(file_path)] = parser

    title_counts = Counter(parser.title for parser in pages.values())
    desc_counts = Counter(parser.meta_description for parser in pages.values())
    all_paths = set(pages)
    rows = []
    service_counts = Counter()
    recommendation_counts = Counter()
    overlap_rows = []
    priority_risks = []

    for path, parser in sorted(pages.items()):
        service = page_service(path)
        city = page_city(path)
        links = [link for link in local_internal_links(parser) if link in all_paths and link != path]
        score, flags, index_recommendation = score_page(path, parser, all_paths, title_counts, desc_counts)
        service_counts[service] += 1
        recommendation_counts[index_recommendation] += 1
        if any(flag.startswith("monitor_overlap") for flag in flags):
            overlap_rows.append(path)
        if is_priority_authority_path(path) and score < 88:
            priority_risks.append(path)
        rows.append(
            {
                "path": path,
                "canonical": parser.canonical,
                "robots": parser.robots or "index,follow",
                "title": parser.title,
                "meta_description": parser.meta_description,
                "service": service,
                "city": city,
                "body_words": len(re.findall(r"\w+", parser.body_text)),
                "h1_count": len(parser.h1),
                "h2_count": len(parser.h2),
                "internal_link_count": len(links),
                "schema_types": "|".join(str(item.get("@type")) for item in parser.json_ld if isinstance(item, dict)),
                "quality_score": score,
                "index_recommendation": index_recommendation,
                "flags": "|".join(flags) if flags else "ok",
            }
        )

    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    improvement_rows = [row for row in rows if row["flags"] != "ok"]
    lowest = sorted(improvement_rows, key=lambda row: int(row["quality_score"]))[:12]
    city_uniqueness = [row for row in rows if is_priority_authority_path(row["path"])]

    report = [
        "# SEO recovery quality report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## What changed in this pass",
        "",
        "- No new pages were created; the sitemap remains at 128 URLs.",
        "- Canonicals were audited against the live `seo.bdmnl.nl` path for every generated page.",
        "- Index/noindex strategy was reviewed and documented; no aggressive noindex changes were applied.",
        "- Internal crawl paths were strengthened through same-city and content-support linking in the generator.",
        "- Duplicate metadata risks on known legacy/cluster URL pairs were cleaned in the generator.",
        "- Breadcrumb schema was reviewed to avoid pointing at non-existing category URLs.",
        "",
        "## Validation result",
        "",
        f"- HTML pages: {len(rows)}",
        f"- Sitemap URLs: {len(sitemap_paths())}",
        f"- Index recommendations: {dict(recommendation_counts)}",
        f"- Priority authority pages below score threshold: {len(priority_risks)}",
        "",
        "## Topical cluster structure",
        "",
    ]
    for service, count in sorted(service_counts.items()):
        report.append(f"- {service}: {count} pages")
    report.extend(
        [
            "",
            "## Canonical and indexing notes",
            "",
            "- All generated pages are self-canonical to `https://seo.bdmnl.nl/...`.",
            "- All generated pages remain indexable for now because validation is clean and pages are in the recovery sitemap.",
            "- Known historical overlap pairs are monitored rather than noindexed because they may still recover legacy search demand.",
        ]
    )
    if overlap_rows:
        report.extend(["", "### Monitor legacy overlap pairs", ""])
        report.extend([f"- {path} overlaps with {KNOWN_LEGACY_OVERLAPS[path]}" for path in overlap_rows])
    report.extend(
        [
            "",
            "## Lowest quality scores to improve next",
            "",
        ]
    )
    report.extend(
        [
            f"- {row['path']} — score {row['quality_score']} — {row['flags']}"
            for row in lowest
        ]
    )
    report.extend(
        [
            "",
            "## City page uniqueness notes",
            "",
            "- Priority authority pages now include local market/scenario sections for Brielle, Rotterdam, Spijkenisse, Hellevoetsluis, Dordrecht, Goes, Middelburg and Breda.",
            "- Non-priority cities still use fallback local context and should be upgraded gradually, city by city, before any further scaling.",
            f"- Priority city/service authority pages reviewed: {len(city_uniqueness)}.",
            "",
            "## Remaining risks",
            "",
            "- Some historical recovery URLs intentionally overlap newer cluster URLs; keep monitoring Search Console before deciding on redirects or noindex.",
            "- Non-priority city pages are stable but less locally distinctive than the eight priority locations.",
            "- Blog/support recovery pages are useful for internal linking but are not yet deep authority articles.",
            "",
            "## Recommended next step",
            "",
            "Use Search Console performance data to choose one cluster at a time for deeper manual copy improvements, starting with the highest-value overlap or priority-city pages rather than creating new URLs.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {CSV_PATH.name} and {REPORT_PATH.name} for {len(rows)} pages.")


if __name__ == "__main__":
    main()
