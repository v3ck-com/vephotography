#!/usr/bin/env python3
"""Check generated pages, internal references, local media, and contact actions."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROUTES = [
    "/",
    "/about/",
    "/price-list/",
    "/portfolio/",
    "/wedding/",
    "/engagement/",
    "/fashion/",
    "/casual/",
    "/families-copy/",
    "/contact/",
]


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []
        self.form_count = 0
        self.whatsapp_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "form":
            self.form_count += 1
        for attribute in ("src", "href"):
            value = values.get(attribute)
            if value:
                self.references.append((attribute, value))
        if tag == "a" and (values.get("href") or "").startswith("https://wa.me/"):
            self.whatsapp_links.append(values["href"] or "")


def page_path(route: str) -> Path:
    return ROOT / ("index.html" if route == "/" else route.strip("/") + "/index.html")


def check_reference(page: Path, attribute: str, value: str) -> str | None:
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https", "mailto", "tel"} or value.startswith("#"):
        return None
    target = (page.parent / parsed.path).resolve()
    if parsed.path.endswith("/"):
        target = target / "index.html"
    if target.is_dir():
        target = target / "index.html"
    if not target.exists():
        return f"{page.relative_to(ROOT)}: missing {attribute} target {value}"
    return None


def main() -> None:
    errors: list[str] = []
    for route in EXPECTED_ROUTES:
        page = page_path(route)
        if not page.exists():
            errors.append(f"Missing page for {route}")
            continue
        parser = ReferenceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        if parser.form_count:
            errors.append(f"{route}: contains {parser.form_count} form element(s)")
        for attribute, value in parser.references:
            problem = check_reference(page, attribute, value)
            if problem:
                errors.append(problem)
        if route in {"/", "/about/", "/price-list/", "/contact/"}:
            if not any(link.startswith("https://wa.me/27698007288") for link in parser.whatsapp_links):
                errors.append(f"{route}: missing WhatsApp contact link")

    data = json.loads((ROOT / "assets/data/site-data.json").read_text(encoding="utf-8"))
    image_paths = [
        image
        for page in data.values()
        for block in page["blocks"]
        for image in block["images"]
    ]
    if len(image_paths) != 291:
        errors.append(f"Expected 291 page images, found {len(image_paths)}")
    for image in image_paths:
        if image.startswith(("http://", "https://")):
            errors.append(f"Remote image remains in generated data: {image}")
        elif not (ROOT / image).exists():
            errors.append(f"Missing data image: {image}")

    oversized = [path for path in ROOT.rglob("*") if path.is_file() and path.stat().st_size >= 100_000_000]
    for path in oversized:
        errors.append(f"File exceeds GitHub's 100 MB limit: {path.relative_to(ROOT)}")

    if errors:
        print("Verification failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"Verified {len(EXPECTED_ROUTES)} pages, {len(image_paths)} page images, local links, and WhatsApp actions")


if __name__ == "__main__":
    main()
