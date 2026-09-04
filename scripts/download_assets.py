#!/usr/bin/env python3
"""Download the Pixieset-hosted media referenced by source-data.json.

The generated assets/data/site-data.json keeps the crawled copy but replaces
remote image URLs with stable, repository-local paths.
"""

from __future__ import annotations

import concurrent.futures
import copy
import json
import mimetypes
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "source-data.json"
ASSET_ROOT = ROOT / "assets"
IMAGE_ROOT = ASSET_ROOT / "images"
DATA_ROOT = ASSET_ROOT / "data"

EXTRA_ASSETS = {
    "logo": "https://images-pw.pixieset.com/profile/544824/c30d35795af924e27a9f7ebe3ac24966c0f54cfe1704fe4e0e5586d73f8c2bf4.png",
}

FONTS = {
    "playfair-display-regular.woff2": "https://assets-pw.pixieset.com/gf/playfairdisplay/n4.woff2",
    "poppins-light.woff2": "https://assets-pw.pixieset.com/gf/poppins/n3.woff2",
    "poppins-regular.woff2": "https://assets-pw.pixieset.com/gf/poppins/n4.woff2",
    "poppins-italic.woff2": "https://assets-pw.pixieset.com/gf/poppins/i4.woff2",
    "poppins-bold.woff2": "https://assets-pw.pixieset.com/gf/poppins/n7.woff2",
}


def route_slug(route: str) -> str:
    return "home" if route == "/" else route.strip("/").replace("/", "-")


def safe_filename(url: str, fallback: str) -> str:
    name = urllib.parse.unquote(Path(urllib.parse.urlparse(url).path).name)
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.")
    if not name:
        name = fallback
    if "." not in name:
        name += mimetypes.guess_extension("image/jpeg") or ".jpg"
    return name


def download(url: str, destination: Path) -> tuple[str, str | None]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return str(destination), None

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://vaneckphotography.mypixieset.com/",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                destination.write_bytes(response.read())
            return str(destination), None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    return str(destination), str(last_error)


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    localized = copy.deepcopy(source)
    jobs: dict[str, Path] = {}

    for route, page in localized.items():
        slug = route_slug(route)
        seen_names: dict[str, str] = {}
        for block_index, block in enumerate(page["blocks"]):
            local_images: list[str] = []
            for image_index, url in enumerate(block["images"]):
                name = safe_filename(url, f"image-{block_index + 1}-{image_index + 1}.jpg")
                previous = seen_names.get(name)
                if previous is not None and previous != url:
                    stem, suffix = Path(name).stem, Path(name).suffix
                    name = f"{stem}-{image_index + 1}{suffix}"
                seen_names[name] = url
                relative = Path("assets") / "images" / slug / name
                jobs[url] = ROOT / relative
                local_images.append(relative.as_posix())
            block["images"] = local_images

    for key, url in EXTRA_ASSETS.items():
        suffix = Path(urllib.parse.urlparse(url).path).suffix or ".png"
        jobs[url] = IMAGE_ROOT / "shared" / f"{key}{suffix.lower()}"

    for name, url in FONTS.items():
        jobs[url] = ASSET_ROOT / "fonts" / name

    failures: list[tuple[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {
            executor.submit(download, url, destination): url
            for url, destination in jobs.items()
        }
        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            _, error = future.result()
            completed += 1
            if error:
                failures.append((url, error))
            if completed % 25 == 0 or completed == len(jobs):
                print(f"Downloaded {completed}/{len(jobs)} assets")

    if failures:
        print("\nFailed downloads:")
        for url, error in failures:
            print(f"- {url}: {error}")
        raise SystemExit(1)

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / "site-data.json").write_text(
        json.dumps(localized, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {DATA_ROOT / 'site-data.json'}")


if __name__ == "__main__":
    main()
