#!/usr/bin/env python3
"""Generate BDMNL city landing pages from the reusable HTML template."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "templates" / "city-landing-template.html"
DATA_PATH = ROOT / "data" / "city-pages.json"


def render_page(template: str, page: dict[str, str]) -> str:
    html = template
    for key, value in page.items():
        html = html.replace("{{" + key + "}}", value)

    remaining_placeholders = sorted(set(part.split("}}", 1)[0] for part in html.split("{{")[1:]))
    if remaining_placeholders:
        missing = ", ".join(remaining_placeholders)
        raise ValueError(f"Missing values for placeholders: {missing}")

    return html


def main() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    pages = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for page in pages:
        slug = page["slug"]
        target_dir = ROOT / slug
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / "index.html"
        target_path.write_text(render_page(template, page), encoding="utf-8")
        print(f"Generated {target_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
