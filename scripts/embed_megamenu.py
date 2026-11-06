"""Fetch ElementsKit megamenu AJAX content and embed it statically into mirrored HTML."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mirror_site import (  # noqa: E402
    BASE_PATH,
    LIVE,
    SITE,
    SESSION,
    collect_asset_urls,
    copy_or_download,
    is_our_host,
    local_path_for_url,
    rewrite_html,
)

MEGA_IDS = ["8143"]  # Portfolio megamenu builder post
API = "https://www.diformainstore.com/wp-json/elementskit/v1/megamenu/megamenu_content"


def fetch_mega(mega_id: str) -> str:
    r = SESSION.get(API, params={"id": mega_id}, timeout=90)
    r.raise_for_status()
    # API returns a JSON string
    data = r.json()
    if isinstance(data, str):
        return data
    return str(data)


def rewrite_mega_fragment(html: str) -> str:
    # Wrap as full doc for rewrite helpers then extract body children
    wrapped = f"<html><head></head><body>{html}</body></html>"
    out = rewrite_html(wrapped, LIVE + "/")
    soup = BeautifulSoup(out, "lxml")
    body = soup.body
    return "".join(str(c) for c in body.children) if body else out


def download_mega_assets(html: str) -> None:
    soup = BeautifulSoup(html, "lxml")
    assets = collect_asset_urls(soup, LIVE + "/")
    for asset in sorted(assets):
        host = urlparse(asset).netloc.lower()
        if any(x in host for x in ("google-analytics", "googletagmanager", "facebook", "doubleclick")):
            continue
        dest = local_path_for_url(asset)
        if dest is None:
            continue
        if not is_our_host(asset):
            if not any(asset.lower().endswith(ext) for ext in (".css", ".js", ".woff2", ".woff", ".ttf", ".png", ".jpg", ".jpeg", ".svg", ".webp")):
                continue
        copy_or_download(asset, dest)
        time.sleep(0.02)


def restore_portfolio_trigger(html: str) -> str:
    """Restore href=# and dropdown caret so ElementsKit hover megamenu works."""
    # Current broken/static variants
    patterns = [
        (
            re.compile(
                r'<a class="ekit-menu-nav-link" href="/web-diformainstore/portfolio/"[^>]*>\s*Portfolio(?:<i[^>]*elementskit-submenu-indicator[^>]*></i>)?\s*</a>',
                re.I,
            ),
            '<a class="ekit-menu-nav-link" href="#">Portfolio'
            '<i aria-hidden="true" class="icon icon-down-arrow1 elementskit-submenu-indicator"></i></a>',
        ),
        (
            re.compile(
                r'<a class="ekit-menu-nav-link" href="/web-diformainstore/portfolio/"[^>]*>Portfolio</a>',
                re.I,
            ),
            '<a class="ekit-menu-nav-link" href="#">Portfolio'
            '<i aria-hidden="true" class="icon icon-down-arrow1 elementskit-submenu-indicator"></i></a>',
        ),
    ]
    for pat, repl in patterns:
        html = pat.sub(repl, html)
    return html


def inject_into_file(path: Path, mega_by_id: dict[str, str]) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    text = restore_portfolio_trigger(text)
    for mid, content in mega_by_id.items():
        needle = f'<div class="megamenu-ajax-load" data-id="{mid}"></div>'
        if needle in text:
            text = text.replace(needle, content)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    mega_by_id: dict[str, str] = {}
    for mid in MEGA_IDS:
        print("Fetching megamenu", mid)
        raw = fetch_mega(mid)
        print(" raw chars", len(raw))
        download_mega_assets(raw)
        mega_by_id[mid] = rewrite_mega_fragment(raw)
        print(" rewritten chars", len(mega_by_id[mid]))

    changed = 0
    files = list(SITE.rglob("*.html"))
    for p in files:
        if inject_into_file(p, mega_by_id):
            changed += 1
    print(f"Updated {changed}/{len(files)} HTML files")

    # sanity: homepage contains TYPE / SEE ALL PORTFOLIO
    home = (SITE / "index.html").read_text(encoding="utf-8", errors="replace")
    for marker in ("SEE ALL PORTFOLIO", "elementskit-megamenu-panel", "Floor Displays", 'href="#">Portfolio'):
        print(marker, marker in home or marker.lower() in home.lower())


if __name__ == "__main__":
    main()
