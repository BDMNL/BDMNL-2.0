#!/usr/bin/env python3
"""Validate the static seo.bdmnl.nl recovery environment."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


BASE_URL = "https://seo.bdmnl.nl"
ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "recovery-stability-report.md"
UTILITY_PAGES = {
    "/algemene-voorwaarden/",
    "/contact/",
    "/cookiebeleid/",
    "/privacyverklaring/",
}
PRIORITY_CITIES = [
    "brielle",
    "rotterdam",
    "spijkenisse",
    "hellevoetsluis",
    "dordrecht",
    "goes",
    "middelburg",
    "breda",
]
PRIORITY_PATTERNS = [
    "website-laten-maken-{city}/index.html",
    "seo-bureau-{city}/index.html",
    "webdesign/webdesign-{city}/index.html",
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self.meta_descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.og_tags: set[str] = set()
        self.json_ld_blocks: list[str] = []
        self.h1_count = 0
        self.h2_count = 0
        self.form_count = 0
        self._in_title = False
        self._in_json_ld = False
        self._json_ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if "id" in data:
            self.ids.add(data["id"])
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])
        if tag == "link" and data.get("rel") == "canonical":
            self.canonicals.append(data.get("href", ""))
        if tag == "meta" and data.get("name") == "description":
            self.meta_descriptions.append(data.get("content", ""))
        if tag == "meta" and data.get("property", "").startswith("og:"):
            self.og_tags.add(data["property"])
        if tag == "title":
            self._in_title = True
        if tag == "script" and data.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_parts = []
        if tag == "h1":
            self.h1_count += 1
        if tag == "h2":
            self.h2_count += 1
        if tag == "form":
            self.form_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_json_ld:
            self.json_ld_blocks.append("".join(self._json_ld_parts))
            self._in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_json_ld:
            self._json_ld_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join(part.strip() for part in self.title_parts if part.strip()).strip()


def page_path(path: Path) -> str:
    relative = path.parent.relative_to(ROOT)
    return "/" if str(relative) == "." else f"/{relative.as_posix()}/"


def local_file_for_href(href: str) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme and parsed.netloc and f"{parsed.scheme}://{parsed.netloc}" != BASE_URL:
        return None
    path = parsed.path
    if not path:
        return None
    if path.endswith(".xml") or path.endswith(".txt") or path.startswith("/assets/"):
        return ROOT / path.lstrip("/")
    if path == "/":
        return ROOT / "index.html"
    return ROOT / path.strip("/") / "index.html"


def parse_pages() -> dict[str, tuple[Path, PageParser, str]]:
    pages: dict[str, tuple[Path, PageParser, str]] = {}
    for file_path in sorted(ROOT.glob("**/index.html")):
        html = file_path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html)
        pages[page_path(file_path)] = (file_path, parser, html)
    return pages


def sitemap_urls() -> list[str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    return [element.text or "" for element in root.findall(f".//{namespace}loc")]


def validate() -> tuple[list[str], list[str]]:
    pages = parse_pages()
    errors: list[str] = []
    warnings: list[str] = []
    titles: dict[str, list[str]] = defaultdict(list)
    descriptions: dict[str, list[str]] = defaultdict(list)
    linked_pages = {"/"}

    for path, (file_path, parser, html) in pages.items():
        titles[parser.title].append(path)
        description = parser.meta_descriptions[0] if parser.meta_descriptions else ""
        descriptions[description].append(path)

        if "{{" in html or "}}" in html or "<<<<<<<" in html or ">>>>>>>" in html:
            errors.append(f"{path}: unresolved template token or merge marker")
        if parser.h1_count != 1:
            errors.append(f"{path}: expected one h1, found {parser.h1_count}")
        if parser.h2_count < 1 and path not in UTILITY_PAGES:
            errors.append(f"{path}: missing h2 structure")
        if len(parser.meta_descriptions) != 1:
            errors.append(f"{path}: expected one meta description, found {len(parser.meta_descriptions)}")
        elif not 70 <= len(description) <= 180:
            warnings.append(f"{path}: meta description length is {len(description)}")
        if len(parser.canonicals) != 1:
            errors.append(f"{path}: expected one canonical, found {len(parser.canonicals)}")
        elif parser.canonicals[0] != f"{BASE_URL}{path}":
            errors.append(f"{path}: canonical mismatch {parser.canonicals[0]}")
        for og_tag in ["og:title", "og:description", "og:url", "og:image"]:
            if og_tag not in parser.og_tags:
                errors.append(f"{path}: missing {og_tag}")
        for block in parser.json_ld_blocks:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}: invalid JSON-LD ({exc})")
        if parser.form_count:
            errors.append(f"{path}: unwanted form block found")

        for href in parser.links:
            if href.startswith("mailto:") or href.startswith("tel:"):
                continue
            if href.startswith("#"):
                if href[1:] and href[1:] not in parser.ids:
                    errors.append(f"{path}: broken same-page anchor {href}")
                continue
            target = local_file_for_href(href)
            if target is None:
                continue
            if not target.exists():
                errors.append(f"{path}: broken internal link {href}")
                continue
            parsed = urlparse(href)
            if target.name == "index.html":
                normalized = "/" if parsed.path == "/" else f"/{parsed.path.strip('/')}/"
                linked_pages.add(normalized)
                if parsed.fragment:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    if parsed.fragment not in target_parser.ids:
                        errors.append(f"{path}: broken target anchor {href}")

    locs = sitemap_urls()
    expected_locs = {f"{BASE_URL}{path}" for path in pages}
    if len(locs) != 128:
        errors.append(f"sitemap.xml: expected 128 URLs, found {len(locs)}")
    if len(locs) != len(set(locs)):
        errors.append("sitemap.xml: duplicate URLs found")
    if set(locs) != expected_locs:
        errors.append(
            f"sitemap.xml: URL mismatch missing={len(expected_locs - set(locs))} extra={len(set(locs) - expected_locs)}"
        )

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://seo.bdmnl.nl/sitemap.xml" not in robots:
        errors.append("robots.txt: missing seo.bdmnl.nl sitemap reference")

    for title, paths in titles.items():
        if not title:
            errors.append("empty title found")
        elif len(paths) > 1:
            warnings.append(f"duplicate title: {title!r} on {', '.join(paths[:6])}")
    for description, paths in descriptions.items():
        if not description:
            errors.append("empty meta description found")
        elif len(paths) > 1:
            warnings.append(f"duplicate meta description on {', '.join(paths[:6])}")

    orphans = sorted(set(pages) - linked_pages)
    if orphans:
        warnings.append(f"orphan pages without HTML inbound links: {len(orphans)} ({', '.join(orphans[:12])})")

    for city in PRIORITY_CITIES:
        for pattern in PRIORITY_PATTERNS:
            file_path = ROOT / pattern.format(city=city)
            path = page_path(file_path)
            if path not in pages:
                errors.append(f"{path}: missing priority authority page")
                continue
            html = pages[path][2]
            for token in ["local-authority", "authority-facts", "authority-visual-card", "cta-actions"]:
                if token not in html:
                    errors.append(f"{path}: missing authority section {token}")

    return errors, warnings


def write_report(errors: list[str], warnings: list[str]) -> None:
    pages = parse_pages()
    locs = sitemap_urls()
    report = [
        "# SEO recovery stability report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Summary",
        "",
        f"- HTML pages checked: {len(pages)}",
        f"- Sitemap URLs checked: {len(locs)}",
        f"- Priority authority pages checked: {len(PRIORITY_CITIES) * len(PRIORITY_PATTERNS)}",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        "",
        "## Errors",
        "",
    ]
    report.extend([f"- {error}" for error in errors] or ["- None"])
    report.extend(["", "## Warnings", ""])
    report.extend([f"- {warning}" for warning in warnings] or ["- None"])
    report.append("")
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    errors, warnings = validate()
    write_report(errors, warnings)
    print(f"Recovery validation: errors={len(errors)} warnings={len(warnings)}")
    if errors:
        for error in errors[:50]:
            print(f"ERROR {error}")
        raise SystemExit(1)
    for warning in warnings[:20]:
        print(f"WARNING {warning}")


if __name__ == "__main__":
    main()
